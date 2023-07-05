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

from typing import Optional, List, Dict, Any
from tortoise.models import Model
from tortoise import fields, validators, exceptions
from enum import IntEnum
from schemas.users import RelationshipType
from common.schemas_models import password_validator_models
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
    TOKEN_LENGTH,
)

__all__ = (
    'User',
    'Relationship',
)


class User(Model):
    """Represents a user entity.

    For details on attributes, see the documentation of `schemas.User`.
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
        validators=[password_validator_models],
    )
    token = fields.CharField(unique=True, max_length=TOKEN_LENGTH, default=generate_auth_token)
    flags = fields.IntField(default=0)

    def to_dict(
            self,
            *,
            exclude: Optional[List[str]] = None,
            exclude_sensitive: bool = True,
        ) -> Dict[str, Any]:
        """Serializes the model to dictionary.

        All values in dictionary wold have JSON serializable values. If
        exclude_sensitive is set to True (default), sensitive credentials
        are omitted from the output dictionary.
        """
        out = {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'bio': self.bio,
            'email': self.email,
            'password': self.password,
            'token': self.token,
            'flags': self.flags,
        }

        if exclude is None:
            exclude = []
        else:
            # In some cases, we might need the original list apart from
            # this to_dict method and since we might be updating the list
            # later, it is sensible to copy it instead to avoid messing with
            # the original list.
            exclude = exclude.copy()

        if exclude_sensitive:
            exclude.extend(['email', 'password', 'token'])

        for key in exclude:
            out.pop(key, None)

        return out


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

    def to_dict(
            self,
            *,
            exclude: Optional[List[str]] = None,
        ) -> Dict[str, Any]:
        """Serializes the user model to dictionary.

        All values in dictionary wold have JSON serializable values.
        """
        out = {
            'user_id': self.user.id,
            'recipient_id': self.recipient.id,
            'type': self.type.value,
        }

        if exclude:
            for key in exclude:
                out.pop(key, None)

        return out