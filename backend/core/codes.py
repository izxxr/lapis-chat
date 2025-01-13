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
from fastapi import HTTPException
from core.helpers import MISSING

__all__ = (
    "Error",
    "GENERIC_ERROR",
    "ENTITY_NOT_FOUND",
    "INVALID_AUTHORIZATION",
    "USERNAME_TAKEN",
    "OperationCode",
    "HELLO",
    "READY",
    "EVENT",
)


class Error:
    """Represents an error."""

    def __init__(self, http_status_code: int, error_code: int, message: str) -> None:
        self.http_status_code = http_status_code
        self.error_code = error_code
        self.message = message

    def http_exc(self, message: str | None = None) -> HTTPException:
        """Raise this error as fastapi.HTTPException.

        The `message` parameter can be used to override existing message.
        """
        return HTTPException(self.http_status_code, {"error_code": self.error_code, "message": message if message else self.message})


# Generic errors
GENERIC_ERROR = Error(400, 10000, "An unknown error occured.")
ENTITY_NOT_FOUND = Error(404, 10001, "This entity could not be found.")
PAGINATION_LIMIT_EXCEEDED = Error(400, 10002, "Pagination limit of this entity has been exceeded.")
DATETIME_ERROR = Error(400, 10003, "Invalid datetime format.")

# Authentication errors
INVALID_AUTHORIZATION = Error(401, 11000, "Invalid credentials or authorization token.")

# Users related errors
USERNAME_TAKEN = Error(409, 12000, "This username is already taken.")

# Friends and friend requests
REQUESTER_RECIPIENT_ID_EQUAL = Error(400, 13000, "Requester and recipient ID cannot be same.")
FRIEND_REQUEST_ALREADY_SENT = Error(409, 13001, "Friend request has already been sent.")
USER_ALREADY_FRIEND = Error(409, 13002, "The user is already a friend.")


class OperationCode:
    """Represents a WebSocket operation code."""

    def __init__(self, code: int, name: str) -> None:
        self.code = code
        self.name = name

    def ws_packet(self, d: Any = MISSING, t: Any = MISSING) -> dict[str, Any]:
        """Returns the operation code as WS packet format."""
        data: dict[str, Any] = {"op": self.code}
        if d is not MISSING:
            data["d"] = d
        if t is not MISSING:
            data["t"] = t

        return data


HELLO = OperationCode(0, "HELLO")
READY = OperationCode(1, "READY")
EVENT = OperationCode(2, "EVENT")
