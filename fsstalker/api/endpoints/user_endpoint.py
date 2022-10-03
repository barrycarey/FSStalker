from fastapi import APIRouter, Depends, HTTPException

from fsstalker.core.config import Config
from fsstalker.core.db.db_models import User
from fsstalker.core.db.unit_of_work_manager import UnitOfWorkManager
from fsstalker.core.util.helpers import get_db_engine, get_reddit_user_data

user_router = APIRouter()
uowm = UnitOfWorkManager(get_db_engine(Config()))
def get_uowm():
    return uowm
@user_router.get('/user/{username}')
def get_user(token: str, username: str, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid user token')
    with uowm.start() as uow:
        user = uow.user.get_user_with_patreon(username)
        if not user:
            raise HTTPException(status_code=404, detail=f'User {user_data["name"]}  not found')

        if user.username != user_data['name'] and not user.is_mod:
            raise HTTPException(status_code=403, detail='Unauthorized')
        return user

@user_router.post('/user/')
def get_user(token: str, uowm: UnitOfWorkManager = Depends(get_uowm)):
    user_data = get_reddit_user_data(token)
    if not user_data:
        raise HTTPException(status_code=403, detail='Invalid user token')
    with uowm.start() as uow:
        user = uow.user.get_by_username(user_data['name'] )
        if user:
            raise HTTPException(status_code=422, detail=f'User already exists')

        new_user = User(username=user_data['name'], patreon_tier_id=1)
        uow.user.add(new_user)
        uow.commit()

        return new_user