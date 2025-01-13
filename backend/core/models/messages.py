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

from enum import IntEnum
from pydantic import UUID4, Field, AwareDatetime
from core.models.base import BaseDatabaseModel

__all__ = (
    "Message",
    "MessageDestinationType",
    "SendMessageJSON",
    "EditMessageJSON",
    "MESSAGE_CONTENT_MIN_LENGTH",
    "MESSAGE_CONTENT_MAX_LENGTH",
)


MESSAGE_CONTENT_MIN_LENGTH = 1
MESSAGE_CONTENT_MAX_LENGTH = 256


class MessageDestinationType(IntEnum):
    """The type of destination where the message is."""

    DIRECT = 0
    """The direct message between two users."""

    GROUP = 1
    """Message in a group chat comprising many users."""


class Message(BaseDatabaseModel):
    """Represents a message."""

    id: UUID4 = Field(alias="_id")
    """The identifier for this message."""

    author_id: UUID4
    """The ID of the message's author."""

    dest_type: MessageDestinationType
    """The type of message's destination."""

    dest_id: UUID4
    """The ID of message's destination.

    If dest_type=DIRECT, this is the ID of user that this message was sent to
    in DMs between that user and the author (represented by author_id).

    If dest_type=GROUP, this is the ID of group chat.
    """

    content: str
    """The content of message."""

    created_at: AwareDatetime
    """The time when this message was sent."""

    edited_at: AwareDatetime | None = None
    """The time when this message was last edited, or None if never."""


class SendMessageJSON(BaseDatabaseModel):
    """JSON body for POST /dms/{user_id}/messages"""

    content: str = Field(min_length=MESSAGE_CONTENT_MIN_LENGTH, max_length=MESSAGE_CONTENT_MAX_LENGTH)
    """The content of message."""


class EditMessageJSON(BaseDatabaseModel):
    """JSON body for PATCH /dms/{user_id}/messages/{message_id}"""

    content: str = Field(min_length=MESSAGE_CONTENT_MIN_LENGTH, max_length=MESSAGE_CONTENT_MAX_LENGTH)
    """The content of message."""
