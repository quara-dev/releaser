import http
import json
import os
import subprocess
import sys
from dataclasses import asdict
from http.client import HTTPConnection, HTTPSConnection
from importlib import import_module
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from releaser.hexagon.entities import artefact, strategy
from releaser.hexagon.entities.artefact.manifest import Manifest
from releaser.hexagon.ports import (
    GitReader,
    JsonWriter,
    StrategyReader,
    VersionReader,
    WebhookClient,
)


class GitSubprocessReader(GitReader):
    """A git reader that uses subprocesses to read git information."""

    def is_dirty(self) -> bool:
        process = subprocess.run(["git", "diff-index", "--quiet", "HEAD", "--"])
        return process.returncode != 0

    def read_most_recent_commit_sha(self) -> str:
        long_sha = (
            subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        )
        return long_sha

    def read_commit_message_history(self, depth: int) -> list[str]:
        history = (
            subprocess.check_output(["git", "log", f"-{depth}", "--pretty=%s"])
            .decode()
            .strip()
            .splitlines()
        )
        return [line.strip() for line in history]


class JsonFileWriter(JsonWriter):
    """A JSON writer that writes to a file."""

    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

    def write_manifest(self, manifest: artefact.Manifest) -> None:
        if self.filepath.exists():
            raise FileExistsError(
                f"output filepath already exists: {self.filepath.as_posix()}"
            )
        self.filepath.write_text(
            json.dumps(
                asdict(manifest),
                separators=(",", ":"),
            )
        )

    def read_manifest(self) -> artefact.Manifest | None:
        if not self.filepath.exists():
            return None
        content = self.filepath.read_text()
        return artefact.Manifest(**json.loads(content))


class JsonStdoutWriter(JsonWriter):
    """A JSON writer that writes to the standard output."""

    def write_manifest(self, manifest: artefact.Manifest) -> None:
        print(json.dumps(asdict(manifest), separators=(",", ":")))

    def read_manifest(self) -> artefact.Manifest | None:
        return None


class InMemoryJsonWriter(JsonWriter):
    """A JSON writer that writes to memory."""

    def __init__(self) -> None:
        self.manifest: artefact.Manifest | None = None

    def write_manifest(self, manifest: artefact.Manifest) -> None:
        self.manifest = manifest

    def read_manifest(self) -> artefact.Manifest | None:
        return self.manifest


class HttpsWebhookClient(WebhookClient):
    def post_json(self, webhook_url: str, manifest: Manifest) -> None:
        parsed_url = urlparse(webhook_url)
        host = parsed_url.hostname
        if not host:
            raise ValueError(f"Invalid webhook URL: {webhook_url}")
        if parsed_url.query:
            path_with_params = f"{parsed_url.path}?{parsed_url.query}"
        else:
            path_with_params = parsed_url.path
        data = json.dumps(asdict(manifest), separators=(",", ":"))
        if parsed_url.scheme == "http":
            connection = HTTPConnection(host=host, port=parsed_url.port)
        else:
            connection = HTTPSConnection(host=host, port=parsed_url.port)
        connection.request(
            method="POST",
            url=path_with_params,
            body=data,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(data)),
            },
        )
        response = connection.getresponse()
        if response.status != http.HTTPStatus.OK:
            print(response.read().decode(), file=sys.stderr)
            raise RuntimeError(
                f"Failed to send webhook to {webhook_url}: {response.status} {response.reason}"
            )


class MagicStrategyReader(StrategyReader):
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def detect(self) -> strategy.ReleaseStrategy | None:
        if self.project_root.joinpath("pyproject.toml").is_file():
            return _PyprojectStrategyReader(
                self.project_root.joinpath("pyproject.toml")
            ).detect()
        if self.project_root.joinpath("package.json").is_file():
            return _PackageJsonStrategyReader(
                self.project_root.joinpath("package.json")
            ).detect()
        return None


class MagicVersionReader(VersionReader):
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def read_version(self) -> str | None:
        if version_file := os.environ.get("VERSION_FILE"):
            return _JsonFileVersionReader(
                self.project_root.joinpath(version_file)
            ).read_version()
        if self.project_root.joinpath("pyproject.toml").is_file():
            return _PyprojectVersionReader(
                self.project_root.joinpath("pyproject.toml")
            ).read_version()
        if self.project_root.joinpath("package.json").is_file():
            return _JsonFileVersionReader(
                self.project_root.joinpath("package.json")
            ).read_version()
        return None


class _PyprojectReader:
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

    def load_pyproject(self) -> dict[str, Any]:
        try:
            import toml  # pyright: ignore[reportMissingModuleSource]
        except ImportError:
            print(
                "ERROR: toml is not installed. Please install it with `pip install toml` in order to read pyproject.toml files.",
                file=sys.stderr,
            )
            sys.exit(1)

        return toml.loads(self.filepath.read_text())


class _PyprojectStrategyReader(StrategyReader, _PyprojectReader):
    def detect(self) -> strategy.ReleaseStrategy | None:
        if not self.filepath.exists():
            return None
        content = self.load_pyproject()
        config = content.get("tool", {}).get("quara", {}).get("releaser", None)
        if not config:
            return None
        return strategy.ReleaseStrategy.parse_dict(config)


class _PackageJsonStrategyReader(StrategyReader):
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath
        if not self.filepath.is_file():
            print(f"Strategy file not found: {self.filepath}", file=sys.stderr)
            sys.exit(1)

    def detect(self) -> strategy.ReleaseStrategy | None:
        package = json.loads(self.filepath.read_text())
        config = package.get("quara", {}).get("releaser", None)
        if not config:
            return None
        return strategy.ReleaseStrategy.parse_dict(config)


class _PyprojectVersionReader(VersionReader, _PyprojectReader):
    def read_version(self) -> str | None:
        if not self.filepath.exists():
            return None
        content = self.load_pyproject()
        # Poetry version
        if "poetry" in content["tool"]:
            return content["tool"]["poetry"]["version"]
        # Setuptools dynamic version
        if (
            version := content.get("tool", {})
            .get("setuptools", {})
            .get("dynamic", {})
            .get("version", {})
            .get("attr", None)
        ):
            mod, attr = str(version).rsplit(".", maxsplit=1)
            return getattr(import_module(mod), attr)
        return None


class _JsonFileVersionReader(VersionReader):
    def __init__(self, filepath: Path):
        self.filepath = filepath
        if not self.filepath.is_file():
            print(f"Version file not found: {self.filepath}", file=sys.stderr)
            sys.exit(1)

    def read_version(self) -> str:
        return json.loads(self.filepath.read_text())["version"]
