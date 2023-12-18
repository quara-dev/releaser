from __future__ import annotations

from releaser.hexagon.entities.artefact import Manifest
from releaser.hexagon.entities.strategy import ReleaseStrategy
from releaser.hexagon.ports import (
    GitReader,
    JsonWriter,
    StrategyReader,
    VersionReader,
    WebhookClient,
)


class GitReaderStub(GitReader):
    def __init__(self) -> None:
        self._sha: str | None = None
        self._history: list[str] | None = None
        self._is_dirty: bool | None = None

    def is_dirty(self) -> bool:
        if self._is_dirty is None:
            raise RuntimeError("is_dirty not set in stub git reader")
        return self._is_dirty

    def read_most_recent_commit_sha(self) -> str:
        if self._sha is None:
            raise RuntimeError("sha not set in stub git reader")
        return self._sha

    def read_commit_message_history(self, depth: int) -> list[str]:
        if self._history is None:
            raise RuntimeError("history not set in stub git reader")
        return list(self._history)

    def set_sha(self, sha: str) -> None:
        self._sha = sha

    def set_history(self, history: list[str]) -> None:
        self._history = history

    def set_is_dirty(self, is_dirty: bool) -> None:
        self._is_dirty = is_dirty


class JsonWriterStub(JsonWriter):
    def __init__(self) -> None:
        self.manifest: Manifest | None = None

    def write_manifest(self, manifest: Manifest) -> None:
        if self.manifest:
            raise RuntimeError("manifest already set in stub json writer")
        self.manifest = manifest

    def read_manifest(self) -> Manifest | None:
        return self.manifest


class StrategyReaderStub(StrategyReader):
    def __init__(self) -> None:
        self.strategy: ReleaseStrategy | None = None

    def detect(self) -> ReleaseStrategy | None:
        return self.strategy

    def set_strategy(self, strategy: ReleaseStrategy) -> None:
        self.strategy = strategy


class VersionReaderStub(VersionReader):
    def __init__(self) -> None:
        self.version: str | None = None

    def read_version(self) -> str | None:
        return self.version

    def set_version(self, version: str) -> None:
        self.version = version


class WebhookClientStub(WebhookClient):
    def __init__(self) -> None:
        self._payload: Manifest | None = None
        self._url: str | None = None

    def post_json(self, webhook_url: str, payload: Manifest) -> None:
        if self._payload:
            raise RuntimeError("payload already set in stub webhook client")
        if self._url:
            raise RuntimeError("url already set in stub webhook client")
        self._url = webhook_url
        self._payload = payload

    def get_payload(self) -> Manifest | None:
        return self._payload

    def get_url(self) -> str | None:
        return self._url
