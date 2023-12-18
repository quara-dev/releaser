from __future__ import annotations

from pathlib import Path

from releaser.hexagon.ports import VersionReader

from .json_file import JsonFileVersionReader
from .pyproject import PyprojectVersionReader


class AutoVersionReader(VersionReader):
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def read_version(self, version_file: str | None) -> str | None:
        if version_file:
            version_path = Path(version_file).expanduser()
            if version_path.is_file():
                return self._read_version_file(version_path)
            return self._read_version_file(self.project_root.joinpath(version_file))
        if self.project_root.joinpath("pyproject.toml").is_file():
            return PyprojectVersionReader().read_version(
                self.project_root.joinpath("pyproject.toml").as_posix()
            )
        if self.project_root.joinpath("package.json").is_file():
            return JsonFileVersionReader().read_version(
                self.project_root.joinpath("package.json").as_posix()
            )
        return None

    def _read_version_file(self, version_file: Path) -> str | None:
        if version_file.suffix == ".json":
            return JsonFileVersionReader().read_version(version_file.as_posix())
        if version_file.name == "pyproject.toml":
            return PyprojectVersionReader().read_version(version_file.as_posix())

        return None
