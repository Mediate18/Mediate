from .settings import *

import sys

TESTING = 'test' in sys.argv

if TESTING:
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]

MIDDLEWARE = [middelware for middelware in MIDDLEWARE if middelware != 'mediate.middleware.OldHostNameWarningMiddleware']