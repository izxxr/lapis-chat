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

from tortoise.models import Model
from tortoise import fields, validators, exceptions
from enum import IntEnum
from models.validators import password_validator
from common.utils import generate_auth_token
from common.constants import (
    ULID_LENGTH,
    MAX_USERNAME_LENGTH,
    MAX_DISPLAY_NAME_LENGTH,
    MIN_DISPLAY_NAME_LENGTH,
    MIN_USERNAME_LENGTH,
    MAX_BIO_LENGTH,
    MAX_EMAIL_ADDRESS_LENGTH,
    MIN_EMAIL_ADDRESS_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_TOKEN_LENGTH,
)

__all__ = (
    'User',
    'Relationship',
    'RelationshipType',
)


class User(Model):
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
    id = fields.CharField(
        pk=True,
        max_length=ULID_LENGTH,
        validators=[validators.MinLengthValidator(ULID_LENGTH)],
    )
    username = fields.CharField(
        unique=True,
        max_length=MAX_USERNAME_LENGTH,
        validators=[validators.MinLengthValidator(MIN_USERNAME_LENGTH)],
    )
    display_name = fields.CharField(
        max_length=MAX_DISPLAY_NAME_LENGTH,
        validators=[validators.MinLengthValidator(MIN_DISPLAY_NAME_LENGTH)],
    )
    bio = fields.CharField(null=True, max_length=MAX_BIO_LENGTH, default=None)
    email = fields.CharField(
        unique=True,
        max_length=MAX_EMAIL_ADDRESS_LENGTH,
        validators=[validators.MinLengthValidator(MIN_EMAIL_ADDRESS_LENGTH)],
    )
    password = fields.CharField(
        max_length=MAX_PASSWORD_LENGTH,
        validators=[password_validator],
    )
    token = fields.CharField(unique=True, max_length=MAX_TOKEN_LENGTH, default=generate_auth_token)
    flags = fields.IntField(default=0)


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


class Relationship(Model):
    """Represents a relationship between two users.

    Attributes
    ----------
    user: :class:`User`
        The user that started the relationship.
    recipient: :class:`User`
        The user with which relationship was started.
    type: :class:`RelationshipType`
        The type of relationship.
    """
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField('models.User', related_name='users')
    recipient: fields.ForeignKeyRelation[User] = fields.ForeignKeyField('models.User', related_name='recipients')
    type = fields.IntEnumField(RelationshipType)

    def is_friend(self) -> bool:
        """Indicates whether the relationship is among friends."""
        return self.type in (RelationshipType.FRIEND, RelationshipType.FAVORITE_FRIEND)
