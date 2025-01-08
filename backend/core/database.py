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

from typing import Any
from contextvars import ContextVar
from pymongo import ReturnDocument
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import Config
from core.cache import CacheManager
from core.models import users
from core import helpers, errcodes

import uuid
import datetime

__all__ = (
    "DatabaseClient",
)


class DatabaseClient:
    """Manages database operations.

    This class deals with operations with MongoDB and also maintains an instance
    of the CacheManager class to manage cache.
    """

    def __init__(self) -> None:
        self._mongodb = AsyncIOMotorClient[dict[str, Any]](Config.MONGODB_URI)
        self._cache = CacheManager()
        self._db = self._mongodb[Config.MONGODB_DATABASE_NAME]

    # Public methods

    def get_database_client(self) -> AsyncIOMotorClient[dict[str, Any]]:
        """Returns the underlying :class:`motor.asyncio.AsyncIOMotorClient` instance."""
        return self._mongodb

    def get_cache_manager(self) -> CacheManager:
        """Returns the underlying :class:`CacheManager` instance."""
        return self._cache

    async def close(self) -> None:
        """Closes all the underlying connections."""
        await self._cache.close()
        self._mongodb.close()

    # -- Users --

    async def validate_user_username(self, username: str) -> users.User | None:
        """Ensures that the given username must not exist raising HTTP exception otherwise."""
        existing = await self._db.users.find_one({"username": username})
        if existing:
            raise errcodes.USERNAME_TAKEN.http_exc()

    async def fetch_user(self, user_id: str, authorized: bool = False) -> users.User | users.AuthorizedUser | None:
        """Fetches the user from given ID.

        If authorized=True, the returned value is a users.AuthorizedUser containing
        the users credentials.
        """
        data = await self._db.users.find_one({"_id": user_id})

        if data:
            return users.AuthorizedUser(**data) if authorized else users.User(**data)

    async def fetch_user_credentials(self, username: str, password: str) -> users.AuthorizedUser | None:
        """Gets the authorized user using credentials."""
        data = await self._db.users.find_one({"username": username, "password": password})
        if data:
            return users.AuthorizedUser(**data)

    async def fetch_user_authorized(self, token: str, cache: bool = True) -> users.AuthorizedUser | None:
        """Gets the authorized user using the token.

        If cache=True (default), the fetched value from database is cached
        and reused on subsequent calls. Moreover, setting this parameter to
        False also prevents access from cache and forces a database call.
        """
        user = None

        if cache:
            user = await self._cache.get_user_by_token(token)
        if user is None:
            data = await self._db.users.find_one({"token": token})
            if data:
                user = users.AuthorizedUser(**data)
            if user and cache:
                await self._cache.set_user_by_token(user)

        return user

    async def create_user(self, create_data: users.CreateUserJSON) -> users.AuthorizedUser:
        """Creates a user."""
        await self.validate_user_username(create_data.username)

        user_data = create_data.model_dump()
        user_data.update({
            "_id": uuid.uuid4(),
            "token": helpers.generate_token(),
            "created_at": datetime.datetime.now(tz=datetime.timezone.utc),
        })
        user = users.AuthorizedUser(**user_data)
        await self._db.users.insert_one(user.model_dump_database())
        return user

    async def delete_user(self, user_id: str) -> None:
        """Deletes the user for given user ID."""
        deleted = await self._db.users.find_one_and_delete({"_id": user_id})

        if deleted:
            await self._cache.delete_user_by_token(deleted["token"])

    async def edit_user(self, user_id: str, data: users.EditAuthorizedUserJSON) -> users.AuthorizedUser:
        """Updates the user for given user ID."""
        update_data = data.model_dump_database(exclude_defaults=True, exclude_unset=True)
        update = True

        if data.username is not helpers.MISSING:
            await self.validate_user_username(data.username)

        if data.password is not helpers.MISSING:
            # If user updates the password then the authorization token should
            # also effectively be changed as security measure.
            update_data["token"] = helpers.generate_token()

            # Since token has changed, we need to update the key as well that
            # includes the old token in the cache so remove previous cache entry.
            update = False
            user = await self.fetch_user(user_id, authorized=True)
            await self._cache.delete_user_by_token(user.token)  # type: ignore

        user_data = await self._db.users.find_one_and_update(
            {"_id": user_id},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        
        # user_data should never be None as this method is only called
        # by /authorized endpoint that requires a valid user token.
        assert user_data is not None
        user = users.AuthorizedUser(**user_data)

        await self._cache.set_user_by_token(user, update=update)
        return user


db_ctx: ContextVar[DatabaseClient] = ContextVar("db", default=DatabaseClient())
"""Context variable for managing global database client instance."""
