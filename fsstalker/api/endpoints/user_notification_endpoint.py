from fastapi import APIRouter, Depends, HTTPException

from fsstalker.core.config import Config
from fsstalker.core.db.unit_of_work_manager import UnitOfWorkManager
from fsstalker.core.util.helpers import get_db_engine, get_reddit_user_data

user_notification_router = APIRouter()
uowm = UnitOfWorkManager(get_db_engine(Config()))
def get_uowm():
    return uowm

@user_notification_router.get('/user-notifications/{username}')
def get_user_notifications(token: str, username: str, unread: bool = True, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid user token')
    with uowm.start() as uow:
        user = uow.user.get_user_with_patreon(username)
        if not user:
            raise HTTPException(status_code=404, detail=f'User {user_data["name"]}  not found')

        if unread:
            return uow.user_notifications.get_unread_by_owner_id(user.id)
        else:
            return uow.user_notifications.get_all_by_owner_id(user.id)