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
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import Config
from core.cache import CacheManager
from core.models import users, friends
from core.events import EventHandler
from core.connections import ConnectionManager
from core import helpers
from core import codes

import uuid
import datetime
import pymongo
import pymongo.errors

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
        self.events = EventHandler(self._cache)
        self.connections = ConnectionManager(self)

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

    async def validate_user_username(self, username: str) -> None:
        """Ensures that the given username must not exist raising HTTP exception otherwise."""
        existing = await self._db.users.find_one({"username": username})
        if existing:
            raise codes.USERNAME_TAKEN.http_exc()

    async def validate_user_exists(self, user_id: str) -> None:
        """Ensures that the given user ID exists."""
        exists = await self._cache.check_user_id_exists(user_id)
        if exists is None:
            exists = await self._db.users.find_one({"_id": user_id})
            await self._cache.set_user_id_exists(user_id, exists is not None)
        if not exists:
            raise codes.ENTITY_NOT_FOUND.http_exc("This user does not exist.")

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

        if not deleted:
            return

        await self._db.friend_requests.delete_many({"$or": [{"_id.requester_id": user_id}, {"_id.recipient_id": user_id}]})
        await self._db.friends.delete_many({"$or": [{"_id.first_user": user_id}, {"_id.second_user": user_id}]})

        await self._cache.delete_user_by_token(deleted["token"])
        await self._cache.set_user_id_exists(user_id, False, update=True)
        await self.connections.disconnect_user_connections(user_id)
        await self.events.dispatch_user_delete(user_id)

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
            return_document=pymongo.ReturnDocument.AFTER
        )
        
        # user_data should never be None as this method is only called
        # by /authorized endpoint that requires a valid user token.
        assert user_data is not None
        user = users.AuthorizedUser(**user_data)

        await self._cache.set_user_by_token(user, update=update)
        await self.events.dispatch_user_update(user)
        return user

    # -- Friends --

    async def fetch_all_friends(self, user_id: str) -> list[friends.Friend]:
        """Get all friends of given user's ID.

        Returned objects are operating user ID aware.
        """
        query = {
            "$or": [
                {"_id.first_user": user_id},
                {"_id.second_user": user_id},
            ]
        }
        friends_data: list[dict[str, Any]] = await self._db.friends.find(
            query,
            sort=[("created_at", pymongo.ASCENDING)]
        ).to_list()  # type: ignore

        return [friends.Friend(**f, operating_user_id=user_id) for f in friends_data]

    async def fetch_friend(self, user_id: str, target_id: str) -> friends.Friend | None:
        """Returns Friend object between the given users' IDs.

        If two users are not friend, this returns None. The first
        user ID is considered as operating user's ID.
        """
        query = {
            "$or": [
                {"_id.first_user": user_id, "_id.second_user": target_id},
                {"_id.first_user": target_id, "_id.second_user": user_id},
            ]
        }
        friend_data = await self._db.friends.find_one(query)

        if friend_data:
            return friends.Friend(**friend_data, operating_user_id=user_id)

    async def unfriend_user(self, user_id: str, target_id: str) -> None:
        """Unfriends two users."""
        if user_id == target_id:
            raise codes.REQUESTER_RECIPIENT_ID_EQUAL.http_exc()

        query = {
            "$or": [
                {"_id.first_user": user_id, "_id.second_user": target_id},
                {"_id.first_user": target_id, "_id.second_user": user_id},
            ]
        }
        # In theory, delete_one should also work here as other methods ensure
        # that documents with same but swapped first_user/second_user do
        # not coexist. However, delete_many() is safer in case that happens
        # for any reason.
        await self._db.friends.delete_many(query)
        await self.events.dispatch_friend_delete(user_id, target_id)

    # -- Friend Requests --

    async def fetch_all_friend_requests(self, user_id: str) -> list[friends.FriendRequest]:
        """Fetches all the friend requests for given user's ID.

        Returned objects are operating ID aware.
        """
        query = {
            "$or": [
                {"_id.requester_id": user_id},
                {"_id.recipient_id": user_id},
            ]
        }
        results: list[dict[str, Any]] = await self._db.friend_requests.find(
            query,
            sort=[("created_at", pymongo.ASCENDING)]
        ).to_list()  # type: ignore

        return [friends.FriendRequest(**r, operating_user_id=user_id) for r in results]

    async def fetch_friend_request(self, requester_id: str, recipient_id: str) -> friends.FriendRequest | None:
        """Returns FriendRequest object between the given users' IDs.

        The returned object is not operating user's ID aware.
        """
        query = {
            "_id.requester_id": requester_id,
            "_id.recipient_id": recipient_id,
        }
        result = await self._db.friend_requests.find_one(query)

        if result:
            return friends.FriendRequest(**result, operating_user_id=None)

    async def delete_friend_request(self, requester_id: str, recipient_id: str) -> None:
        """Delete friend request between the given users' IDs."""
        query = {
            "_id.requester_id": requester_id,
            "_id.recipient_id": recipient_id,
        }
        await self._db.friend_requests.delete_one(query)

    async def send_accept_friend_request(self, user_id: str, target_id: str) -> bool:
        """Sends or accepts friend request between the given users' IDs.

        The first user ID is considered as operating user's ID.
        """
        if user_id == target_id:
            raise codes.REQUESTER_RECIPIENT_ID_EQUAL.http_exc()

        incoming_request = await self.fetch_friend_request(target_id, user_id)

        if incoming_request is None:
            # sending a request
            friendship_exists = await self.fetch_friend(user_id, target_id)
            if friendship_exists:
                raise codes.USER_ALREADY_FRIEND.http_exc()

            await self.validate_user_exists(target_id)
            request_data: dict[str, Any] = {
                "_id": {
                    "requester_id": user_id,
                    "recipient_id": target_id,
                },
                "created_at": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
            }
            try:
                await self._db.friend_requests.insert_one(request_data)
            except pymongo.errors.DuplicateKeyError:
                raise codes.FRIEND_REQUEST_ALREADY_SENT.http_exc()

            await self.events.dispatch_friend_request_receive(friends.FriendRequest(**request_data, operating_user_id=user_id))
            return True
        else:
            # accepting the request
            friend_data: dict[str, Any] = {
                "_id": {
                    "first_user": user_id,
                    "second_user": target_id,
                },
                "created_at": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
            }
            await self.delete_friend_request(target_id, user_id)
            await self._db.friends.insert_one(friend_data)
            await self.events.dispatch_friend_create(user_id, target_id)
            return False

    async def withdraw_reject_friend_request(self, user_id: str, target_id: str) -> bool:
        """Withdraws or rejects friend request between the given users' IDs.

        The first user ID is considered as operating user's ID. Returns True
        if a request was withdrawn and False if a request was rejected. Raises
        404 if no request was found for the given user.
        """
        if user_id == target_id:
            raise codes.REQUESTER_RECIPIENT_ID_EQUAL.http_exc()

        incoming_request = await self.fetch_friend_request(target_id, user_id)

        if incoming_request is not None:
            # rejecting a request
            await self.delete_friend_request(target_id, user_id)
            return False

        outgoing_request = await self.fetch_friend_request(user_id, target_id)

        if outgoing_request is not None:
            # withdrawing a request
            await self.delete_friend_request(user_id, target_id)
            return True
        
        raise codes.ENTITY_NOT_FOUND.http_exc("No incoming or outgoing request found for this user.")

db_ctx: ContextVar[DatabaseClient] = ContextVar("db", default=DatabaseClient())
"""Context variable for managing global database client instance."""
