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
    'fsstalker.core.celery.tasks.send_notification_task': {'queue': 'notify'},
    'fsstalker.core.celery.tasks.update_patreon_members': {'queue': 'enforce_tiers'},
    'fsstalker.core.celery.tasks.enforce_tier_limits': {'queue': 'enforce_tiers'}
}

beat_schedule = {
    'patreon-member-update': {
        'task': 'fsstalker.core.celery.tasks.update_patreon_members',
        'schedule': 60.0
    },
    'enforce-tier-limits': {
        'task': 'fsstalker.core.celery.tasks.enforce_tier_limits',
        'schedule': 60.0
    }
}

imports = 'fsstalker.core.celery.tasks'