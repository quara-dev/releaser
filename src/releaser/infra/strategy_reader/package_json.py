from __future__ import annotations

import json
from pathlib import Path

from releaser.hexagon.entities import strategy
from releaser.hexagon.ports import StrategyReader


class PackageJsonStrategyReader(StrategyReader):
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

    def detect(self) -> strategy.ReleaseStrategy | None:
        if not self.filepath.is_file():
            return None
        package = json.loads(self.filepath.read_text())
        config = package.get("quara", {}).get("releaser", None)
        if not config:
            return None
        return strategy.ReleaseStrategy.parse_dict(config)
