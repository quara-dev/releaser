from __future__ import annotations

import shlex

import pytest

from releaser.cli import testing
from releaser.cli.app import Application
from releaser.hexagon.entities import artefact, strategy

from ..stubs import (
    GitReaderStub,
    JsonWriterStub,
    StrategyReaderStub,
    VersionReaderStub,
    WebhookClientStub,
)


class CreateManifestCommandSetup:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        git_reader: GitReaderStub,
        json_writer: JsonWriterStub,
        strategy_reader: StrategyReaderStub,
        version_reader: VersionReaderStub,
        webhook_client: WebhookClientStub,
    ):
        self.git_reader = git_reader
        self.manifest_writer = json_writer
        self.strategy_reader = strategy_reader
        self.version_reader = version_reader
        self.webhook_client = webhook_client
        self.app = Application(
            testing_dependencies=testing.Dependencies(
                git_reader=self.git_reader,
                manifest_writer=self.manifest_writer,
                strategy_reader=self.strategy_reader,
                version_reader=self.version_reader,
                webhook_client=self.webhook_client,
            )
        )

    def assert_manifest(self, expected: dict[str, object]) -> None:
        """An assertion helper to check the manifest contents."""
        assert self.manifest_writer.read_manifest() == artefact.Manifest.parse_dict(
            expected
        )

    def set_strategy(self, values: dict[str, object]) -> None:
        """A helper to set the release strategy during test."""
        valid_strategy = strategy.ReleaseStrategy.parse_dict(values)
        self.strategy_reader.set_strategy(valid_strategy)

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
