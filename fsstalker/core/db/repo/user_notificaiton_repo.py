from typing import NoReturn, Optional

from fsstalker.core.db.db_models import UserNotification
from fsstalker.core.db.repo.repo_base import RepoBase


class UserNotificationRepo(RepoBase):

    def get_by_id(self, id: int) -> Optional[UserNotification]:
        return self.db_session.query(UserNotification).filter(UserNotification.id == id).first()
    def get_unread_by_owner_id(self, owner_id: int, limit: int = 20, offset: int = None) -> list[UserNotification]:
        return self.db_session.query(UserNotification).filter(UserNotification.owner_id == owner_id,
                                                              UserNotification.read == False).order_by(UserNotification.id.desc()).limit(limit).offset(offset).all()
    def get_all_by_owner_id(self, owner_id: int, limit: int = None, offset: int = None) -> list[UserNotification]:
        return self.db_session.query(UserNotification).filter(UserNotification.owner_id == owner_id).limit(limit).offset(offset).all()