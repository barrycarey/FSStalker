from typing import Text

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request

from fsstalker.api.data_schema.schemas import WatchSchema
from fsstalker.core.config import Config
from fsstalker.core.db.db_models import Watch, NotificationService
from fsstalker.core.db.unit_of_work_manager import UnitOfWorkManager
from fsstalker.core.util.helpers import get_reddit_user_data, get_db_engine

watch_router = APIRouter()

uowm = UnitOfWorkManager(get_db_engine(Config()))

def get_uowm():
    return uowm

@watch_router.get('/watch/{username}')
def get_watches(username: str, token: str, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid auth token')
    with uowm.start() as uow:
        user = uow.user.get_or_create_by_username(user_data['name'])
        if not user:
            raise HTTPException(status_code=404, detail=f'User {user} not found')
        if user.username.lower() != username and not user.is_mod:
            raise HTTPException(status_code=403, detail='Unauthorized')
        return uow.watch.get_by_owner_id(user.id)

@watch_router.post('/watch')
def create_watch(new_watch: WatchSchema, token: Text, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid auth token')

    with uowm.start() as uow:
        user = uow.user.get_by_username(user_data['name'])
        if not user:
            raise HTTPException(status_code=404, detail=f'User {user} not found')

        if [x for x in user.watches if x.subreddit == new_watch.subreddit]:
            raise HTTPException(status_code=422, detail=f'You already have a watch for {new_watch.subreddit}')

        if len(user.watches) >= user.patreon_tier.max_watches:
            raise HTTPException(status_code=422, detail='You have exceeded the max number of allowed watches')

        watch = Watch(
            subreddit=new_watch.subreddit,
            name=new_watch.name,
            include=new_watch.include,
            exclude=new_watch.exclude,
            active=new_watch.active,
            owner=user,
            notification_services=[ns for ns in user.notification_services if ns.id in new_watch.notification_services]
        )
        uow.watch.add(watch)
        uow.commit()

@watch_router.patch('/watch')
def create_watch(watch: WatchSchema, token: Text, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid auth token')

    with uowm.start() as uow:
        user = uow.user.get_by_username(user_data['name'])
        if not user:
            raise HTTPException(status_code=404, detail=f'User {user} not found')

        existing_watch = uow.watch.get_by_id(watch.id)

        if not existing_watch:
            raise HTTPException(status_code=404, detail=f'No existing Watch with ID {watch.id}')

        if user.id != existing_watch.owner_id and not user.is_mod:
            raise HTTPException(status_code=403, detail='You do not own this Watch')

        if len(user.watches) > user.patreon_tier.max_watches:
            raise HTTPException(status_code=422, detail='You have exceeded the max number of allowed watches')

        notification_services = []
        for svc in watch.notification_services:
            existing_notify_svc = uow.notification_service.get_by_id(svc.id)
            if existing_notify_svc:
                if existing_notify_svc.owner_id == user.id or user.is_mod:
                    notification_services.append(existing_notify_svc)
        existing_watch.notification_services = notification_services
        existing_watch.include = watch.include
        existing_watch.exclude = watch.exclude
        existing_watch.name = watch.name
        existing_watch.active = watch.active

        uow.commit()
        return existing_watch

@watch_router.delete('/watch/{id}')
def create_notification_svc(token: str, id: int, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid user token')
    with uowm.start() as uow:
        user = uow.user.get_by_username(user_data['name'])
        if not user:
            raise HTTPException(status_code=404, detail=f'User {user_data["name"]} not found')

        watch = uow.watch.get_by_id(id)
        if not watch:
            raise HTTPException(status_code=404, detail='Failed to find notification service with given ID')

        if watch.owner_id != user.id and not user.is_mod:
            raise HTTPException(status_code=403, detail='Unauthorized')

        uow.watch.remove(watch)

        try:
            uow.commit()
        except Exception as e:
            raise HTTPException(status_code=400, detail='A notification service already exists with that URL')
