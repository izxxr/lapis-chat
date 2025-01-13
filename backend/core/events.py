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

import json

if TYPE_CHECKING:
    from core.cache import CacheManager
    from core.models import users, friends

__all__ = (
    "EventHandler",
)


class EventHandler:
    """Manages events sent over WebSocket using Redis PubSub."""

    def __init__(self, cache: CacheManager) -> None:
        self._cache = cache
        self._redis = cache.get_redis_client()

    def _apply_scheme(self, scheme: str, *values: Any) -> str:
        return f"event_{scheme}:{','.join(values)}"

    async def _dispatch(self, channel: str, message: Any) -> None:
        if isinstance(message, dict):
            message = json.dumps(message)

        await self._redis.publish(channel, message)  # type: ignore


    # User events

    def channel_user_update(self, user_id: str) -> str:
        """Channel for receiving the user updates.

        Whenever user corresponding to user_id is updated, an event is published
        in this channel.
        """
        return self._apply_scheme("user_update", user_id)

    def channel_user_delete(self, user_id: str) -> str:
        """Channel for receiving the user deletion events.

        Whenever user corresponding to user_id is deleted, an event is published in
        this channel.
        """
        return self._apply_scheme("user_delete", user_id)

    async def dispatch_user_update(self, user: users.User) -> None:
        await self._dispatch(self.channel_user_update(str(user.id)), user.model_dump_api())

    async def dispatch_user_delete(self, user_id: str) -> None:
        await self._dispatch(self.channel_user_delete(user_id), {"user_id": user_id})

    # Friend events

    def channel_friend_delete(self, user_id: str) -> str:
        """Channel for receiving unfriend events.

        Whenever user corresponding to user_id unfriends another user or is unfriended
        by another user, an event is published to this channel.
        """
        return self._apply_scheme("friend_delete", user_id)

    def channel_friend_create(self, user_id: str) -> str:
        """Channel for receiving friend create events.
        
        Whenever user corresponding to user_id accepts an incoming friend request
        or an outgoing friend request from the user_id user is accepted, an event
        is published to this channel.
        """
        return self._apply_scheme("friend_create", user_id)

    async def dispatch_friend_create(self, operating_user_id: str, target_id: str) -> None:
        """Dispatches the FRIEND_CREATE event.

        This event is dispatched when two users become friend and is dispatched
        to both users.
        """
        await self._dispatch(self.channel_friend_create(operating_user_id), {"user_id": target_id})
        await self._dispatch(self.channel_friend_create(target_id), {"user_id": operating_user_id})

    async def dispatch_friend_delete(self, operating_user_id: str, target_id: str) -> None:
        await self._dispatch(self.channel_friend_delete(operating_user_id), {"user_id": target_id})
        await self._dispatch(self.channel_friend_delete(target_id), {"user_id": operating_user_id})

    # Friend Request events

    def channel_friend_request_receive(self, recipient_id: str) -> str:
        """Channel for friend request receive events.

        Whenever the user corresponding to recipient_id receives an incoming friend
        request, an event is published on this channel.
        """
        return self._apply_scheme("friend_request_receive", recipient_id)

    async def dispatch_friend_request_receive(self, request: friends.FriendRequest) -> None:
        await self._dispatch(self.channel_friend_request_receive(str(request.id.recipient_id)), request.model_dump_api())
