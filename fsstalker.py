import time

from redis import Redis

from fsstalker.core.celery.tasks import load_subreddit_task
from fsstalker.core.config import Config
from fsstalker.core.db.unit_of_work_manager import UnitOfWorkManager
from fsstalker.core.logging import log
from fsstalker.core.util.helpers import get_db_engine


config = Config()
uowm = UnitOfWorkManager(get_db_engine(config))

redis = Redis(
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_database,
        password=config.redis_password
    )


while True:
    if len(redis.lrange('load_subreddits', 0, 20000)) > 0 or len(redis.lrange('check_posts', 0, 20000)) > 0:
        log.info('Redis queue still has incomplete tasks')
        time.sleep(5)
        continue
    with uowm.start() as uow:
        subreddits = uow.watch.get_distinct_subreddits()
        for sub in subreddits:
            log.debug('Adding %s to queue', sub.subreddit)
            load_subreddit_task.apply_async((sub.subreddit,), queue='load_subreddits')
    time.sleep(60)