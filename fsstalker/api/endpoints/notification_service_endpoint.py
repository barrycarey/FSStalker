from typing import Text

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from fsstalker.api.data_schema.schemas import NotificationSvcSchema
from fsstalker.core.config import Config
from fsstalker.core.db.db_models import NotificationService
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

@notification_svc_router.post('/notification-svc')
def create_notification_svc(token: str, notification_svc: NotificationSvcSchema, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid user token')
    with uowm.start() as uow:
        user = uow.user.get_by_username(user_data['name'])
        if not user:
            raise HTTPException(status_code=404, detail=f'User {user_data["name"]} not found')

        acting_notification_svc = None
        if notification_svc.id:
            acting_notification_svc = uow.notification_service.get_by_id(notification_svc.id)
            if not acting_notification_svc:
                raise HTTPException(status_code=400, detail='Failed to find existing notification service with given ID')
            if acting_notification_svc.owner_id != notification_svc.owner_id:
                raise HTTPException(status_code=401, detail='You do not own that notification service')
            acting_notification_svc.name = notification_svc.name
            acting_notification_svc.url = notification_svc.url
        else:
            acting_notification_svc = NotificationService(owner_id=user.id, name=notification_svc.name, url=notification_svc.url)
            uow.notification_service.add(acting_notification_svc)
        try:
            uow.commit()
        except IntegrityError:
            raise HTTPException(status_code=400, detail='A notification service already exists with that URL')
        return acting_notification_svc

@notification_svc_router.delete('/notification-svc/{id}')
def create_notification_svc(token: str, id: int, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid user token')
    with uowm.start() as uow:
        user = uow.user.get_by_username(user_data['name'])
        if not user:
            raise HTTPException(status_code=404, detail=f'User {user_data["name"]} not found')

        notification_svc = uow.notification_service.get_by_id(id)
        if not notification_svc:
            raise HTTPException(status_code=404, detail='Failed to find notification service with given ID')

        if notification_svc.owner_id != user.id and not user.is_mod:
            raise HTTPException(status_code=403, detail='Unauthorized')

        uow.notification_service.remove(notification_svc)

        try:
            uow.commit()
        except IntegrityError:
            raise HTTPException(status_code=400, detail='A notification service already exists with that URL')



@notification_svc_router.get('/notification-svc/{username}')
def get_notification_svc(username: str, token: str, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid user token')
    with uowm.start() as uow:
        user = uow.user.get_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail=f'User {username} not found')
        if user.username != username and not user.is_mod:
            raise HTTPException(status_code=403, detail='Unauthorized')

        return user.notification_services
