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

import dotenv
import os

__all__ = (
    "Config",
)

_default_missing: Any = object()

dotenv.load_dotenv()


class Config:
    """The application's configuration."""

    _allowed_true_values = {"true", "1"}
    _allowed_false_values = {"false", "0"}

    @staticmethod
    def _bool_converter(value: str, key: str) -> bool:
        if value in Config._allowed_true_values:
            return True
        elif value in Config._allowed_false_values:
            return False
        else:
            raise ValueError(f"Value for {key!r} must be a boolean (true/false/1/0), found {value!r}")

    @staticmethod
    def _get_from_env(key: str, default: Any = _default_missing, convert_bool: bool = False) -> Any:
        try:
            value = os.environ[key]
        except KeyError:
            if default is not _default_missing:
                return default
            raise ValueError(f"{key} environment variable is not set.")
        else:
            return Config._bool_converter(value, key) if convert_bool else value

    MONGODB_URI = _get_from_env("MONGODB_DATABASE_URI")
    """The URI for MongoDB connection."""

    MONGODB_DATABASE_NAME = _get_from_env("MONGODB_DATABASE_NAME", "production")
    """The name of database to use."""

    REDIS_URI = _get_from_env("REDIS_URI")
    """The URI for Redis connection."""
