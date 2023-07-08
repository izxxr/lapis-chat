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

from quart import Blueprint, g as state
from common.constants import MAX_SESSIONS
from common.decorators import require_authorization
from common.exceptions import HTTPException

import models

__all__ = (
    'sessions',
)

sessions = Blueprint('sessions', __name__, url_prefix='/sessions')


@sessions.get('/<session_token>')
async def get_session(session_token: str):
    """Get a session by its token."""
    session = await models.Session.filter(token=session_token).first()
    if not session:
        raise HTTPException(404, 'Session not found')

    active = await session.ensure_active()
    if not active:
        raise HTTPException(404, 'Session has expired.', error_code='SESSION_EXPIRED')

    return session.to_dict()

@sessions.delete('/<session_token>')
async def delete_session(session_token: str):
    """Deletes a session by its token."""
    session = await models.Session.filter(token=session_token).first()
    if not session:
        raise HTTPException(404, 'Session not found')

    await session.delete()
    return ('', 204)

@sessions.post('/')
@require_authorization()
async def create_session():
    """Creates a session and returns it."""
    if len(await models.Session.filter(user=state.user)) >= MAX_SESSIONS:
        raise HTTPException(
            400,
            f'Only {MAX_SESSIONS} sessions are allowed at a time.',
            error_code='SESSIONS_LIMIT_REACHED',
        )

    session = await models.Session.create(user=state.user)
    return session.to_dict()
