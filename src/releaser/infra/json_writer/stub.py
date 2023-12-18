from __future__ import annotations

from releaser.hexagon.entities import artefact
from releaser.hexagon.ports import JsonWriter


class JsonWriterStub(JsonWriter):
    """A stub JSON writer that can be used for testing.

    A stub cannot be used twice in the same test without calling
    reset() in between.
    """

    def __init__(self) -> None:
        self.manifest: artefact.Manifest | None = None

    def write_manifest(self, manifest: artefact.Manifest) -> None:
        if self.manifest:
            raise RuntimeError("manifest already set in stub json writer")
        self.manifest = manifest

    def read_manifest(self) -> artefact.Manifest | None:
        return self.manifest

    def reset(self) -> None:
        """Test helper: reset the stub."""
        self.manifest = None
