import asyncio

import pytest

from releaser.adapters import HttpsWebhookClient
from releaser.hexagon.entities import artefact

from .webhook import (  # noqa: F401
    EmbeddedTestServer,
    Spy,
    test_webhook_server,
    webhook_spy,
)


class TestHttpsWebookClient:
    @pytest.fixture(autouse=True)
    def setup(
        self, webhook_spy: Spy, test_webhook_server: EmbeddedTestServer  # noqa: F811
    ) -> None:
        self.spy = webhook_spy
        self.server = test_webhook_server
        self.client = HttpsWebhookClient()

    @pytest.mark.asyncio
    async def test_http_request_fails(self) -> None:
        def act() -> None:
            self.client.post_json(
                "http://localhost:8000/webhook", artefact.Manifest(applications={})
            )

        await asyncio.get_event_loop().run_in_executor(None, act)
        assert len(self.spy.received) == 1
        request = self.spy.received[0]
        assert request.json == {"applications": {}}
        assert request.method == "POST"
        assert request.path == "/webhook"
