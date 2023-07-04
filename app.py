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

from quart import Quart
from common import utils
from tortoise.contrib.quart import register_tortoise

__all__ = (
    'app',
)

app = Quart(__name__)

register_tortoise(
    app,
    db_url='sqlite://db.sqlite',
    modules={'models': ['models']},
    generate_schemas=True,
)

@app.route('/')
async def index():
    return {"message": "Welcome to Lapis API"}


if __name__ == '__main__':
    port = utils.get_env_var('LAPIS_PORT', 8000, integer=True)
    debug = utils.get_env_var('LAPIS_DEBUG', False, boolean=True)
    app.run(debug=debug, port=port)
