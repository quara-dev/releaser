from __future__ import annotations

import pytest

from .stubs import (
    DependenciesForTests,
    GitReaderStub,
    ImageBakerStub,
    JsonWriterStub,
    StrategyReaderStub,
    VersionReaderStub,
    WebhookClientStub,
)


@pytest.fixture
def image_baker():
    return ImageBakerStub()


@pytest.fixture
def git_reader():
    return GitReaderStub()


@pytest.fixture
def json_writer():
    return JsonWriterStub()


@pytest.fixture
def strategy_reader():
    return StrategyReaderStub()


@pytest.fixture
def version_reader():
    return VersionReaderStub()


@pytest.fixture
def webhook_client():
    return WebhookClientStub()


@pytest.fixture
def testing_dependencies(
    git_reader: GitReaderStub,
    json_writer: JsonWriterStub,
    strategy_reader: StrategyReaderStub,
    version_reader: VersionReaderStub,
    webhook_client: WebhookClientStub,
    image_baker: ImageBakerStub,
):
    testing_dependencies = DependenciesForTests(
        git_reader=git_reader,
        manifest_writer=json_writer,
        strategy_reader=strategy_reader,
        version_reader=version_reader,
        webhook_client=webhook_client,
        image_baker=image_baker,
    )
    return testing_dependencies
