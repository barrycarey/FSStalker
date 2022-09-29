import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fsstalker.api.endpoints.auth_endpoint import auth_router
from fsstalker.api.endpoints.notification_service_endpoint import notification_svc_router
from fsstalker.api.endpoints.sent_notification_endpoint import sent_notification_router
from fsstalker.api.endpoints.user_endpoint import user_router
from fsstalker.core.config import Config
from fsstalker.core.db.unit_of_work_manager import UnitOfWorkManager
from fsstalker.core.util.helpers import get_db_engine
from fsstalker.api.endpoints.watch_endpoint import watch_router

app = FastAPI()
config = Config()
allowed_origins = [
    'http://localhost:3000'
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
"""
@app.on_event('startup')
async def startup():
    app.state.db = UnitOfWorkManager(get_db_engine(config))
"""
app.include_router(watch_router)
app.include_router(notification_svc_router)
app.include_router(user_router)
app.include_router(sent_notification_router)
app.include_router(auth_router)
uvicorn.run(app, host="0.0.0.0", port=os.getenv('port', 8989))