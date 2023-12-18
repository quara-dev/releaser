from __future__ import annotations

import pytest

from ..stubs import GitReaderStub, JsonWriterStub, StrategyReaderStub, VersionReaderStub


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
