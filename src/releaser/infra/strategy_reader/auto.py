from __future__ import annotations

from pathlib import Path

from releaser.hexagon.entities import strategy
from releaser.hexagon.ports import StrategyReader

from .package_json import PackageJsonStrategyReader
from .pyproject import PyprojectStrategyReader


class AutoStrategyReader(StrategyReader):
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def read(self) -> strategy.ReleaseStrategy | None:
        if self.project_root.joinpath("pyproject.toml").is_file():
            return PyprojectStrategyReader(
                self.project_root.joinpath("pyproject.toml")
            ).read()
        if self.project_root.joinpath("package.json").is_file():
            return PackageJsonStrategyReader(
                self.project_root.joinpath("package.json")
            ).read()
        return None
