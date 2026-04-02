"""
인메모리 상태 저장소.
추후 SQLite/PostgreSQL + SQLAlchemy로 교체하기 쉽도록
접근 인터페이스를 함수로 분리해 둠.
"""

from typing import Optional
from app.models.gem import Gem
from app.models.core import Core, GRADES

# ── 상태 ────────────────────────────────────────────────
_gems: list[Gem] = []
_gid: int = 1

_cores: list[Core] = [
    Core(id=0, grade="relic"),
    Core(id=1, grade="relic"),
    Core(id=2, grade="relic"),
]

# ── 젬 ────────────────────────────────────────────────
def get_gems() -> list[Gem]:
    return _gems

def get_gem(gem_id: int) -> Optional[Gem]:
    return next((g for g in _gems if g.id == gem_id), None)

def add_gem(will: int, pt: int) -> Gem:
    global _gid
    gem = Gem(id=_gid, will=will, pt=pt)
    _gid += 1
    _gems.append(gem)
    _refresh_used()
    return gem

def remove_gem(gem_id: int) -> bool:
    global _gems
    gem = get_gem(gem_id)
    if not gem:
        return False
    # 코어 슬롯에서도 제거
    for core in _cores:
        core.slots = [None if (s and s.id == gem_id) else s for s in core.slots]
    _gems = [g for g in _gems if g.id != gem_id]
    _refresh_used()
    return True

def clear_gems():
    global _gems, _gid
    _gems = []
    _gid = 1
    for core in _cores:
        core.slots = [None, None, None, None]

# ── 코어 ────────────────────────────────────────────────
def get_cores() -> list[Core]:
    _refresh_used()
    return _cores

def get_core(core_id: int) -> Optional[Core]:
    return next((c for c in _cores if c.id == core_id), None)

def set_core_grade(core_id: int, grade: str) -> Optional[Core]:
    core = get_core(core_id)
    if not core:
        return None
    core.grade = grade
    core.slots = [None, None, None, None]
    _refresh_used()
    return core

def assign_gem_to_slot(core_id: int, gem_id: int) -> tuple[Optional[Core], Optional[str]]:
    core = get_core(core_id)
    gem = get_gem(gem_id)
    if not core:
        return None, "코어를 찾을 수 없습니다."
    if not gem:
        return None, "젬을 찾을 수 없습니다."
    if gem.used:
        return None, "이미 배치된 젬입니다."
    grade = GRADES[core.grade]
    used_will = sum(s.will for s in core.slots if s)
    if used_will + gem.will > grade["max_will"]:
        return None, f"의지력 초과! 현재 {used_will}/{grade['max_will']}, 필요 추가: {gem.will}"
    try:
        slot_idx = core.slots.index(None)
    except ValueError:
        return None, "슬롯이 가득 찼습니다 (최대 4개)"
    core.slots[slot_idx] = gem
    _refresh_used()
    return core, None

def remove_from_slot(core_id: int, slot_idx: int) -> tuple[Optional[Core], Optional[str]]:
    core = get_core(core_id)
    if not core:
        return None, "코어를 찾을 수 없습니다."
    if slot_idx < 0 or slot_idx > 3:
        return None, "슬롯 인덱스는 0~3 이어야 합니다."
    core.slots[slot_idx] = None
    _refresh_used()
    return core, None

# ── 내부 헬퍼 ────────────────────────────────────────────
def _refresh_used():
    used_ids = {s.id for c in _cores for s in c.slots if s}
    for g in _gems:
        g.used = g.id in used_ids
