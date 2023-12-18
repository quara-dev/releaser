from __future__ import annotations

from importlib import import_module
from pathlib import Path

from releaser.hexagon.ports import VersionReader

from .._pyproject.loader import PyprojectLoader


class PyprojectVersionReader(VersionReader, PyprojectLoader):
    def read_version(self, version_file: str | None) -> str | None:
        if not version_file:
            return None
        version_filepath = Path(version_file).expanduser()
        if not version_filepath.exists():
            return None
        content = self.load_pyproject(version_filepath)
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
