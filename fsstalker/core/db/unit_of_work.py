from sqlalchemy.orm import scoped_session

from fsstalker.core.db.repo.checked_post_repo import CheckedPostRepo
from fsstalker.core.db.repo.notification_service_repo import NotificationServiceRepo
from fsstalker.core.db.repo.sent_notification_repo import SentNotificationRepo
from fsstalker.core.db.repo.user_repo import UserRepo
from fsstalker.core.db.repo.watch_repo import WatchRepo


class UnitOfWork():

    def __init__(self, session_factory):
        self.session_factory = scoped_session(session_factory)

    def __enter__(self):
        self.session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    @property
    def watch(self) -> WatchRepo:
        return WatchRepo(self.session)

    @property
    def notification_service(self) -> NotificationServiceRepo:
        return NotificationServiceRepo(self.session)

    @property
    def sent_notification(self) -> SentNotificationRepo:
        return SentNotificationRepo(self.session)

    @property
    def checked_post(self) -> CheckedPostRepo:
        return CheckedPostRepo(self.session)

    @property
    def user(self) -> UserRepo:
        return UserRepo(self.session)