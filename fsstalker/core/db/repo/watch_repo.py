from typing import List, Text

from sqlalchemy.orm import joinedload

from fsstalker.core.db.db_models import Watch
from fsstalker.core.db.repo.repo_base import RepoBase


class WatchRepo(RepoBase):
    def __init__(self, db_session):
        super().__init__(db_session)

    def update(self, item: Watch):
        self.db_session.update(item)

    def get_by_id(self, id: int) -> Watch:
        return self.db_session.query(Watch).options(joinedload(Watch.notification_services)).filter(Watch.id == id).first()

    def get_by_owner_id(self, owner_id: int) -> List[Watch]:
        return self.db_session.query(Watch).options(joinedload(Watch.notification_services)).filter(Watch.owner_id == owner_id).all()

    def get_by_owner_id_with_notifications(self, owner_id: int) -> List[Watch]:
        return self.db_session.query(Watch).options(joinedload(Watch.notification_services), joinedload(Watch.sent_notifications)).filter(Watch.owner_id == owner_id).all()

    def get_by_subreddit(self, subreddit: Text) -> List[Watch]:
        return self.db_session.query(Watch).filter(Watch.subreddit == subreddit, Watch.active == True).all()

    def get_distinct_subreddits(self):
        return self.db_session.query(Watch.subreddit).distinct().all()