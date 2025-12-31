import os
import fakeredis
from django_redis.pool import ConnectionFactory

_fake_server = fakeredis.FakeServer()


class FakeConnectionFactory(ConnectionFactory):
    """Connection factory that returns fakeredis connections for testing."""

    def get_connection(self, params):
        return fakeredis.FakeConnection(server=_fake_server)


def get_fake_connection_factory(_name=None):
    return FakeConnectionFactory
