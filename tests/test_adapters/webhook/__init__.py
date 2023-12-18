from __future__ import annotations

import pytest
import pytest_asyncio

from .embedded_server import EmbeddedTestServer
from .fake_app import Spy


@pytest.fixture
def webhook_spy() -> Spy:
    return Spy()


@pytest_asyncio.fixture
async def test_webhook_server(webhook_spy: Spy):
    async with EmbeddedTestServer(webhook_spy) as server:
        yield server


__all__ = ["Spy", "EmbeddedTestServer", "webhook_spy", "test_webhook_server"]
