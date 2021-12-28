from fsstalker.core.db.repo.repo_base import RepoBase


class SentNotificationRepo(RepoBase):
    def __init__(self, db_session):
        super().__init__(db_session)