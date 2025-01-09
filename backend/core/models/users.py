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

from pydantic import UUID4, Field, AwareDatetime
from core.models.base import BaseDatabaseModel
from core import helpers

__all__ = (
    "USER_USERNAME_MAX_LENGTH",
    "USER_USERNAME_MIN_LENGTH",
    "USER_FULLNAME_MAX_LENGTH",
    "USER_FULLNAME_MIN_LENGTH",
    "USER_PASSWORD_MIN_LENGTH",
    "USER_BIO_MAX_LENGTH",
    "User",
    "AuthorizedUser",
    "GetAuthorizedUserCredsJSON",
    "GetAuthorizedUserTokenJSON",
    "GetAuthorizedUserJSONT",
    "EditAuthorizedUserJSON",
)


USER_USERNAME_MAX_LENGTH = 80
USER_USERNAME_MIN_LENGTH = 3
USER_FULLNAME_MAX_LENGTH = 100
USER_FULLNAME_MIN_LENGTH = 3
USER_BIO_MAX_LENGTH = 300
USER_PASSWORD_MIN_LENGTH = 8


class User(BaseDatabaseModel):
    """Represents a user."""

    id: UUID4 = Field(alias="_id")
    """The identifier for this user."""

    username: str = Field(max_length=USER_USERNAME_MAX_LENGTH, min_length=USER_USERNAME_MIN_LENGTH)
    """The user's unique username."""

    created_at: AwareDatetime
    """The time when this user was created."""

    fullname: str | None = Field(
        max_length=USER_FULLNAME_MAX_LENGTH,
        min_length=USER_FULLNAME_MIN_LENGTH,
        default=None,
    )
    """The user's full name."""

    bio: str | None = Field(
        max_length=USER_BIO_MAX_LENGTH,
        default=None,
    )
    """The user's bio section."""


class AuthorizedUser(User):
    """Represents a user which is authorized with its credentials."""

    password: str = Field(min_length=USER_PASSWORD_MIN_LENGTH)
    """The login password of the user."""

    token: str
    """The user's authorization token."""

# --- API types --- #

class GetAuthorizedUserCredsJSON(BaseDatabaseModel):
    """Request JSON body for GET /users/authorized involving user credentials"""

    username: str
    """The username of user."""

    password: str
    """The login password."""


class GetAuthorizedUserTokenJSON(BaseDatabaseModel):
    """Request JSON body for GET /users/authorized involving authorization token."""

    token: str
    """The authorization token."""


GetAuthorizedUserJSONT = GetAuthorizedUserTokenJSON | GetAuthorizedUserCredsJSON
"""Type alias for union of GetAuthorizedUserTokenJSON and GetAuthorizedUserCredsJSON."""


class EditAuthorizedUserJSON(BaseDatabaseModel):
    """Request JSON body for PATCH /users/authorized."""

    username: str = Field(max_length=USER_USERNAME_MAX_LENGTH, min_length=USER_USERNAME_MIN_LENGTH, default=helpers.MISSING)
    """The new username."""

    fullname: str | None = Field(
        max_length=USER_FULLNAME_MAX_LENGTH,
        min_length=USER_FULLNAME_MIN_LENGTH,
        default=helpers.MISSING,
    )
    """The full name. Set None to remove."""

    bio: str | None = Field(
        max_length=USER_BIO_MAX_LENGTH,
        default=helpers.MISSING,
    )
    """The user's bio. Set None to remove."""

    password: str = Field(min_length=USER_PASSWORD_MIN_LENGTH, default=helpers.MISSING)
    """The login password of the user."""


class CreateUserJSON(BaseDatabaseModel):
    """Request JSON body for POST /users"""

    username: str = Field(max_length=USER_USERNAME_MAX_LENGTH, min_length=USER_USERNAME_MIN_LENGTH, default=helpers.MISSING)
    """The new username."""

    fullname: str | None = Field(
        max_length=USER_FULLNAME_MAX_LENGTH,
        min_length=USER_FULLNAME_MIN_LENGTH,
        default=helpers.MISSING,
    )
    """The full name (optional)"""

    password: str = Field(min_length=USER_PASSWORD_MIN_LENGTH, default=helpers.MISSING)
    """The login password of the user."""
