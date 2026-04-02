from dataclasses import dataclass, field

@dataclass
class Gem:
    id: int
    will: int   # 필요 의지력 3~7
    pt: int     # 부여 포인트 1~5
    used: bool = False
