from fastapi import APIRouter, Depends, HTTPException

from fsstalker.core.config import Config
from fsstalker.core.db.unit_of_work_manager import UnitOfWorkManager
from fsstalker.core.util.helpers import get_db_engine, get_reddit_user_data

sent_notification_router = APIRouter()

uowm = UnitOfWorkManager(get_db_engine(Config()))

def get_uowm():
    return uowm

@sent_notification_router.get('/sent-notifications/{username}')
def get_watches(username: str, token: str, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid auth token')
    with uowm.start() as uow:
        user = uow.user.get_or_create_by_username(user_data['name'])
        if not user:
            raise HTTPException(status_code=404, detail=f'User {user} not found')
        if user.username.lower() != username.lower() and not user.is_mod:
            raise HTTPException(status_code=403, detail='Unauthorized')
        res = uow.sent_notification.get_by_owner_id(user.id)
        return res


