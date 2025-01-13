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
from fastapi import APIRouter, WebSocket, WebSocketException, Query
from core.websocket import WSClient
from core.database import db_ctx
from core import codes

__all__ = (
    "ws",
)

ws = APIRouter(prefix="/websocket")


# TODO: token is passed as query parameter for testing purposes only temporarily
# Proper authentication flow after initial connection will/must be implemented later.
@ws.websocket("/")
async def websocket_route(websocket: WebSocket, token: Annotated[str, Query()]):
    """Connect to Lapis chat WebSocket server."""
    db = db_ctx.get()
    user = await db.fetch_user_authorized(token)

    if user is None:
        raise WebSocketException(codes.INVALID_AUTHORIZATION.error_code, "Invalid authorization token")

    ws = WSClient(websocket, db, user)
    await ws.start()
