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

from typing import Callable, Any
from functools import wraps
from quart import request, g as state
from common.exceptions import HTTPException
from models.users import User

__all__ = (
    'require_authorization',
)


def require_authorization() -> Callable[[Callable[..., Any]], Any]:
    """Ensures that only authorized requests can access a route.

    When `token_only` is True (default), only `Bearer` token requests
    are accepted and vice versa.
    """
    def predicate(view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        async def __decorator(*args: Any, **kwargs: Any):
            header = request.headers.get('Authorization')
            if header is None:
                raise HTTPException(401, 'Unauthorized')

            scheme, _, value = header.partition(' ')
            if scheme.lower() == 'bearer':
                user = await User.filter(token=value.strip()).first()
                if user:
                    state.user = user
                else:
                    raise HTTPException(401, 'Invalid authorization token')
            else:
                raise HTTPException(401, 'Authorization scheme must be Bearer')

        return __decorator

    return predicate