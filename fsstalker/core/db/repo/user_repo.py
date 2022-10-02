from typing import Text

from sqlalchemy.orm import joinedload

from fsstalker.core.db.db_models import User
from fsstalker.core.db.repo.repo_base import RepoBase


class UserRepo(RepoBase):

    def get_by_username(self, username: str) -> User:
        return self.db_session.query(User).filter(User.username == username).first()

    def get_by_id(self, id: int) -> User:
        return self.db_session.query(User).filter(User.id == id).first()

    def get_all(self, limit: int = None, offset: int = None) -> list[User]:
        return self.db_session.query(User).limit(limit).offset(offset).all()
    def get_or_create_by_username(self, username: str) -> User:
        user = self.db_session.query(User).filter(User.username == username).first()
        if not user:
            user = User(username=username)
            self.db_session.commit()
        return user

    def get_user_with_patreon(self, username: str) -> User:
        return self.db_session.query(User).options(joinedload(User.patreon_tier)).filter(User.username == username).first()