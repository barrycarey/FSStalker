from typing import List, Text, NoReturn, Optional, Dict

from praw import Reddit
from praw.models import Submission
from prawcore import PrawcoreException, Forbidden
from sqlalchemy.exc import IntegrityError

from fsstalker.core.common.models.patreon import PatreonMemberData
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

def load_subreddit_submissions(uowm: UnitOfWorkManager, reddit: Reddit, subreddit_name: str) -> List[Submission]:
    """
    Load submissions from given subreddit, remove all non-text posts and already checked posts
    :param uowm:
    :param reddit:
    :param subreddit_name:
    :return:
    """
    try:
        submissions = list(reddit.subreddit(subreddit_name).new(limit=500))
    except Forbidden as e:
        log.error('Forbidden from checking subreddit %s', subreddit_name)
        return []
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
            log.exception('Failed to save checked post: %s', e, exc_info=False)


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
            results.append({'watch_id': watch.id, 'match_word': match, 'submission': submission, 'owner_id': watch.owner_id})
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

def convert_raw_patreon_member_data(member_data: dict) -> list[PatreonMemberData]:
    """
    Parse the raw Patreon member response and return a stripped down dataclass with the values we need
    :param member_data: Raw API data
    :return: List of PatreonMemberData
    """
    results = []
    for member in member_data['data']:
        log.debug(member)
        results.append(
            PatreonMemberData(
                user_id=member['relationships']['user']['data']['id'],
                tier=member['relationships']['currently_entitled_tiers']['data'][0]['id'],
                status=member['attributes']['patron_status']
            )
        )

    return results
def patreon_member_update(member_data: dict, uowm: UnitOfWorkManager) -> NoReturn:
    """
    Take the raw API result for Patreon campaign members and check them against the database.
    Adjust user's tiers where needed
    :param member_data: Raw Patreon API result
    :param uowm: UnitOfWorkManager
    :return: None
    """
    try:
        patreon_data = convert_raw_patreon_member_data(member_data)
    except KeyError:
        log.error('Failed to convert raw Patreon member data')
        return
    except Exception as e:
        log.exception('Unknown Patreon member conversion error')
        return

    with uowm.start() as uow:
        users = uow.user.get_all()
        for user in users:
            patreon_user = next((x for x in patreon_data if user.patreon_id == x.user_id), None)
            if not patreon_user:
                log.error('No Patreon data for user %s', user.username)
                continue
            if patreon_user.status != 'active_patron':
                log.info('%s is inactive on Patreon. Setting to free tier')
                user.patreon_tier_id = 1
                continue

            tier = uow.patreon_tier.get_by_tier_id(patreon_user.tier)
            if not tier:
                log.critical('Failed to find existing tier with ID %s', patreon_user.tier)
                continue

            if user.patreon_tier_id != tier.id:
                log.info('Changing user %s to tier %s', user.username, tier.name)
                user.patreon_tier_id = tier.id

        log.info('Finished refreshing Patreon member data')
        uow.commit()