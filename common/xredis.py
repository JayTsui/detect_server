import time
import redis

handle = redis.Redis(host='localhost', port=6379)

# pool = redis.ConnectionPool(host='localhost', port=6379)

class XRedis(object):

    def add(self, key, obj):
        for k, v in obj.items():
            handle.hset(key, k, v)
    
    def get(self, key):
        obj = handle.hgetall(key)
        return obj


class XRedisLock(object):

    ACQUIRY_MILLIS = 100

    def __init__(self, key, timeout=60000, expires=10000):
        self.lock_key = key + '_lock'
        self.timeout = timeout
        self.expires = expires
        self.locked = False

    def lock(self):
        timeout = self.timeout
        while timeout > 0:
            expires = int(time.time()) + self.expires + 1
            if handle.setnx(self.lock_key, expires) == 1:
                self.locked = True
                return True
            current_value = handle.get(self.lock_key)
            if current_value and current_value < int(time.time()):
                old_value = handle.getset(self.lock_key, expires)
                if old_value and old_value == current_value:
                    self.locked = True
                    return True
            timeout -= self.ACQUIRY_MILLIS
            time.sleep(self.ACQUIRY_MILLIS)
        return False


    def unlock(self):
        handle.delete(self.lock_key)