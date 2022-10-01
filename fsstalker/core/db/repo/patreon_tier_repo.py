from typing import Optional

from fsstalker.core.db.db_models import PatreonTier
from fsstalker.core.db.repo.repo_base import RepoBase


class PatreonTierRepo(RepoBase):
    def get_by_tier_id(self, tier_id: int) -> Optional[PatreonTier]:
        return self.db_session.query(PatreonTier).filter(PatreonTier.tier_id == tier_id).first()