from typing import Text

from fsstalker.core.db.db_models import CheckedPost
from fsstalker.core.db.repo.repo_base import RepoBase


class CheckedPostRepo(RepoBase):
    def __init__(self, db_session):
        super().__init__(db_session)

    def get_by_post_id(self, post_id: Text) -> CheckedPost:
        return self.db_session.query(CheckedPost).filter(CheckedPost.post_id == post_id).first()