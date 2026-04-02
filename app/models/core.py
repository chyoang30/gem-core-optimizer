from dataclasses import dataclass, field
from typing import Optional
from app.models.gem import Gem

GRADES: dict[str, dict] = {
    "hero":   {"name": "영웅", "max_will": 9,  "points": [10]},
    "legend": {"name": "전설", "max_will": 12, "points": [10, 14]},
    "relic":  {"name": "유물", "max_will": 15, "points": [10, 14, 17, 18, 19, 20]},
    "ancient":{"name": "고대", "max_will": 17, "points": [10, 14, 17, 18, 19, 20]},
}

@dataclass
class Core:
    id: int
    grade: str = "relic"
    slots: list[Optional[Gem]] = field(default_factory=lambda: [None, None, None, None])

    def total_points(self) -> int:
        return sum(s.pt for s in self.slots if s)

    def active_effects(self) -> list[int]:
        pts = self.total_points()
        return [p for p in GRADES[self.grade]["points"] if pts >= p]
