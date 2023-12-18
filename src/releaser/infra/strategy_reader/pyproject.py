from __future__ import annotations

from pathlib import Path

from releaser.hexagon.entities import strategy
from releaser.hexagon.ports import StrategyReader

from .._pyproject.loader import PyprojectLoader


class PyprojectStrategyReader(StrategyReader, PyprojectLoader):
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

    def detect(self) -> strategy.ReleaseStrategy | None:
        if not self.filepath.exists():
            return None
        content = self.load_pyproject(self.filepath)
        config = content.get("tool", {}).get("quara", {}).get("releaser", None)
        if not config:
            return None
        return strategy.ReleaseStrategy.parse_dict(config)
