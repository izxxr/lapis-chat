# MIT License

# Copyright (c) 2025 lapis-chat

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

from typing import Annotated
from fastapi import Depends, Header
from core.typedefs import Request
from core.database import db_ctx
from core import errcodes

__all__ = (
    "requires_auth_token",
)


async def _requires_auth_token_dep(request: Request, authorization: Annotated[str, Header()]):
    db = db_ctx.get()
    user = await db.fetch_user_authorized(authorization)

    if user is None:
        raise errcodes.INVALID_AUTHORIZATION.http_exc()

    request.state.current_user = user


def requires_auth_token():
    return Depends(_requires_auth_token_dep)
