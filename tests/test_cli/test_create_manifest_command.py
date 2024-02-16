from __future__ import annotations

import json
import shlex
from pathlib import Path
import toml
import pytest

from releaser.cli.app import Application
from releaser.hexagon.entities import artefact, strategy

from ..stubs import DependenciesForTests


class CreateManifestCommandSetup:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        testing_dependencies: DependenciesForTests,
    ):
        self.deps = testing_dependencies
        self.app = Application(
            testing_dependencies=self.deps,
        )

    def assert_manifest(self, expected: dict[str, object]) -> None:
        """An assertion helper to check the manifest contents."""
        assert (
            self.deps.manifest_writer.read_manifest()
            == artefact.Manifest.parse_dict(expected)
        )

    def set_strategy(self, values: dict[str, object]) -> None:
        """A helper to set the release strategy during test."""
        valid_strategy = strategy.ReleaseStrategy.parse_dict(values)
        self.deps.strategy_reader.set_strategy(valid_strategy)

    def set_git_state(
        self,
        branch: str,
        history: list[str],
        sha: str | None = None,
        dirty: bool = False,
    ):
        """a helper to set git state"""
        self.deps.git_reader.set_history(history)
        self.deps.git_reader.set_sha(sha)
        self.deps.git_reader.set_branch(branch)
        self.deps.git_reader.set_is_dirty(dirty)

    def run_command(self, command: str) -> None:
        """A helper to run a command during test."""
        self.app.execute(shlex.split(command))

    def read_pyproject_toml(self, file_name: str) -> dict[str, object]:
        """a helper that  read and return a toml object from  file"""
        return toml.loads(self.read_file("regression_test_data", file_name))["tool"][
            "quara"
        ]["releaser"]

    @classmethod
    def read_file(cls, *path: str) -> str:
        """read file regarding path"""
        path = Path(__file__).parent.joinpath(*path)
        return path.read_text()

    def read_releaser_config(self, file_name: str, type: str) -> dict[str, object]:
        if type == "toml":
            return self.read_pyproject_toml(f"{file_name}.{type}")
        elif type == "json":
            return self.read_package_json(f"{file_name}.{type}")

    def read_package_json(self, file_name: str) -> dict[str, object]:
        """read packages json for regression test"""
        return json.loads(self.read_file("regression_test_data", file_name))["quara"][
            "releaser"
        ]


class TestCreateManifestCommand(CreateManifestCommandSetup):

    def test_it_should_create_an_empty_manifest(self):
        self.set_strategy(
            {"applications": {}},
        )
        self.run_command(
            "create-manifest",
        )
        self.assert_manifest(
            {
                "applications": {},
            }
        )

    @pytest.mark.parametrize(
        "strategy_file_name, strategy_file_extension,  branches, output_file_name",
        [
            (
                "quara-frontend.package",
                "json",
                ["next"],
                "manifest_quara-frontend-branch_next.json",
            ),
            (
                "quara-app.package",
                "json",
                ["next"],
                "manifest_quara-app-branch_next.json",
            ),
            (
                "quara-python.pyproject",
                "toml",
                ["next"],
                "manifest_quara-python-branch_next.json",
            ),
        ],
    )
    def test_json_manifest(
        self,
        strategy_file_name: str,
        strategy_file_extension: str,
        branches: list[str],
        output_file_name: str,
    ):
        self.set_strategy(
            self.read_releaser_config(strategy_file_name, strategy_file_extension)
        )
        self.set_git_state(
            branch="next", history=["this is the latest commit message"], sha="shatest"
        )
        self.run_command(
            "create-manifest",
        )
        manifest = json.loads(
            self.read_file("regression_test_data", "output", output_file_name)
        )
        self.assert_manifest({"applications": manifest})
