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
from schemas.users import AuthorizedUser
from common.schemas_models import password_validator, dob_validator
from common.constants import (
    MAX_USERNAME_LENGTH,
    MIN_USERNAME_LENGTH,
    MAX_DISPLAY_NAME_LENGTH,
    MIN_DISPLAY_NAME_LENGTH,
)

__all__ = (
    'LoginQueryParams',
    'LoginResponse',
    'GetSelfResponse',
    'CreateUserJSON',
)


class LoginQueryParams(Schema):
    """Represents the query parameters for the GET /users/self/login route.

    email (string) : the email address of user.
    password (string) : the password of user.
    """
    email = fields.Email(required=True)
    password = fields.String(validate=password_validator, required=True)


LoginResponse = AuthorizedUser
"""The OK response of GET /users/self/login"""

GetSelfResponse = AuthorizedUser
"""The OK response of GET /users/self"""


class CreateUserJSON(Schema):
    """Represents the JSON body for the POST /users/self route.

    email (string) : the email address of user.
    password (string) : the password of user.
    username (string) : the username of user.
    display_name (string) : the display name of user.
    dob (string) : the date of birth of user in ISO format.
    """
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=password_validator)
    username = fields.String(required=True, validate=validate.Length(max=MAX_USERNAME_LENGTH, min=MIN_USERNAME_LENGTH))
    display_name = fields.String(required=True, validate=validate.Length(max=MAX_DISPLAY_NAME_LENGTH, min=MIN_DISPLAY_NAME_LENGTH))
    dob = fields.Date(required=True, validate=dob_validator)
