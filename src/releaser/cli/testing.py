from __future__ import annotations

from dataclasses import dataclass

from releaser.hexagon.ports import (
    GitReader,
    JsonWriter,
    StrategyReader,
    VersionReader,
    WebhookClient,
)


@dataclass
class Dependencies:
    """Dependencies for testing."""

    git_reader: GitReader
    manifest_writer: JsonWriter
    strategy_reader: StrategyReader
    version_reader: VersionReader
    webhook_client: WebhookClient
