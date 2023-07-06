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


# User
MAX_DISPLAY_NAME_LENGTH = 50
MIN_DISPLAY_NAME_LENGTH = 1
MAX_USERNAME_LENGTH = 36
MIN_USERNAME_LENGTH = 3
MAX_BIO_LENGTH = 200
MAX_EMAIL_ADDRESS_LENGTH = 320
MIN_EMAIL_ADDRESS_LENGTH = 3
MAX_PASSWORD_LENGTH = 200
MIN_PASSWORD_LENGTH = 8
TOKEN_LENGTH = 48
MIN_ALLOWED_AGE = 13

# Internal Constants
ULID_LENGTH = 26

# Error codes
ERROR_CODES = {
    # Unspecified (-1)
    'UNSPECIFIED_ERROR': -1,
    
    # Generic (1000-1999)
    'VALIDATION_ERROR': 1000,
    
    # User Account (2000-2999)
    'UNDERAGE': 2000,
    'USERNAME_TAKEN': 2001,
    'EMAIL_ALREADY_REGISTERED': 2002,
    'PASSWORD_INVALID': 2003,
    'INVALID_OLD_PASSWORD': 2004,
}

ERROR_NAMES = {
    code: name
    for name, code in ERROR_CODES.items()
}

ERROR_HINTS = {
    'EMAIL_ALREADY_REGISTERED': 'If you already have an account, try logging in instead.',
    'USERNAME_TAKEN': 'Try a different username or modify the current one to get a unique username.',
}
