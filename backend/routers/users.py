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

from fastapi import APIRouter
from core.typedefs import Request
from core.deps import requires_auth_token
from core.models import users as users_models
from core.database import db_ctx
from core import codes

__all__ = (
    "users",
)

users = APIRouter(prefix="/users")


@users.get("/authorized")
async def get_authorized_user(data: users_models.GetAuthorizedUserJSONT) -> users_models.AuthorizedUser:
    """Get the authorized user details."""
    db = db_ctx.get()
    if isinstance(data, users_models.GetAuthorizedUserCredsJSON):
        user = await db.fetch_user_credentials(data.username, data.password)
    else:
        user = await db.fetch_user_authorized(data.token)

    if user is None:
        raise codes.INVALID_AUTHORIZATION.http_exc()

    return user

@users.delete("/authorized", dependencies=[requires_auth_token()])
async def delete_authorized_user(request: Request) -> None:
    """Deletes the authorized user account."""
    db = db_ctx.get()
    await db.delete_user(str(request.state.current_user.id))

@users.patch("/authorized", dependencies=[requires_auth_token()])
async def edit_authorized_user(request: Request, data: users_models.EditAuthorizedUserJSON) -> users_models.AuthorizedUser:
    """Edit the authorized user data."""
    db = db_ctx.get()
    return await db.edit_user(str(request.state.current_user.id), data)

@users.post("/")
async def create_user(data: users_models.CreateUserJSON) -> users_models.AuthorizedUser:
    """Get information about a user."""
    db = db_ctx.get()
    return await db.create_user(data)

@users.get("/{user_id}", dependencies=[requires_auth_token()])
async def get_user(user_id: str) -> users_models.User:
    """Get information about a user."""
    db = db_ctx.get()
    user = await db.fetch_user(user_id, authorized=False)

    if user is None:
        raise codes.ENTITY_NOT_FOUND.http_exc("User not found.")

    return user
