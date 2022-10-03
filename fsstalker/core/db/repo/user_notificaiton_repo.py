from typing import NoReturn

from fsstalker.core.db.db_models import UserNotification
from fsstalker.core.db.repo.repo_base import RepoBase


class UserNotificationRepo(RepoBase):
    def get_unread_by_owner_id(self, owner_id: int) -> list[UserNotification]:
        return self.db_session.query(UserNotification).filter(UserNotification.owner_id == owner_id,
                                                              UserNotification.read == False).all()
    def get_all_by_owner_id(self, owner_id: int) -> list[UserNotification]:
        return self.db_session.query(UserNotification).filter(UserNotification.owner_id == owner_id).all()