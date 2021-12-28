import os

import uvicorn
from fastapi import FastAPI

from fsstalker.api.endpoints.notification_service_endpoint import notification_svc_router
from fsstalker.core.config import Config
from fsstalker.core.db.unit_of_work_manager import UnitOfWorkManager
from fsstalker.core.util.helpers import get_db_engine
from fsstalker.api.endpoints.watch_endpoint import watch_router

app = FastAPI()
config = Config()

"""
@app.on_event('startup')
async def startup():
    app.state.db = UnitOfWorkManager(get_db_engine(config))
"""
app.include_router(watch_router)
app.include_router(notification_svc_router)
uvicorn.run(app, host="0.0.0.0", port=os.getenv('port', 8989))