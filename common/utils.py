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

from typing import Any, Optional, Union, TYPE_CHECKING
from tortoise.fields import Field
from common.constants import ERROR_CODES

import os
import base64
import uuid
import datetime
import ulid

if TYPE_CHECKING:
    from tortoise.models import Model

__all__ = (
    'get_env_var',
    'get_ulid',
    'get_ulid_id',
    'generate_auth_token',
)

_MISSING: Any = object()

def get_env_var(
        key: str,
        default: Any = _MISSING,
        /,
        *,
        boolean: bool = False,
        integer: bool = False,
    ) -> Any:
    """Returns the environment variable value for given key.

    If no default is provided, a KeyError is raised if variable doesn't
    exist. `boolean` and `integer` parameters can be used to get the
    type casted value as return value.
    """
    try:
        value = os.environ[key]
    except KeyError:
        if default is not _MISSING:
            return default
        raise

    if boolean:
        value = value.lower()
        return value in ('true', '1')
    if integer:
        try:
            return int(value)
        except ValueError:
            raise ValueError(f'value for key {key!r} must be an integer') from None

    return value


def get_ulid(id: Optional[str] = None, /, *, time: Optional[Union[int, float, datetime.datetime]] = None) -> ulid.ULID:
    """Creates a ULID instance.
    
    If both id and time parameters are omitted, a ULID for the current time is
    generated and returned. If an ID string is provided, it's ULID counterpart
    is returned.

    time parameter can be an int, float (epoch timestamp) or datetime instance.
    Both parameters are mutually exclusive and id takes priority.
    """
    if id is not None:
        return ulid.ULID.from_str(id)
    if time is not None:
        if isinstance(time, (int, float)):
            return ulid.ULID.from_timestamp(time)
        if isinstance(time, datetime.datetime):
            return ulid.ULID.from_datetime(time)
        else:
            raise TypeError('time must be an int, float or datetime.datetime instance.')

    # id and time not provided
    return ulid.ULID()


def get_ulid_id(time: Optional[Union[int, float, datetime.datetime]] = None) -> str:
    """A syntactic sugar for getting the ULID string.

    This is a simple shorthand to `str(utils.get_ulid())`. Similar to
    `get_ulid()`, this method takes an optional `time` parameter.
    """
    return str(get_ulid(time=time))


def generate_auth_token() -> str:
    """Generates an authorization token."""
    randomness = str(uuid.uuid4()).encode()
    return base64.b64encode(randomness).decode()


def get_error_code(name: str, default: str = 'UNSPECIFIED_ERROR') -> int:
    """Gets error code for given error."""
    code = ERROR_CODES.get(name)
    if code is None:
        code = ERROR_CODES.get(default, -1)
    return code
