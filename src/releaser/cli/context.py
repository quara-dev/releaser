from __future__ import annotations

from dataclasses import dataclass

from releaser.hexagon.ports import (
    GitReader,
    JsonWriter,
    StrategyReader,
    VersionReader,
    WebhookClient,
)

from . import testing


@dataclass
class GlobalOpts:
    """Global options available for all commands."""

    debug: bool
    """Debug mode."""

    _testing_dependencies: testing.Dependencies | None = None
    """Testing dependencies. Only used in tests."""

    def get_reader(self, default: GitReader) -> GitReader:
        """Get the reader."""
        return (
            self._testing_dependencies.git_reader
            if self._testing_dependencies
            else default
        )

    def get_writer(self, default: JsonWriter) -> JsonWriter:
        """Get the writer."""
        return (
            self._testing_dependencies.manifest_writer
            if self._testing_dependencies
            else default
        )

    def get_strategy_reader(self, default: StrategyReader) -> StrategyReader:
        """Get the strategy reader."""
        return (
            self._testing_dependencies.strategy_reader
            if self._testing_dependencies
            else default
        )

    def get_version_reader(self, default: VersionReader) -> VersionReader:
        """Get the version reader."""
        return (
            self._testing_dependencies.version_reader
            if self._testing_dependencies
            else default
        )

    def get_webhook_client(self, default: WebhookClient) -> WebhookClient:
        """Get the webhook client."""
        return (
            self._testing_dependencies.webhook_client
            if self._testing_dependencies
            else default
        )
