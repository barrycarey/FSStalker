from datetime import datetime
from typing import Text, List

from pydantic import BaseModel




class NotificationSvcSchema(BaseModel):
    id: int = None
    url: str
    owner_id: int = None
    name: str

class WatchSchema(BaseModel):
    id: int = None
    owner_id: int = None
    name: str
    subreddit: str
    active: bool
    include: str
    exclude: str
    notification_services: List[NotificationSvcSchema]

class UserNotificationSchema(BaseModel):
    id: int
    owner_id: int
    created_at: datetime
    read: bool
    message: str
    type: str
