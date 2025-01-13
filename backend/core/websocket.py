# MIT License

# Copyright (c) 2025 lapis-chat

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from fastapi import WebSocketDisconnect
from typing import TYPE_CHECKING, Any
from core.helpers import MISSING
from core import codes

import asyncio

if TYPE_CHECKING:
    from fastapi import WebSocket
    from core.models import users
    from core.database import DatabaseClient

__all__ = (
    "WSClient",
)


class WSClient:
    """Contains and manages the FastAPI WebSocket connection."""

    def __init__(self, ws: WebSocket, db: DatabaseClient, user: users.AuthorizedUser) -> None:
        self.user = user
        self._ready = asyncio.Event()
        self._ws = ws
        self._db = db
        self._cache = db.get_cache_manager()
        self._pubsub = self._cache.get_redis_client().pubsub()  # type: ignore
        self._connected = False
        self._pubsub_listener_task = None
        self._session_id = None

    @property
    def session_id(self) -> str:
        """The session ID associated with this websocket connection."""
        if self._session_id is None:
            raise RuntimeError("The websocket connection is not registered.")
        
        return self._session_id

    def _register(self, session_id: str) -> None:
        self._session_id = session_id
        self._connected = True

    async def _send_initial_packets(self) -> None:
        await self.send(codes.HELLO)
        await self._ready.wait()
        await self.send(codes.READY, {"user": self.user.model_dump_api(), "session_id": self.session_id})

    async def _pubsub_listener_worker(self) -> None:
        while self._connected:
            await self._pubsub.get_message(ignore_subscribe_messages=True, timeout=None)

    async def close(self, code: int = 1000, close_ws: bool = False) -> None:
        """Closes the WebSocket connection.

        The underlying websocket connection is only attempted to be closed
        if close_ws is True. Otherwise this method only serves as a cleanup
        function.
        """
        if close_ws:
            await self._ws.close(code=code)
        if self._pubsub_listener_task:
            self._pubsub_listener_task.cancel()

        await self._db.connections.delete_connection(self)
        await self._pubsub.unsubscribe()  # type: ignore
        await self._pubsub.aclose()

        self._connected = False

    async def start(self) -> None:
        """Starts listening to the WebSocket messages."""

        await self._db.connections.register_connection(self)
        await self._ws.accept()
        await self._send_initial_packets()

        self._pubsub_listener_task = asyncio.create_task(self._pubsub_listener_worker())

        try:
            while self._connected:
                await self._ws.receive_text()
        except WebSocketDisconnect:
            await self.close()

    async def send(self, op: codes.OperationCode, d: Any = MISSING, t: Any = MISSING) -> None:
        """Sends a packet over WebSocket for given operation code with an optional data."""
        await self._ws.send_json(op.ws_packet(d, t))
