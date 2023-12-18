from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI, Request


@dataclass
class SpyRequest:
    method: str
    path: str
    query: str
    json: str


class Spy:
    def __init__(self) -> None:
        self.received: list[SpyRequest] = []


def create_app(spy: Spy):
    app = FastAPI(title="Testing Webhook")

    @app.post("/QUARA/_apis/public/distributedtask/webhooks/TestWebhook")
    async def webhook(request: Request):
        spy.received.append(
            SpyRequest(
                method=request.method,
                path=request.url.path,
                query=request.url.query,
                json=await request.json(),
            )
        )
        return {"status": "OK"}

    return app
