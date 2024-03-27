#!/usr/bin/env python3
"""Writing, Reading, Incrementing values to Redis"""
import uuid
import redis
from typing import Optional, Callable, Union
from functools import wraps


def call_history(method: Callable) -> Callable:
    """decorator function to recode parameter & output history"""
    key = method.__qualname__
    inputs = key + ":inputs"
    outputs = key + ":outputs"

    @wraps(method)
    def wrapper(self, *args, **kwds):
        """wrapped function"""
        self._redis.rpush(inputs, str(args))
        data = method(self, *args, **kwds)
        self._redis.rpush(outputs, str(data))
        return data
    return wrapper


def count_calls(method: Callable) -> Callable:
    """decorator function"""
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwds):
        """method wrapper"""
        self._redis.incr(key)
        return method(self, *args, **kwds)

    return wrapper


class Cache:
    """Cache class representation"""

    def __init__(self) -> None:
        """Initialize redis instance"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """takes data arg, generates random key,
        store data in redis with random key"""
        random_key = str(uuid.uuid4())
        self._redis.set(random_key, data)
        return random_key

    def get(self, key: str,
            fn:  Optional[Callable] = None) -> Union[str, bytes, int, float]:
        """takes key and convert data back to desired format"""
        result = self._redis.get(key)
        if fn:
            return fn(result)
        return result

    def get_str(self, result: bytes) -> str:
        """convert result to string"""
        return str(result, 'UTF-8')

    def get_int(self, result: bytes) -> int:
        """convert result to int"""
        return int.from_bytes(result, "big")


def replay(method: Callable) -> None:
    """ display the history of calls for a function """
    key = method.__qualname__
    inputs = key + ":inputs"
    outputs = key + ":outputs"
    redis = method.__self__._redis
    count = redis.get(key).decode("utf-8")
    print("{} was called {} times:".format(key, count))
    inputList = redis.lrange(inputs, 0, -1)
    outputList = redis.lrange(outputs, 0, -1)
    redis_all = list(zip(inputList, outputList))

    for a, b in redis_all:
        attr, data = a.decode("utf-8"), b.decode("utf-8")
        print("{}(*{}) -> {}".format(key, attr, data))
