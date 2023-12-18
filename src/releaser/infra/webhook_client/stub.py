from __future__ import annotations

from releaser.hexagon.entities import artefact
from releaser.hexagon.ports import WebhookClient


class WebhookClientStub(WebhookClient):
    def __init__(self) -> None:
        self._payload: artefact.Manifest | None = None
        self._url: str | None = None

    def post_json(self, webhook_url: str, manifest: artefact.Manifest) -> None:
        if self._payload:
            raise RuntimeError("payload already set in stub webhook client")
        if self._url:
            raise RuntimeError("url already set in stub webhook client")
        self._url = webhook_url
        self._payload = manifest

    def get_payload(self) -> artefact.Manifest | None:
        return self._payload

    def get_url(self) -> str | None:
        return self._url
