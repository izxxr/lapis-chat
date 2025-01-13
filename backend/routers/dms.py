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
from fastapi import APIRouter, Query
from core.deps import requires_auth_token
from core.typedefs import Request
from core.database import db_ctx
from core.models import messages

import datetime

__all__ = (
    "dms",
)

dms = APIRouter(prefix="/dms")

@dms.post("/{user_id}/messages", dependencies=[requires_auth_token()])
async def send_message(request: Request, user_id: str, body: messages.SendMessageJSON) -> messages.Message:
    """Send direct message to the given user."""
    db = db_ctx.get()
    return await db.send_direct_message(str(request.state.current_user.id), user_id, body)

@dms.get("/{user_id}/messages", dependencies=[requires_auth_token()])
async def get_messages(
    request: Request,
    user_id: str,
    _from: Annotated[datetime.datetime | None, Query(alias="from")] = None,
    to: Annotated[datetime.datetime | None, Query()] = None,
    limit: Annotated[int, Query(le=64)] = 16,
) -> list[messages.Message]:
    """Get direct messages from the DMs chat of the given user.

    Query Parameters:

    from: The starting datetime, in ISO format, from which point to get the messages.
    to: The ending datetime, in ISO format, till which point to get messages.
    limit: The number of messages to fetch. Defaults to 16 and capped at 64.
    """
    db = db_ctx.get()
    return await db.fetch_direct_messages(str(request.state.current_user.id), user_id, _from, to, limit)

@dms.patch("/{user_id}/{message_id}", dependencies=[requires_auth_token()])
async def edit_message(
    request: Request,
    user_id: str,
    message_id: str,
    body: messages.EditMessageJSON,
) -> messages.Message:
    """Edit a message."""
    db = db_ctx.get()
    return await db.edit_message(str(request.state.current_user.id), user_id, message_id, body)

@dms.delete("/{user_id}/{message_id}", dependencies=[requires_auth_token()])
async def delete_message(
    request: Request,
    user_id: str,
    message_id: str,
) -> None:
    """Deletes a message."""
    db = db_ctx.get()
    return await db.delete_message(str(request.state.current_user.id), user_id, message_id)
