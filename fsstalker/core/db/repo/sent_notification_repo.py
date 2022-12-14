from sqlalchemy.orm import joinedload

from fsstalker.core.db.db_models import SentNotification
from fsstalker.core.db.repo.repo_base import RepoBase


class SentNotificationRepo(RepoBase):
    def __init__(self, db_session):
        super().__init__(db_session)

    def get_by_owner_id(self, owner_id: int, limit: int = 100, offset: int = None) -> list[SentNotification]:
        return self.db_session.query(SentNotification).options(joinedload(SentNotification.owner),
                                                               joinedload(SentNotification.watch)).filter(
            SentNotification.owner_id == owner_id).order_by(SentNotification.id.desc()).limit(limit).offset(offset).all()