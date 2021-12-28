from typing import Text

from fastapi import APIRouter, Depends, HTTPException

from fsstalker.core.config import Config
from fsstalker.core.db.unit_of_work_manager import UnitOfWorkManager
from fsstalker.core.util.helpers import get_db_engine, get_reddit_user_data

notification_svc_router = APIRouter()

uowm = UnitOfWorkManager(get_db_engine(Config()))

def get_uowm():
    return uowm

@notification_svc_router.get('/notification-svc')
def get_notification_svc(token: str, limit: int = None, offset: int = None, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid user token')
    with uowm.start() as uow:
        user = uow.user.get_by_username(user_data['name'])
        if not user:
            raise HTTPException(status_code=404, detail=f'User {user_data["name"]} not found')
        if not user.is_mod:
            raise HTTPException(status_code=401, detail='You\'re not allowed to do that')

        return uow.notification_service.get_all(limit=limit, offset=offset)

@notification_svc_router.get('/notification-svc/{user}')
def get_notification_svc(username: str, token: str, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid user token')
    with uowm.start() as uow:
        user = uow.user.get_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail=f'User {username} not found')
        if user.username.lower() != username:
        return user.notification_services