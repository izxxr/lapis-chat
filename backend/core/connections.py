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

from typing import TYPE_CHECKING, Any
from core.models import messages
from core import codes

import asyncio
import uuid
import json

if TYPE_CHECKING:
    from core.database import DatabaseClient
    from core.websocket import WSClient

__all__ = (
    "ConnectionManager",
)    


class ConnectionManager:
    """Manages the ongoing WebSocket connections."""

    def __init__(self, db: DatabaseClient) -> None:
        self._db = db
        self._cache = db.get_cache_manager()
        self._connections: dict[str, WSClient] = {}
        self._events = db.events

    async def register_connection(self, ws: WSClient) -> None:
        """Registers a WebSocket connection."""
        session_id = str(uuid.uuid4())
        await self._cache.insert_user_session_id(str(ws.user.id), session_id)

        self._connections[session_id] = ws
        ws._register(session_id=session_id)  # type: ignore
        asyncio.create_task(self._subscribe_event_channels_worker(ws))

    async def delete_connection(self, ws: WSClient) -> None:
        """Unregisters the given WebSocket connection."""
        await self._cache.delete_user_session_id(str(ws.user.id), ws.session_id)
        self._connections.pop(ws.session_id, None)

    async def disconnect_user_connections(self, user_id: str) -> None:
        """Disconnects all WebSocket connections that the given user has."""
        session_ids = await self._cache.get_user_sessions(user_id)

        for session_id in session_ids:
            conn = self._connections.get(session_id)
            if conn:
                await conn.close(code=1000)

        await self._cache.clear_user_session_ids(user_id)

    def _event_handler_wrapper(self, ws: WSClient) -> Any:
        async def _event_handler(event_data: dict[str, Any]) -> None:
            data: str = event_data["data"]
            channel: str = event_data["channel"].decode()

            event, *_ = channel.split(":")
            assert event.startswith("event_")

            event = event.lstrip("event_").upper()
            await ws.send(codes.EVENT, json.loads(data), event)

        return _event_handler

    async def _subscribe_event_channels_worker(self, ws: WSClient) -> None:
        subscribe = ws._pubsub.subscribe  # type: ignore
        events = self._events
        user_id = str(ws.user.id)
        handler = self._event_handler_wrapper(ws)

        friends = await self._db.fetch_all_friends(user_id)

        for friend in friends:
            friend_id = friend.friend_id

            # User Events - Friends
            await subscribe(**{events.channel_user_update(friend_id): handler})
            await subscribe(**{events.channel_user_delete(friend_id): handler})

        # Friend Events
        await subscribe(**{events.channel_friend_create(user_id): handler})
        await subscribe(**{events.channel_friend_delete(user_id): handler})
        await subscribe(**{events.channel_friend_request_receive(user_id): handler})

        # Message Events - DMs
        await subscribe(**{events.channel_message_create(messages.MessageDestinationType.DIRECT, user_id): handler})
        await subscribe(**{events.channel_message_update(messages.MessageDestinationType.DIRECT, user_id): handler})
        await subscribe(**{events.channel_message_delete(messages.MessageDestinationType.DIRECT, user_id): handler})

        # Notify the main thread that subscription is done.
        ws._ready.set()  # type: ignore
