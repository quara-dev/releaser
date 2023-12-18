from __future__ import annotations

from releaser.cli.context import Dependencies
from releaser.infra.git_reader.stub import GitReaderStub
from releaser.infra.image_baker.stub import ImageBakerStub
from releaser.infra.json_writer.stub import JsonWriterStub
from releaser.infra.strategy_reader.stub import StrategyReaderStub
from releaser.infra.version_reader.stub import VersionReaderStub
from releaser.infra.webhook_client.stub import WebhookClientStub


class DependenciesForTests(Dependencies):
    git_reader: GitReaderStub
    image_baker: ImageBakerStub
    manifest_writer: JsonWriterStub
    strategy_reader: StrategyReaderStub
    version_reader: VersionReaderStub
    webhook_client: WebhookClientStub


__all__ = [
    "GitReaderStub",
    "JsonWriterStub",
    "ImageBakerStub",
    "StrategyReaderStub",
    "VersionReaderStub",
    "WebhookClientStub",
    "DependenciesForTests",
]
