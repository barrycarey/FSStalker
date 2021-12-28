from fsstalker.core.config import Config

config = Config()

broker_url = config.redis_url
result_backend = broker_url
task_serializer = 'pickle'
result_serializer='pickle'
accept_content = ['pickle', 'json']
result_expires = 60
task_routes = {
    'fsstalker.core.celery.tasks.load_subreddit_task': {'queue': 'load_subreddits'},
    'fsstalker.core.celery.tasks.process_submissions_task': {'queue': 'check_posts'},
    'fsstalker.core.celery.tasks.send_notification_task': {'queue': 'notify'}
}

imports = 'fsstalker.core.celery.tasks'