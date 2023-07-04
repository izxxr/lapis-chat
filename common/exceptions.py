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

from typing import Optional, Dict, Any

__all__ = (
    'HTTPException',
)


class HTTPException(Exception):
    """Base class for all HTTP exceptions.
    
    These exceptions are properly handled and propagated as reponse when
    raised in a request view context.
    
    Attributes
    ----------
    status_code: :class:`int`
        The HTTP status code.
    message: :class:`str`
        The error message.
    hint: Optional[:class:`str`]
        The optional hint, if any.
    """
    def __init__(self, status_code: int, message: str, hint: Optional[str] = None) -> None:
        self.status_code = status_code
        self.message = message
        self.hint = hint

        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Returns the dictionary for the exception."""
        ret = {
            "error": True,
            "message": self.message
        }

        if self.hint is not None:
            ret["hint"] = self.hint

        return ret
