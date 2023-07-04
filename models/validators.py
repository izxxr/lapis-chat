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

from tortoise import exceptions
from common.constants import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH

import string

__all__ = (
    'password_validator',
)

def password_validator(value: str) -> bool:
    """A validator that ensures the strongness of a password.

    Conditions for a password to be valid:

    - Has at least 8 characters and at max, 200 characters.
    - Must contain at least one number.
    - Must contain at least one letter.
    """
    error = None
    if len(value) < MIN_PASSWORD_LENGTH:
        error = f'Password length must be at least {MIN_PASSWORD_LENGTH} characters.'
    elif len(value) > MAX_PASSWORD_LENGTH:
        error = f'Password lenght must be less than {MAX_PASSWORD_LENGTH} characters.'
    else:
        letters = set(string.ascii_letters)
        digits = set(string.digits)

        if not letters.intersection(value) or not digits.intersection(value):
            error = 'Password must contain at least one letter and one digit.'

    if error:
        raise exceptions.ValidationError(error)

    return True
