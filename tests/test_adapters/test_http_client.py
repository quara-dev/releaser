from __future__ import annotations

import asyncio

import pytest

from releaser.hexagon.entities import artefact
from releaser.infra.webhook_client.standard_http import HttpWebhookClient

from .webhook import EmbeddedTestServer, Spy


class TestHttpsWebookClient:
    @pytest.fixture(autouse=True)
    def setup(
        self, webhook_spy: Spy, test_webhook_server: EmbeddedTestServer  # noqa: F811
    ) -> None:
        self.spy = webhook_spy
        self.server = test_webhook_server
        self.client = HttpWebhookClient()

    @pytest.mark.asyncio
    async def test_http_request_fails(self) -> None:
        def act() -> None:
            self.client.post_json(
                "http://localhost:8000/QUARA/_apis/public/distributedtask/webhooks/TestWebhook?api-version=6.0-preview",
                artefact.Manifest(applications={}),
            )

        await asyncio.get_event_loop().run_in_executor(None, act)
        assert len(self.spy.received) == 1
        request = self.spy.received[0]
        assert request.json == {"applications": {}}
        assert request.method == "POST"
        assert (
            request.path == "/QUARA/_apis/public/distributedtask/webhooks/TestWebhook"
        )
        assert request.query == "api-version=6.0-preview"
