from typing import List, Text

from fsstalker.core.db.db_models import Watch
from fsstalker.core.db.repo.repo_base import RepoBase


class WatchRepo(RepoBase):
    def __init__(self, db_session):
        super().__init__(db_session)

    def get_by_id(self, id: int) -> Watch:
        return self.db_session.query(Watch).filter(Watch.id == id).first()

    def get_by_owner(self, owner: Text) -> List[Watch]:
        return self.db_session.query(Watch).filter(Watch.owner == owner).all()

    def get_by_subreddit(self, subreddit: Text) -> List[Watch]:
        return self.db_session.query(Watch).filter(Watch.subreddit == subreddit).all()

    def get_distinct_subreddits(self):
        return self.db_session.query(Watch.subreddit).distinct().all()