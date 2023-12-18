from __future__ import annotations

import http
import json
import sys
from dataclasses import asdict
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse

from releaser.hexagon.entities import artefact
from releaser.hexagon.ports import WebhookClient


class HttpWebhookClient(WebhookClient):
    """A webhook client that uses HTTP to send webhooks.

    HTTP client is implemented using the standard library.
    """

    def post(self, webhook_url: str, manifest: artefact.Manifest) -> None:
        """Send a webhook to the given URL with the given manifest as JSON."""

        parsed_url = urlparse(webhook_url)
        host = parsed_url.hostname
        if not host:
            raise ValueError(f"Invalid webhook URL: {webhook_url}")
        if parsed_url.query:
            path_with_params = f"{parsed_url.path}?{parsed_url.query}"
        else:
            path_with_params = parsed_url.path
        data = json.dumps(asdict(manifest), separators=(",", ":"))
        if parsed_url.scheme == "http":
            connection = HTTPConnection(host=host, port=parsed_url.port)
        else:
            connection = HTTPSConnection(host=host, port=parsed_url.port)
        connection.request(
            method="POST",
            url=path_with_params,
            body=data,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(data)),
            },
        )
        response = connection.getresponse()
        if response.status != http.HTTPStatus.OK:
            print(response.read().decode(), file=sys.stderr)
            raise RuntimeError(
                f"Failed to send webhook to {webhook_url}: {response.status} {response.reason}"
            )
