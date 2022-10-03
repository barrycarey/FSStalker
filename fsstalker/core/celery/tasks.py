import json
from datetime import datetime
from typing import Text, NoReturn, List

import requests
from apprise import Apprise
from celery import Task
from praw.models import Submission

from fsstalker.core.celery.app import celery
from fsstalker.core.config import Config
from fsstalker.core.db.db_models import SentNotification, CheckedPost
from fsstalker.core.db.unit_of_work_manager import UnitOfWorkManager
from fsstalker.core.logging import log
from fsstalker.core.util.helpers import get_db_engine, get_reddit_instance, post_includes_words
from fsstalker.core.util.task_helpers import load_subreddit_submissions, check_watches, patreon_member_update, \
    update_watch_limits


class FsStalkerTask(Task):
    def __init__(self):
        self.config = Config()
        self.uowm = UnitOfWorkManager(get_db_engine(self.config))
        self.reddit = get_reddit_instance(self.config)

@celery.task(bind=True, base=FsStalkerTask)
def load_subreddit_task(self, subreddit: Text) -> NoReturn:
    submissions = load_subreddit_submissions(self.uowm, self.reddit, subreddit)
    if submissions:
        log.info('Queuing %s submissions for checking', len(submissions))
        process_submissions_task.apply_async((submissions,))

@celery.task(bind=True, base=FsStalkerTask)
def process_submissions_task(self, submissions: List[Submission]) -> NoReturn:
    results = check_watches(self.uowm, submissions)
    with self.uowm.start() as uow:
        for result in results:
            user = uow.user.get_by_id(result['owner_id'])
            log.info('Queue notification for watch %s for word %s with %s second delay', result['watch_id'], result['match_word'], user.patreon_tier.notify_delay)
            send_notification_task.apply_async((result['watch_id'], result['match_word'], result['submission']), countdown=user.patreon_tier.notify_delay)

@celery.task(bind=True, base=FsStalkerTask)
def send_notification_task(self, watch_id: int, match: Text, submission: Submission) -> NoReturn:
    log.info('Sending notification for watch %s for word %s', watch_id, match)
    apprise = Apprise()
    with self.uowm.start() as uow:
        watch = uow.watch.get_by_id(watch_id)
        if not watch:
            log.error('No watch found with ID %s', watch_id)
            return
        for notify_svc in watch.notification_services:
            apprise.add(notify_svc.url)
        submission_created = datetime.utcfromtimestamp(submission.created_utc)
        delta = datetime.utcnow() - submission_created
        apprise.notify(f'Found a match for word {match} in subreddit r/{submission.subreddit.display_name}. https://redd.it/{submission.id} \n\nNotification Delay: {delta.seconds} seconds', f'Watch {watch.name} Alert!')
        uow.sent_notification.add(
            SentNotification(
                triggered_post=submission.id,
                watch=watch,
                triggered_word=match,
                submission_created_at=datetime.utcfromtimestamp(submission.created_utc)
            )
        )
        try:
            uow.commit()
        except Exception as e:
            log.exception()

@celery.task(bind=True, base=FsStalkerTask)
def update_patreon_members(self) -> NoReturn:
    res = requests.get(
        'https://www.patreon.com/api/oauth2/v2/campaigns/9343789/members?include=currently_entitled_tiers,user&fields%5Bmember%5D=patron_status',
        headers={'Authorization': f'Bearer {self.config.patreon_auth_token}'},
        timeout=15
    )

    if res.status_code != 200:
        log.error('Bad status code when fetching Patreon member data')
        return

    member_data = json.loads(res.text)
    patreon_member_update(member_data, self.uowm)

@celery.task(bind=True, base=FsStalkerTask)
def enforce_tier_limits(self) -> NoReturn:
    update_watch_limits(self.uowm)