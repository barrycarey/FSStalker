import os
import sys

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from fsstalker.api.endpoints.user_notification_endpoint import user_notification_router

sys.path.append('./')
from fsstalker.api.endpoints.auth_endpoint import auth_router
from fsstalker.api.endpoints.notification_service_endpoint import notification_svc_router
from fsstalker.api.endpoints.sent_notification_endpoint import sent_notification_router
from fsstalker.api.endpoints.user_endpoint import user_router
from fsstalker.core.config import Config
from fsstalker.api.endpoints.watch_endpoint import watch_router

app = FastAPI()
config = Config()
allowed_origins = [
    'http://localhost:3000',
    'https://bstsleuth.com',
    'https://www.bstsleuth.com'
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

heath_router = APIRouter()
@heath_router.get('/health')
def get_health():
    return {'status': 'OK'}

app.include_router(watch_router)
app.include_router(notification_svc_router)
app.include_router(user_router)
app.include_router(sent_notification_router)
app.include_router(auth_router)
app.include_router(heath_router)
app.include_router(user_notification_router)
uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('UV_PORT', 8989)))