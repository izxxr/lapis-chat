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

from typing import Any
from fastapi import APIRouter
from core.typedefs import Request
from core.deps import requires_auth_token
from core.database import db_ctx

__all__ = (
    "friends",
)

friends = APIRouter(prefix="/friends")

# The format exposed by API for Friend/FriendRequest is not same as
# how these objects are stored in database hence the default model_dump()
# cannot be used in this case. This is why model_dump_api() has to be
# called manually in responses for some routes below.
#
# TODO: Perhaps there's a better and possibly faster approach to
# achieve this behaviour. To tackle performance issues, pagination
# could be implemented for routes that return bulk of these objects
# and maximum number of objects per page could be capped.

@friends.get("/requests", dependencies=[requires_auth_token()])
async def get_friend_requests(request: Request) -> list[dict[str, Any]]:
    """Get all incoming and outgoing friends requests."""
    db = db_ctx.get()
    result = await db.fetch_all_friend_requests(str(request.state.current_user.id))
    return [r.model_dump_api() for r in result]

@friends.post("/requests/{user_id}", dependencies=[requires_auth_token()])
async def send_accept_friend_request(request: Request, user_id: str) -> dict[str, Any]:
    """Send or accept a friend request."""
    db = db_ctx.get()
    result = await db.send_accept_friend_request(str(request.state.current_user.id), user_id)
    return {"operation": "REQUEST_SENT" if result else "REQUEST_ACCEPTED"}

@friends.delete("/requests/{user_id}", dependencies=[requires_auth_token()])
async def withdraw_reject_friend_request(request: Request, user_id: str) -> dict[str, Any]:
    """Withdraw or reject a friend request."""
    db = db_ctx.get()
    result = await db.withdraw_reject_friend_request(str(request.state.current_user.id), user_id)
    return {"operation": "REQUEST_WITHDRAWN" if result else "REQUEST_REJECTED"}

@friends.get("/", dependencies=[requires_auth_token()])
async def get_friends(request: Request) -> list[dict[str, Any]]:
    """Get all friends of the user."""
    db = db_ctx.get()
    result = await db.fetch_all_friends(str(request.state.current_user.id))
    
    return [r.model_dump_api() for r in result]

@friends.delete("/{user_id}", dependencies=[requires_auth_token()])
async def unfriend_user(request: Request, user_id: str) -> None:
    """Unfriends a user."""
    db = db_ctx.get()
    await db.unfriend_user(str(request.state.current_user.id), user_id)
