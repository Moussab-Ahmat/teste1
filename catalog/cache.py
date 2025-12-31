import json
from typing import Any

from django.core.serializers.json import DjangoJSONEncoder
from django_redis import get_redis_connection

CACHE_PREFIX = 'catalog:products:'
CACHE_TIMEOUT = 60 * 15


def _build_cache_key(params: dict[str, Any]) -> str:
    parts = [f"{key}={value}" for key, value in sorted(params.items())]
    return CACHE_PREFIX + ':'.join(parts or ['default'])


def get_cached_products(params: dict[str, Any]):
    cache_key = _build_cache_key(params)
    conn = get_redis_connection()
    cached = conn.get(cache_key)
    if cached:
        return json.loads(cached)
    return None


def set_cached_products(params: dict[str, Any], payload: Any):
    cache_key = _build_cache_key(params)
    conn = get_redis_connection()
    conn.setex(cache_key, CACHE_TIMEOUT, json.dumps(payload, cls=DjangoJSONEncoder))


def invalidate_products_cache():
    conn = get_redis_connection()
    for key in conn.scan_iter(match=f"{CACHE_PREFIX}*"):
        conn.delete(key)
