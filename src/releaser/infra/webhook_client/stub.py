from __future__ import annotations

from releaser.hexagon.entities import artefact
from releaser.hexagon.ports import WebhookClient


class WebhookClientStub(WebhookClient):
    """A stub webhook client that stores the payload and URL.

    A stub cannot be used twice in the same test without calling
    reset() in between.
    """

    def __init__(self) -> None:
        self._payload: artefact.Manifest | None = None
        self._url: str | None = None

    def post(self, webhook_url: str, manifest: artefact.Manifest) -> None:
        """Store the payload and URL."""

        if self._payload:
            raise RuntimeError("payload already set in stub webhook client")
        if self._url:
            raise RuntimeError("url already set in stub webhook client")
        self._url = webhook_url
        self._payload = manifest

    def get_payload(self) -> artefact.Manifest | None:
        """Test helper: get the payload sent to the webhook client."""
        return self._payload

    def get_url(self) -> str | None:
        """Test helper: get the URL sent to the webhook client."""
        return self._url

    def reset(self) -> None:
        """Test helper: reset the stub."""
        self._payload = None
        self._url = None
