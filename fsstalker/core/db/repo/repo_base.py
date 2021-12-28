from fsstalker.core.db.db_models import Base


class RepoBase:
    def __init__(self, db_session):
        self.db_session = db_session

    def add(self, item: Base):
        self.db_session.add(item)

    def remove(self, item: Base):
        self.db_session.delete(item)