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

from typing import TYPE_CHECKING, Dict, Any
from tortoise.models import Model
from tortoise import fields, validators
from common.constants import UUID4_LENGTH, SESSION_TIMEOUT_DAYS, TOKEN_LENGTH
from common.utils import generate_auth_token

import uuid
import datetime

if TYPE_CHECKING:
    from models.users import User


__all__ = (
    'Session',
)


class Session(Model):
    """Stores information about a user login session.

    For more information on session object, see the `schemas.Session`
    object documentation.
    """
    id = fields.CharField(
        pk=True,
        max_length=UUID4_LENGTH,
        validators=[validators.MinLengthValidator(UUID4_LENGTH)],
        default=lambda: str(uuid.uuid4()),
    )
    token = fields.CharField(
        unique=True,
        max_length=TOKEN_LENGTH,
        default=generate_auth_token,
        validators=[validators.MinLengthValidator(TOKEN_LENGTH)],
    )
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField('models.User', 'session_users')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    async def ensure_active(self) -> bool:
        """Ensures the session is active.

        This method deletes the session if it is not active. Returns
        True if active.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        active = True

        if (now - self.updated_at).days >= SESSION_TIMEOUT_DAYS:
            active = False
        if not active:
            await self.delete()

        return active

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'token': self.token,
            'user_id': self.user_id,  # type: ignore
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
