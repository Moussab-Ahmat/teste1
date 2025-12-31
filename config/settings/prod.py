from .base import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ALLOWED_HOSTS or ['*']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
