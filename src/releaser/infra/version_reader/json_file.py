from __future__ import annotations

import json
from pathlib import Path

from releaser.hexagon.ports import VersionReader


class JsonFileVersionReader(VersionReader):
    def read(self, version_file: str | None) -> str | None:
        if not version_file:
            return None
        version_filepath = Path(version_file).expanduser()
        if not version_filepath.is_file():
            return None
        return json.loads(version_filepath.read_text())["version"]
