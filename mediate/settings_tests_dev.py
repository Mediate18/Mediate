from .settings_dev import *

import sys

TESTING = 'test' in sys.argv

if TESTING:
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]