# MIT License

# Copyright (c) 2023 Izhar Ahmad

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

from marshmallow import Schema, fields, validate
from schemas.fields import ULIDField, EnumField
from common.schemas_models import password_validator_schemas
from common.constants import (
    MAX_USERNAME_LENGTH,
    MIN_USERNAME_LENGTH,
    MAX_DISPLAY_NAME_LENGTH,
    MIN_DISPLAY_NAME_LENGTH,
    MAX_BIO_LENGTH,
    TOKEN_LENGTH,
)
from enum import IntEnum

__all__ = (
    'User',
    'Relationship',
    'RelationshipType',
)


class User(Schema):
    """Represents a user entity.

    Attributes
    ----------
    id: :class:`str`
        The unique ULID ID for this user.
    username: :class:`str`
        The unique username of user.
    display_name: Optional[:class:`str`]
        The display name of user.
    bio: Optional[:class:`str`]
        The bio or about me text of the user profile.
    email: :class:`str`
        The email address of the user.
    password: :class:`str`
        The password of user.
    token: :class:`str`
        The authorization token of user.
    flags: :class:`int`
        The bitwise value for the flags that user has.
    """
    id = ULIDField(required=True)
    username = fields.String(validate=validate.Length(max=MAX_USERNAME_LENGTH, min=MIN_USERNAME_LENGTH), required=True)
    display_name = fields.String(validate=validate.Length(max=MAX_DISPLAY_NAME_LENGTH, min=MIN_DISPLAY_NAME_LENGTH), required=True)
    bio = fields.String(validate=validate.Length(max=MAX_BIO_LENGTH), allow_none=True, load_default=None)
    email = fields.Email(required=True)
    password = fields.String(validate=password_validator_schemas, required=True)
    token = fields.String(validate=validate.Length(equal=TOKEN_LENGTH), required=True)
    flags = fields.Integer(strict=True, load_default=0)

class RelationshipType(IntEnum):
    """The type of relationship between two users.

    Attributes
    ----------
    FRIEND
        Friend relationship.
    FAVOURITE_FRIENT
        Friend marked as favorite.
    BLOCKED
        The recipient is blocked.
    """
    FRIEND = 1
    FAVORITE_FRIEND = 2
    BLOCKED = 3


class Relationship(Schema):
    """Represents a relationship between two users.

    Attributes
    ----------
    user_id: :class:`str`
        The ID of user that started the relationship.
    recipient_id: :class:`str`
        The ID of user with which relationship was started.
    type: :class:`RelationshipType`
        The type of relationship.
    """
    user_id = ULIDField(required=True)
    recipient_id = ULIDField(required=True)
    type = EnumField(RelationshipType, required=True)
