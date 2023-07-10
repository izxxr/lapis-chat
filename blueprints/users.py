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

from typing import Dict, Any, Optional
from tortoise.expressions import Q
from quart import Blueprint, request, g as state
from common.exceptions import HTTPException, ValidationError
from common.decorators import require_authorization

import models
import schemas

__all__ = (
    'users',
)

users = Blueprint('users', __name__, url_prefix='/users')
_self = Blueprint('self', __name__, url_prefix='/self')

users.register_blueprint(_self)

async def ensure_no_conflict(
        email: Optional[str] = None,
        username: Optional[str] = None,
        user: Optional[models.User] = None,
        **kwargs: Any,
    ) -> bool:
    
    error = None
    error_code = None
    filters = [~Q(id=user.id)] if user else []

    if email and await models.User.exists(*filters, email=email):
        error = 'This email is already registered.'
        error_code = 'EMAIL_ALREADY_REGISTERED'
    if username and await models.User.exists(*filters, username=username):
        error = 'This username is taken.'
        error_code = 'USERNAME_TAKEN'

    if error and error_code:
        raise HTTPException(409, error, error_code=error_code, **kwargs)

    return True


@_self.get('/login')
async def login():
    """Login and get details about the current user.

    Query Parameters
    ----------------
    email: string
        The user's email address.
    password: string
        The user's password.

    Returns
    -------
    200: User object
    400: Invalid query parameters
    401: Invalid email or password
    """
    schema = schemas.LoginQueryParams()
    params: Dict[str, Any] = schema.load(dict(request.args))  # type: ignore

    user = await models.User.filter(email=params['email'], password=params['password']).first()

    if user is None:
        raise HTTPException(401, 'Invalid email or password.')

    return user.to_dict(exclude_sensitive=False)


@_self.get('/')
@require_authorization()
async def get_self():
    """Get details about the current user.

    Returns user object on success.
    """
    return state.user.to_dict(exclude_sensitive=False)


@_self.post('/')
async def create_user():
    """Create a user account.

    Returns 201 Created on success.
    """
    schema = schemas.CreateUserJSON()
    data = await request.get_json(silent=True) or {}
    json: Dict[str, Any] = schema.load(data)  # type: ignore

    await ensure_no_conflict(json['email'], json['username'])
    await models.User.create(
        email=json['email'],
        password=json['password'],
        username=json['username'],
        display_name=json['display_name'],
        dob=json['dob'],
    )
    return ('', 201)


@_self.delete('/')
@require_authorization()
async def delete_self():
    """Delete the user account.

    Returns 204 No Content on success.
    """
    await state.user.delete()
    return ('', 204)


@_self.patch('/')
@require_authorization()
async def edit_self():
    """Edits the current user's account.

    Returns updated user on success.
    """
    user: models.User = state.user
    schema = schemas.EditSelfJSON()
    data = await request.get_json(silent=True) or {}
    json: Dict[str, Any] = schema.load(data)  # type: ignore

    # Validate old_password
    if json.get('password'):
        old_password = json.get('old_password')
        if not old_password:
            raise ValidationError({'old_password': 'This field is required when passing password'})
        if user.password != old_password:
            raise ValidationError('Invalid old password', error_code='INVALID_OLD_PASSWORD')

    await ensure_no_conflict(json.get('email'), json.get('username'), user)

    user.update_from_dict(json)
    await user.save()

    return user.to_dict()
