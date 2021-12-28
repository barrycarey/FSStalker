from typing import Text

from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request

from fsstalker.api.data_schema.schemas import WatchSchema
from fsstalker.core.config import Config
from fsstalker.core.db.db_models import Watch
from fsstalker.core.db.unit_of_work_manager import UnitOfWorkManager
from fsstalker.core.util.helpers import get_reddit_user_data, get_db_engine

watch_router = APIRouter()

uowm = UnitOfWorkManager(get_db_engine(Config()))

def get_uowm():
    return uowm

@watch_router.get('/watch')
def get_watches(request: Request, token: Text, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid user token')
    with uowm.start() as uow:
        user = uow.user.get_or_create_by_username(user_data['name'])
        return user.watches

@watch_router.post('/watch')
def create_watch(new_watch: WatchSchema, token: Text, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid user token')

    with uowm.start() as uow:
        user = uow.user.get_or_create_by_username(user_data['name'])
        if [x for x in user.watches if x.subreddit == new_watch.subreddit]:
            raise HTTPException(status_code=422, detail=f'You already have a watch for {new_watch.subreddit}')

        watch = Watch(
            subreddit=new_watch.subreddit,
            include=','.join(new_watch.include),
            exclude=','.join(new_watch.exclude),
            owner=user,
            notification_services=[ns for ns in user.notification_services if ns.id in new_watch.notification_svc]
        )
        uow.watch.add(watch)
        uow.commit()