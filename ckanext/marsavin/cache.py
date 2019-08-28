from ckan.lib.redis import connect_to_redis
from ckan.plugins.toolkit import config
from functools import wraps
import json


def cacheable(cacheable_func, **cacheable_kwargs):
    @wraps(cacheable_func)
    def cacheable_wrapper(*args, **kwargs):
        expiry = cacheable_kwargs.get("expiry", 100)
        site_id = config.get("ckan.site_id", "default")
        cache_key = cacheable_kwargs.get("key", "CACHE:" + site_id + "::" +
                                         cacheable_func.__name__)
        conn = connect_to_redis()
        if conn.exists(cache_key):
            return json.loads(conn.get(cache_key))

        value = cacheable_func(*args, **kwargs)
        conn.setex(cache_key, json.dumps(value), expiry)
        return value

    return cacheable_wrapper
