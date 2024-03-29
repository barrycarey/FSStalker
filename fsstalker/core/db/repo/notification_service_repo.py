from typing import Text, List

from fsstalker.core.db.db_models import NotificationService
from fsstalker.core.db.repo.repo_base import RepoBase


class NotificationServiceRepo(RepoBase):
    def __init__(self, db_session):
        super().__init__(db_session)

    def get_by_owner(self, owner: Text) -> List[NotificationService]:
        return self.db_session.query(NotificationService).filter(NotificationService.owner == owner).order_by(NotificationService.created_at.desc()).all()

    def get_all(self, limit: int = None, offset: int = None) -> List[NotificationService]:
        return self.db_session.query(NotificationService).limit(limit).offset(offset).all()

    def get_by_id(self, id: int) -> NotificationService:
        return self.db_session.query(NotificationService).filter(NotificationService.id == id).first()