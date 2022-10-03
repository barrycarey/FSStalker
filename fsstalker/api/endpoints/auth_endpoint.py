import json

import requests
from fastapi import APIRouter, Depends

from fsstalker.core.config import Config
from fsstalker.core.db.unit_of_work_manager import UnitOfWorkManager
from fsstalker.core.logging import log
from fsstalker.core.util.helpers import get_db_engine, get_reddit_user_data, get_patreon_tier_id

auth_router = APIRouter()

uowm = UnitOfWorkManager(get_db_engine(Config()))

def get_uowm():
    return uowm

# gets member list with owner token
# https://www.patreon.com/api/oauth2/v2/campaigns/9343789/members?include=currently_entitled_tiers,user

@auth_router.get('/auth/patreoncb')
def patreon_cb(code: str, state: str, uowm: UnitOfWorkManager = Depends(get_uowm)):
    log.info('Attempting to link Patreon account')
    config = Config()

    res = requests.post('https://www.patreon.com/api/oauth2/token', {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': config.patreon_client_id,
        'client_secret': config.patreon_client_secret,
        'redirect_uri': config.patreon_redirect_uri
    }, timeout=14)

    if res.status_code != 200:
        log.error(f'Bad status code {res.status_code} from Patreon when getting token')
        return {'status': 'Error', 'message': 'Failed to get Patreon auth token'}

    patreon_token_data = json.loads(res.text)

    identity_res = requests.get(
        'https://www.patreon.com/api/oauth2/v2/identity?include=memberships.currently_entitled_tiers',
        headers={'Authorization': f'Bearer {patreon_token_data["access_token"]}'}
    )

    if identity_res.status_code != 200:
        log.error(f'Bad status code {res.status_code} getting Patreon identity')
        return {'status': 'Error', 'message': 'Failed to get Patreon identity'}

    patreon_data = json.loads(identity_res.text)

    user_data = get_reddit_user_data(state)
    if not user_data:
        return {'status': 'Error', 'message': 'Failed to get Reddit user data'}

    with uowm.start() as uow:
        user = uow.user.get_or_create_by_username(user_data['name'])
        if not user:
            return {'status': 'Error', 'message': 'Failed to find account info'}

        user.patreon_id = patreon_data['data']['id']
        user.patreon_tier_id = get_patreon_tier_id(patreon_data, user.username, uowm)
        uow.commit()

    return {'status': 'Success', 'message': 'Patreon linked, you may now close this window'}