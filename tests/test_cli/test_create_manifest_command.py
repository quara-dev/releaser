from __future__ import annotations

import json
import shlex
from pathlib import Path

import pytest
import toml

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

    def read_manifest(self) -> artefact.Manifest:
        """Get the generated manifest."""
        generated = self.deps.manifest_writer.read_manifest()
        if generated is None:
            raise ValueError("Manifest is not generated")
        return generated

    def assert_manifest(self, expected: dict[str, object]) -> None:
        """Assert the generated manifest."""
        generated = self.read_manifest()
        assert generated == generated.parse_dict(expected)

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
        if sha is not None:
            self.deps.git_reader.set_sha(sha)
        self.deps.git_reader.set_branch(branch)
        self.deps.git_reader.set_is_dirty(dirty)

    def run_command(self, command: str) -> None:
        """A helper to run a command during test."""
        self.app.execute(shlex.split(command))

    @staticmethod
    def read_test_file(*path: str) -> str:
        """read file regarding path"""
        absolute_path = Path(__file__).parent.joinpath(*path)
        return absolute_path.read_text()

    @classmethod
    def read_package_json(cls, file_name: str) -> dict[str, object]:
        """read packages json for regression test"""
        content = json.loads(cls.read_test_file("regression_test_data", file_name))
        return content["quara"]["releaser"]

    @classmethod
    def read_pyproject_toml(cls, file_name: str) -> dict[str, object]:
        """a helper that  read and return a toml object from  file"""
        content = toml.loads(cls.read_test_file("regression_test_data", file_name))
        return content["tool"]["quara"]["releaser"]

    @classmethod
    def read_releaser_config(cls, file_name: str) -> dict[str, object]:
        extension = file_name.split(".")[-1]
        if extension == "toml":
            return cls.read_pyproject_toml(file_name)
        elif extension == "json":
            return cls.read_package_json(file_name)
        raise TypeError(f"Unknown file extension: {extension}")


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
        "strategy_file_name, branch, output_file_name",
        [
            (
                "quara-frontend.package.json",
                "next",
                "manifest_quara-frontend-branch_next.json",
            ),
            (
                "quara-app.package.json",
                "next",
                "manifest_quara-app-branch_next.json",
            ),
            (
                "quara-python.pyproject.toml",
                "next",
                "manifest_quara-python-branch_next.json",
            ),
        ],
    )
    def test_json_manifest(
        self,
        strategy_file_name: str,
        branch: str,
        output_file_name: str,
    ):
        expected_output = self.read_test_file(
            "regression_test_data", "output", output_file_name
        )
        # Arrange
        self.set_strategy(self.read_releaser_config(strategy_file_name))
        self.set_git_state(
            branch=branch,
            history=["this is the latest commit message"],
            sha="shatest",
        )
        # Act
        self.run_command(
            "create-manifest",
        )
        # Assert
        self.assert_manifest(json.loads(expected_output))
