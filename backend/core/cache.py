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

from redis.asyncio import Redis
from core.config import Config
from core.models import users

import json

class CacheManager:
    """Manages Redis caching operations.

    This class is not used directly but is created and maintained by the
    DatabaseClient instead.
    """

    def __init__(self) -> None:
        self._redis = Redis.from_url(Config.REDIS_URI)  # type: ignore

    def get_redis_client(self) -> Redis:
        """Returns the underlying :class:`redis.asyncio.Redis` instance."""
        return self._redis

    async def close(self) -> None:
        """Closes the underlying Redis connection."""
        await self._redis.aclose()

    def _apply_scheme(self, scheme: str, value: str) -> str:
        return f"{scheme}:{value}"

    # --- Users by token ---

    def _scheme_user_token(self, value: str):
        return self._apply_scheme("user_token", value)
    
    async def get_user_by_token(self, token: str) -> users.AuthorizedUser | None:
        """Gets the user for the given encrypted token if present otherwise None."""
        data = await self._redis.get(self._scheme_user_token(token))
        if data:
            return users.AuthorizedUser(**json.loads(data))

    async def set_user_by_token(self, user: users.AuthorizedUser, update: bool = False) -> None:
        """Caches the given user with encrypted token as the key.

        If update=True then given value is only cached if another value
        was previously cached.
        """
        key = self._scheme_user_token(user.token)
        value = json.dumps(user.model_dump_database())
        await self._redis.set(key, value, ex=300, xx=update)

    async def delete_user_by_token(self, token: str) -> None:
        """Evicts the given user for the given encrypted token."""
        await self._redis.delete(self._scheme_user_token(token))

    # --- Users by ID ---

    def _scheme_user_id_integ(self, user_id: str):
        return self._apply_scheme("user_id_integ", user_id)

    async def check_user_id_exists(self, user_id: str) -> bool | None:
        """Checks if the given user ID exists or not.

        If this method returns None, it means that existence is not known.
        """
        exists = await self._redis.get(self._scheme_user_id_integ(user_id))

        if exists is None:
            return

        return bool(int(exists))

    async def set_user_id_exists(self, user_id: str, exists: bool, update: bool = False) -> None:
        """Sets existence status of a user ID."""
        key = self._scheme_user_id_integ(user_id)
        await self._redis.set(key, int(exists), xx=update, ex=300)

    # --- Websocket Connections ---

    def _scheme_user_sessions(self, user_id: str):
        return self._apply_scheme("user_sessions", user_id)

    async def get_user_sessions(self, user_id: str) -> list[str]:
        """Get list of IDs of websocket sessions that user has."""
        data = await self._redis.get(self._scheme_user_sessions(user_id))
        if data is None:
            return []
        else:
            return json.loads(data)

    async def insert_user_session_id(self, user_id: str, session_id: str) -> None:
        """Inserts a websocket session ID for the given user ID."""
        session_ids = await self.get_user_sessions(user_id)
        session_ids.append(session_id)
        await self._redis.set(self._scheme_user_sessions(user_id), json.dumps(session_ids))

    async def delete_user_session_id(self, user_id: str, session_id: str) -> bool:
        """Deletes a websocket session ID from the user's session.
        
        Returns True if the operation was successful or False if no session
        with that ID is stored.
        """
        session_ids = await self.get_user_sessions(user_id)
        try:
            session_ids.remove(session_id)
        except ValueError:
            return False
        else:
            await self._redis.set(self._scheme_user_sessions(user_id), json.dumps(session_ids))
            return True

    async def clear_user_session_ids(self, user_id: str) -> None:
        """Removes all stored session IDs for given user."""
        await self._redis.delete(self._scheme_user_sessions(user_id))
