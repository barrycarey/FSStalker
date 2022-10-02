from dataclasses import dataclass


@dataclass
class PatreonMemberData:
    status: str
    user_id: int
    tier: int