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

from typing import Dict, Any
from quart import Blueprint, request, g as state
from common.exceptions import HTTPException
from common.decorators import require_authorization
from common import utils

import models
import schemas

__all__ = (
    'users',
)

users = Blueprint('users', __name__, url_prefix='/users')
_self = Blueprint('self', __name__, url_prefix='/self')

users.register_blueprint(_self)

# TODO: Test these routes

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

    if await models.User.exists(email=json['email']):
        raise HTTPException(
            409,
            'This email is already registered by another account.',
            hint='Try logging in if you already have an account.',
            error_code=utils.get_error_code('EMAIL_REGISTERED'),
        )
    
    if await models.User.exists(username=json['username']):
        raise HTTPException(
            409,
            'This username is taken.',
            error_code=utils.get_error_code('USERNAME_TAKEN'),
        )

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
