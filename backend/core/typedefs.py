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

# This file is used for type checking purposes only.
# At runtime, Request from this module is simply equivalent to fastapi.Request
# but for type checkers, the Request class is defined as subclass of fastapi.Request
# with type hinted state.

from __future__ import annotations

from typing import TYPE_CHECKING
from fastapi import Request as FastAPIRequest

if TYPE_CHECKING:
    from fastapi.datastructures import State
    from core.models import users

    class TypedState(State):
        current_user: users.AuthorizedUser

    class Request(FastAPIRequest):
        @property
        def state(self) -> TypedState:
            ...
else:
    Request = FastAPIRequest

__all__ = (
    "Request",
)
