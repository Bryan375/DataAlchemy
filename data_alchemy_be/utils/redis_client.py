import redis

from data_alchemy_be.settings import CELERY_BROKER_URL
from utils.singleton import SingletonMeta


class RedisClient(metaclass=SingletonMeta):

    def __init__(self) -> None:
        self.redis = redis.Redis.from_url(CELERY_BROKER_URL)

    def get(self, key: str) -> str:
        return self.redis.get(key)