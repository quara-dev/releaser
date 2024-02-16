"""Service used to send a POST request to a webhook URL with a
manifest as JSON payload."""

from __future__ import annotations

from dataclasses import dataclass

from releaser.hexagon.entities import artefact

from ..ports import WebhookClient


@dataclass
class ManifestNotifier:
    """Service used to publish manifest to webhook after a release."""

    webhook_url: str
    """The webhook URL to publish manifest to."""

    manifest: artefact.Manifest
    """The manifest to publish."""

    webhook_client: WebhookClient
    """The webhook client to use for publishing."""

    def execute(self) -> None:
        """Upload the manifest to webhook url."""
        self.webhook_client.post(self.webhook_url, self.manifest)
