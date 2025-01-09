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

from fastapi import HTTPException

__all__ = (
    "Error",
    "GENERIC_ERROR",
    "ENTITY_NOT_FOUND",
    "INVALID_AUTHORIZATION",
    "USERNAME_TAKEN",
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

# Authentication errors
INVALID_AUTHORIZATION = Error(401, 11000, "Invalid credentials or authorization token.")

# Users related errors
USERNAME_TAKEN = Error(409, 12000, "This username is already taken.")
