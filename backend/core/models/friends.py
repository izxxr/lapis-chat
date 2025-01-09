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
from pydantic import UUID4, Field, AwareDatetime
from core.models.base import BaseDatabaseModel

__all__ = (
    "Friend",
    "FriendObjectId",
    "FriendRequest",
    "FriendRequestObjectId",
)


class FriendObjectId(BaseDatabaseModel):
    """The composite MongoDB object ID for Friend object."""

    first_user: UUID4
    """The ID of first user."""

    second_user: UUID4
    """The ID of second user."""


class Friend(BaseDatabaseModel):
    """Represents a friendship between two users."""

    id: FriendObjectId = Field(alias="_id")
    """The IDs of friends."""

    created_at: AwareDatetime
    """The time when users became friends."""

    operating_user_id: str | None = Field(default=None, exclude=True)
    """The ID of user who requested this object from API."""

    def model_dump_api(self, **kwargs: Any) -> dict[str, Any]:
        if self.operating_user_id:
            if self.operating_user_id == str(self.id.first_user):
                user_id = self.id.second_user
            elif self.operating_user_id == str(self.id.second_user):
                user_id = self.id.first_user
            else:
                raise RuntimeError("operating_user_id is invalid")
        else:
            raise RuntimeError("model_dump_api() requires operating_user_id specified.")

        data: dict[str, Any] = {
            "user_id": user_id,
            "created_at": self.created_at.isoformat()
        }
        return data


class FriendRequestObjectId(BaseDatabaseModel):
    """The composite MongoDB object ID for FriendRequest object."""

    requester_id: UUID4
    """The ID of user who initiated the friend request."""

    recipient_id: UUID4
    """The ID of user who received the friend request."""


class FriendRequest(BaseDatabaseModel):
    """Represents a friend request."""

    id: FriendRequestObjectId = Field(alias="_id")
    """The composite object ID containing requester and recipient IDs."""

    created_at: AwareDatetime
    """The time when users became friends."""

    operating_user_id: str | None = Field(default=None, exclude=True)
    """The ID of user who requested this object from API."""

    def model_dump_api(self, **kwargs: Any) -> dict[str, Any]:
        if self.operating_user_id:
            if self.operating_user_id == str(self.id.recipient_id):
                incoming = True
                user_id = self.id.requester_id
            elif self.operating_user_id == str(self.id.requester_id):
                incoming = False
                user_id = self.id.recipient_id
            else:
                raise RuntimeError("operating_user_id is invalid")
        else:
            raise RuntimeError("model_dump_api() requires operating_user_id specified.")

        data: dict[str, Any] = {
            "user_id": user_id,
            "incoming": incoming,
            "created_at": self.created_at.isoformat()
        }
        return data
