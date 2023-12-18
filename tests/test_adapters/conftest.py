from __future__ import annotations

import pytest
import pytest_asyncio

from .webhook import EmbeddedTestServer, Spy


@pytest.fixture
def webhook_spy() -> Spy:
    return Spy()


@pytest_asyncio.fixture
async def test_webhook_server(webhook_spy: Spy):
    async with EmbeddedTestServer(webhook_spy) as server:
        yield server
