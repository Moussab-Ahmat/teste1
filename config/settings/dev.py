from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ALLOWED_HOSTS or ['localhost', '127.0.0.1']
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
