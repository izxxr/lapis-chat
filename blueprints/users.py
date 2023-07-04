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

from quart import Blueprint, request, g as state
from common.exceptions import HTTPException
from common.decorators import require_authorization
from models.users import User

__all__ = (
    'users',
)

users = Blueprint('users', __name__, url_prefix='/users')
_self = Blueprint('self', __name__, url_prefix='/self')

users.register_blueprint(_self)

# TODO: Use a schema library (preferably marshmallow) to validate 
# incoming data such as JSON body
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
    400: Missing required query parameters
    401: Invalid email or password
    """
    email = request.args.get('email')
    password = request.args.get('password')

    if not email or not password:
        raise HTTPException(400, 'Both "email" and "password" query parameters are required.')

    user = await User.filter(email=email.lower(), password=password).first()

    if user is None:
        raise HTTPException(401, 'Invalid email or password.')

    return user.to_dict()


@_self.get('/')
@require_authorization()
async def get_self():
    """Get details about the current user.

    Returns user object on success.
    """
    return state.user
