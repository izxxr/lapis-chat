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
from pydantic import BaseModel

import json


__all__ = (
    "BaseDatabaseModel",
)


class BaseDatabaseModel(BaseModel):
    """The base class for all database models."""

    def model_dump_database(self, **kwargs: Any) -> dict[str, Any]:
        """Returns database compatible serialized model.

        This by default passes by_alias to the serialization method. Any other
        keyword arguments to this method (including by_alias for overriding) are
        passed to model_dump_json().
        """
        by_alias = kwargs.pop("by_alias", True)
        return json.loads(self.model_dump_json(by_alias=by_alias, **kwargs))

    def model_dump_api(self, **kwargs: Any) -> dict[str, Any]:
        """Returns HTTP API compatible serialized model.

        By default, this is equivalent to model_dump_database() but could be
        overriden to implement another behaviour.

        Note that unlike model_dump_database(), this method does not pass
        by_alias as True by default.
        """
        by_alias = kwargs.pop("by_alias", False)
        return self.model_dump_database(by_alias=by_alias, **kwargs)
