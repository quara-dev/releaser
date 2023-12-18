from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from releaser.hexagon.entities import artefact
from releaser.hexagon.ports import JsonWriter


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
