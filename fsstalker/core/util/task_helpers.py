from typing import List, Text, NoReturn, Optional, Dict

from praw import Reddit
from praw.models import Submission
from sqlalchemy.exc import IntegrityError

from fsstalker.core.db.db_models import CheckedPost, Watch
from fsstalker.core.db.unit_of_work_manager import UnitOfWorkManager
from fsstalker.core.logging import log
from fsstalker.core.util.helpers import get_submission_type, post_includes_words


def checked_submission_filter(uowm: UnitOfWorkManager):
    """
    Filter a list of submissions to remove any we have already checked
    :param uowm: Unit of work manager
    :return: Filter functions
    """

    def checked_submission(submission: Submission):
        with uowm.start() as uow:
            if uow.checked_post.get_by_post_id(submission.id):
                return False
            return True

    return checked_submission


def submission_type_filter(submission_type: Text):
    """
    Filter a list of submissions to remove all but the type we select
    :param submission_type: The type of submission to keep
    :return: filter function
    """
    def type_filter(submission: Submission):
        if get_submission_type(submission) != submission_type:
            return False
        return True

    return type_filter

def load_subreddit_submissions(uowm: UnitOfWorkManager, reddit: Reddit, subreddit_name: Text) -> List[Submission]:
    """
    Load submissions from given subreddit, remove all non-text posts and already checked posts
    :param uowm:
    :param reddit:
    :param subreddit_name:
    :return:
    """
    submissions = list(reddit.subreddit(subreddit_name).new(limit=500))
    log.debug('Loaded %s submissions from %s pre-filter', len(submissions), subreddit_name)
    submissions = list(filter(checked_submission_filter(uowm), submissions))
    submissions = list(filter(submission_type_filter('text'), submissions))
    log.info('%s submissions from %s after filter', len(submissions), subreddit_name)
    return submissions


def create_checked_post(uowm: UnitOfWorkManager, submission_id: Text) -> NoReturn:
    """
    Saved a checked post to the database
    :param uowm: Unit of work manager
    :param submission_id: Submission ID
    """
    with uowm.start() as uow:
        uow.checked_post.add(
            CheckedPost(post_id=submission_id)
        )
        try:
            uow.commit()
        except IntegrityError as e:
            log.exception('Failed to save checked post', exc_info=True)


def check_submission_for_watches(submission: Submission, watches: List[Watch]) -> List[Dict]:
    results = []
    for watch in watches:
        match = post_includes_words(
            watch.include.split(','),
            submission.title + submission.__dict__.get('selftext', None),
            exclude_words=watch.exclude.split(',') if watch.exclude else None
        )
        if match:
            log.info('Post %s matches word %s for watch %s', submission.id, match, watch.id)
            results.append({'watch_id': watch.id, 'match_word': match, 'submission': submission})
    return results

def check_watches(uowm: UnitOfWorkManager, submissions: List[Submission]) -> List[dict]:
    subreddit_name = submissions[0].subreddit.display_name
    results = []
    log.info('Processing watches for %s', subreddit_name)

    with uowm.start() as uow:
        watches = uow.watch.get_by_subreddit(subreddit_name)

    log.info('Found %s watches for subreddit %s', len(watches), subreddit_name)
    for submission in submissions:
        results += check_submission_for_watches(submission, watches)
        create_checked_post(uowm, submission.id)

    return results

