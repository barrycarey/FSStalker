import json

import requests
from fastapi import APIRouter, Depends

from fsstalker.core.config import Config
from fsstalker.core.db.unit_of_work_manager import UnitOfWorkManager
from fsstalker.core.logging import log
from fsstalker.core.util.helpers import get_db_engine, get_reddit_user_data

auth_router = APIRouter()

uowm = UnitOfWorkManager(get_db_engine(Config()))

def get_uowm():
    return uowm

@auth_router.get('/auth/patreoncb')
def patreon_cb(code: str, state: str, uowm: UnitOfWorkManager = Depends(get_uowm)):
    log.info('Attempting to link Patreon account')

    res = requests.post('https://www.patreon.com/api/oauth2/token', {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': 'WxT_NvtcRrVuqed9pygyK51tADYWY1qHXr5yHw5jGwsPmXXJhQqqQeU_MynwzfJx',
        'client_secret': '5IRTwwy-hRzIIl3uFmeoP6TCzCr-eiIf8MUIrYpPgX5TvTySJvKiHjdgJgEJF8cW',
        'redirect_uri': 'http://localhost:8989/auth/patreoncb'
    })

    if res.status_code != 200:
        log.error(f'Bad status code {res.status_code} from Patreon when getting token')
        return {'status': 'Error', 'message': 'Failed to get Patreon auth token'}

    patreon_token_data = json.loads(res.text)

    identity_res = requests.get('https://www.patreon.com/api/oauth2/v2/identity', headers={'Authorization': f'Bearer {patreon_token_data["access_token"]}'})

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
        user.patreon_tier_id = 1
        uow.commit()

    return {'status': 'Success', 'message': 'Patreon linked, you may now close this window'}