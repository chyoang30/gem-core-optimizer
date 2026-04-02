from fastapi import APIRouter, HTTPException
from app import store
from app.models.core import GRADES
from app.models.gem import Gem
from app.schemas import OptimizeResult
from app.serializers import core_to_response

router = APIRouter()

# ── 최적화 알고리즘 ──────────────────────────────────────
POINT_WEIGHTS = {10: 10, 14: 100, 17: 1000, 18: 1, 19: 1, 20: 1}

def _core_score(pts: int, grade: str) -> int:
    return sum(POINT_WEIGHTS.get(p, 1) for p in GRADES[grade]["points"] if pts >= p)

def _build_types(gems: list[Gem]) -> list[dict]:
    """동일한 (will, pt) 젬을 묶어서 탐색 공간 축소."""
    buckets: dict[tuple, dict] = {}
    for g in gems:
        key = (g.will, g.pt)
        if key not in buckets:
            buckets[key] = {"will": g.will, "pt": g.pt, "cnt": 0, "ids": []}
        buckets[key]["cnt"] += 1
        buckets[key]["ids"].append(g.id)
    return list(buckets.values())

def _subsets(types: list[dict], max_slots: int, max_will: int) -> list[dict]:
    """Branch-and-bound 서브셋 열거."""
    results = []
    used = [0] * len(types)

    def bt(i: int, slots: int, will: int, pts: int):
        if slots >= 1:
            results.append({"pts": pts, "will": will, "used": used[:]})
        if slots == max_slots or i == len(types):
            return
        for j in range(i, len(types)):
            t = types[j]
            max_take = min(t["cnt"], max_slots - slots,
                           (max_will - will) // t["will"] if t["will"] else 0)
            for k in range(1, max_take + 1):
                used[j] += k
                bt(j + 1, slots + k, will + t["will"] * k, pts + t["pt"] * k)
                used[j] -= k

    bt(0, 0, 0, 0)
    return results

def _run_optimization(gems: list[Gem], cores) -> list[list[int]] | None:
    """3개 코어 전체 최적 젬 배치를 계산해 gem_id 배열로 반환."""
    types = _build_types(gems)

    subsets = []
    for core in cores:
        grade = core.grade
        fs = _subsets(types, 4, GRADES[grade]["max_will"])
        fs.sort(key=lambda s: _core_score(s["pts"], grade), reverse=True)
        subsets.append(fs)

    top_pts = [
        _core_score(subsets[i][0]["pts"], cores[i].grade) if subsets[i] else 0
        for i in range(3)
    ]

    best_score = -1
    best_assignment = None

    for s0 in subsets[0]:
        sc0 = _core_score(s0["pts"], cores[0].grade)
        if sc0 + top_pts[1] + top_pts[2] <= best_score:
            break
        for s1 in subsets[1]:
            sc01 = sc0 + _core_score(s1["pts"], cores[1].grade)
            if sc01 + top_pts[2] <= best_score:
                break
            if any((s0["used"][i] or 0) + (s1["used"][i] or 0) > types[i]["cnt"]
                   for i in range(len(types))):
                continue
            for s2 in subsets[2]:
                sc = sc01 + _core_score(s2["pts"], cores[2].grade)
                if sc <= best_score:
                    break
                if any((s0["used"][i] or 0) + (s1["used"][i] or 0) + (s2["used"][i] or 0)
                       > types[i]["cnt"] for i in range(len(types))):
                    continue
                best_score = sc
                best_assignment = [s0, s1, s2]

    if not best_assignment:
        return None

    result_ids = []
    for s in best_assignment:
        ids = []
        for i, cnt in enumerate(s["used"]):
            ids.extend(types[i]["ids"][:cnt])
        result_ids.append(ids)
    return result_ids

# ── 엔드포인트 ───────────────────────────────────────────

@router.post("", response_model=OptimizeResult, summary="최적 배치 계산 후 코어에 적용")
def optimize_and_apply():
    gems = store.get_gems()
    cores = store.get_cores()
    if not gems:
        raise HTTPException(400, detail="젬을 먼저 추가해주세요.")

    best_ids = _run_optimization(gems, cores)
    if not best_ids:
        raise HTTPException(400, detail="조합을 찾을 수 없습니다. 코어 등급과 의지력 조건을 확인해주세요.")

    # 결과를 실제 코어에 적용
    for ci, core in enumerate(cores):
        core.slots = [None, None, None, None]
        for si, gid in enumerate(best_ids[ci]):
            core.slots[si] = store.get_gem(gid)

    store._refresh_used()

    total_effects = sum(len(c.active_effects()) for c in cores)
    return OptimizeResult(
        total_effects=total_effects,
        cores=[core_to_response(c) for c in cores],
        message=f"총 {total_effects}개 효과 활성화. 코어 배치에 자동 적용되었습니다.",
    )

@router.get("/preview", response_model=OptimizeResult, summary="최적 배치 미리보기 (적용 없음)")
def optimize_preview():
    gems = store.get_gems()
    cores = store.get_cores()
    if not gems:
        raise HTTPException(400, detail="젬을 먼저 추가해주세요.")

    best_ids = _run_optimization(gems, cores)
    if not best_ids:
        raise HTTPException(400, detail="조합을 찾을 수 없습니다.")

    # 임시 복사본에만 적용 (원본 수정 없음)
    import copy
    preview_cores = copy.deepcopy(cores)
    for ci, core in enumerate(preview_cores):
        core.slots = [None, None, None, None]
        for si, gid in enumerate(best_ids[ci]):
            original = store.get_gem(gid)
            if original:
                core.slots[si] = copy.deepcopy(original)

    total_effects = sum(len(c.active_effects()) for c in preview_cores)
    return OptimizeResult(
        total_effects=total_effects,
        cores=[core_to_response(c) for c in preview_cores],
        message=f"미리보기 결과: 총 {total_effects}개 효과 활성화 (적용되지 않음)",
    )
