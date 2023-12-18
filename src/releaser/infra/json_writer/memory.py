from __future__ import annotations

from releaser.hexagon.entities import artefact
from releaser.hexagon.ports import JsonWriter


class InMemoryJsonWriter(JsonWriter):
    """A JSON writer that writes to memory."""

    def __init__(self) -> None:
        self.manifest: artefact.Manifest | None = None

    def write_manifest(self, manifest: artefact.Manifest) -> None:
        self.manifest = manifest

    def read_manifest(self) -> artefact.Manifest | None:
        return self.manifest
