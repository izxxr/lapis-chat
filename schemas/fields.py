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

from typing import TYPE_CHECKING, Any, Type
from marshmallow import fields, validate, ValidationError
from common.constants import ULID_LENGTH
from enum import Enum, IntEnum

__all__ = (
    'ULIDField',
    'EnumField',
)


class ULIDField(fields.String):
    """Represents a ULID field."""
    def __init__(self, *, required: bool = False) -> None:
        kwargs = {}
        if not required:
            kwargs.setdefault('load_default', None)

        super().__init__(
            required=required,
            validate=validate.Length(equal=ULID_LENGTH),
            **kwargs,
        )


class EnumField(fields.Field):
    """Enum field with support for IntEnum subclasses."""
    # Credits: https://github.com/marshmallow-code/marshmallow/issues/267#issuecomment-420154612
    def __init__(self, enum_type: Type[Enum], *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self._enum_type = enum_type

    def _serialize(self, value: Enum, attr: str, obj: Any, **kwargs: Any):
        if value is not None:
            return value.value

    def _deserialize(self, value: Any, attr: str, data: Any, **kwargs: Any):
        if issubclass(self._enum_type, IntEnum):
            if not isinstance(value, int):
                raise ValidationError('Value must be an integer')
            else:
                return self._enum_type(value)
        else:
            return self._enum_type(value)
