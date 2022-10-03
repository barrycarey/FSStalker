import json
from typing import Text, Optional, List

import requests
from praw import Reddit
from praw.models import Submission
from prawcore import Forbidden
from sqlalchemy import create_engine

from fsstalker.core.config import Config
from fsstalker.core.db.unit_of_work_manager import UnitOfWorkManager
from fsstalker.core.logging import log


def get_reddit_instance(config: Config) -> Reddit:
    return Reddit(
                        client_id=config.reddit_client_id,
                        client_secret=config.reddit_client_secret,
                        user_agent=config.reddit_useragent,
                    )


def get_db_engine(config: Config):
    return create_engine('mysql+pymysql://{}:{}@{}/{}'.format(config.database_user,
                                                                   config.database_password,
                                                                   config.database_hostname,
                                                                   config.database_name), echo=False, pool_size=50, pool_pre_ping=True)


def get_submission_type(submission: Submission) -> Optional[Text]:
    """
    Attempt to get the type of post from a submission.
    The Praw object doesn't always contain a post_hint
    :rtype: Text
    :param submission: Praw Submission
    :return:  post type
    """
    submission_type = None
    if submission.is_self:
        submission_type = 'text'
    else:
        try:
            submission_type = submission.__dict__.get('post_hint', None)
        except (AttributeError, Forbidden) as e:
            pass
    return submission_type


def post_includes_words(include_words: List[Text], post_text: Text, exclude_words: List[Text] = None) -> Optional[Text]:
    """
    Check if a given block of text contains any of the given words
    :rtype: Optional[Text]
    :param exclude_words: Don't match if these words are in text
    :param include_words: List of words
    :param post_text: Text to check for words
    :return: The word or None
    """
    include_match = None
    for word in include_words:
        if word.lower() in post_text.lower():
            log.debug('Matched word %s', word)
            include_match = word
            break
    if exclude_words and include_match:
        for word in exclude_words:
            if word.lower() in post_text.lower():
                log.debug('Matched exclude word in text')
                return None

    return include_match

def get_reddit_user_data(token: Text, user_agent: Text = 'windows.repostsleuthbot:v0.0.1 (by /u/barrycarey)'):
    headers = {'Authorization': f'Bearer {token}', 'User-Agent': user_agent}
    r = requests.get('https://oauth.reddit.com/api/v1/me/', headers=headers, timeout=15)
    if r.status_code != 200:
        return
    return json.loads(r.text)

def get_patreon_tier_id(api_data: dict, username: str, uowm: UnitOfWorkManager) -> Optional[int]:
    log.info('Attempting to get Patreon tier for %s', username)
    if 'included' not in api_data:
        log.error('No Include data in Patron API response')
        return

    tier_data = next((x for x in api_data['included'] if x['type'] == 'tier'), None)

    if not tier_data:
        log.error('No tier data in API response')
        return


    with uowm.start() as uow:
        tier = uow.patreon_tier.get_by_tier_id(tier_data['id'])
        if not tier:
            log.error('Failed to find Patreon tier with ID %s', tier_data['id'])
            return

        return tier.id

