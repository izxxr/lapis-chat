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

from typing import Optional, Dict, Any, Union, List
from tortoise.exceptions import ValidationError as DBValidationError
from marshmallow import ValidationError as SchemaValidationError
from common.constants import ERROR_HINTS, ERROR_NAMES
from common import utils

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
    def __init__(
            self,
            status_code: int,
            message: Union[str, bytes, List[Any], Dict[str, Any]],
            hint: Optional[str] = None,
            error_code: Union[int, str] = -1,
        ) -> None:

        if isinstance(error_code, str):
            error_code = utils.get_error_code(error_code)

        if hint is None:
            code = ERROR_NAMES.get(error_code)
            if code:
                self.hint = ERROR_HINTS.get(code)

        self.status_code = status_code
        self.messages = [message] if isinstance(message, str) else message
        self.hint = hint
        self.error_code = error_code

        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Returns the dictionary for the exception."""
        ret: Dict[str, Any] = {
            'error': True,
            'error_code': self.error_code,
            'messages': self.messages,
        }

        if self.hint is not None:
            ret.setdefault('hint', self.hint)

        return ret


class ValidationError(HTTPException):
    def __init__(
            self,
            message: Union[str, bytes, List[Any], Dict[str, Any]],
            *,
            status_code: int = 400,
            error_code: Union[int, str] = 1000,
            hint: Optional[str] = None,
        ):

        super().__init__(message=message, status_code=status_code, hint=hint, error_code=error_code)

    @classmethod
    def from_external_exc(cls, exc: Union[DBValidationError, SchemaValidationError]) -> ValidationError:
        """Constructs ValidationError instance from external exception instances.

        External exception instances mean ValidationError counterparts from
        the tortoise ORM and marshmallow library.
        """
        if isinstance(exc, SchemaValidationError):
            error_code = exc.kwargs.get('error_code', utils.get_error_code('VALIDATION_ERROR'))
            hint = exc.kwargs.get('hint')
            message = exc.messages
        else:
            error_code = utils.get_error_code('VALIDATION_ERROR')
            hint = None
            message = str(exc)

        return cls(message, error_code=error_code, hint=hint)
