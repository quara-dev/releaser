from __future__ import annotations

import asyncio
from contextlib import AsyncExitStack

from uvicorn import Config, Server

from .fake_app import Spy, create_app


class EmbeddedTestServer:
    def __init__(self, spy: Spy) -> None:
        self._app = create_app(spy)
        self._config = Config(self._app, host="127.0.0.1", port=8000)
        self._server = Server(self._config)
        self._server.install_signal_handlers = lambda: None
        self._stack: AsyncExitStack | None = None
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()
        self._task = asyncio.create_task(self._server.serve(None))
        await asyncio.sleep(0)
        self._stack.push_async_callback(self._cancel_on_exit)

    async def stop(self) -> None:
        if not self._stack:
            return
        await self._stack.__aexit__(None, None, None)

    async def _cancel_on_exit(self) -> None:
        if not self._task:
            return
        if self._task.done():
            return
        self._task.cancel()
        await asyncio.wait([self._task])

    async def __aenter__(self) -> "EmbeddedTestServer":
        await self.start()
        return self

    async def __aexit__(self, *args: object, **kwargs: object) -> None:
        await self.stop()
