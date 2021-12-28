from typing import Text, List

from pydantic import BaseModel


class WatchSchema(BaseModel):
    owner_id: int
    subreddit: Text
    active: bool
    include: List[Text]
    exclude: List[Text]
    notification_svc: List[int]