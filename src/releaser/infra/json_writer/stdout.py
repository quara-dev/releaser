from __future__ import annotations

import json
from dataclasses import asdict

from releaser.hexagon.entities import artefact
from releaser.hexagon.ports import JsonWriter


class JsonStdoutWriter(JsonWriter):

    """A JSON writer that writes to the standard output."""

    def write_manifest(self, manifest: artefact.Manifest) -> None:
        """Write the given manifest to the standard output as JSON."""

        print(json.dumps(asdict(manifest), separators=(",", ":")))

    def read_manifest(self) -> artefact.Manifest | None:
        """Always raises NotImplementedError as reading from stdout is not supported."""

        raise NotImplementedError("JsonStdoutWriter does not support reading")
