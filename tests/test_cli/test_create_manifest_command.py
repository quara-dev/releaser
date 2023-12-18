from __future__ import annotations

import shlex

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

    def run_command(self, command: str) -> None:
        """A helper to run a command during test."""
        self.app.execute(shlex.split(command))


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
