from fastapi import APIRouter, HTTPException
from app import store
from app.schemas import GemCreate, GemBulkCreate, GemResponse, BulkResult
from app.serializers import gem_to_response

router = APIRouter()

@router.get("", response_model=list[GemResponse], summary="전체 젬 목록 조회")
def list_gems():
    return [gem_to_response(g) for g in store.get_gems()]

@router.post("", response_model=GemResponse, status_code=201, summary="젬 추가")
def create_gem(body: GemCreate):
    gem = store.add_gem(body.will, body.pt)
    return gem_to_response(gem)

@router.post("/bulk", response_model=BulkResult, status_code=201, summary="젬 일괄 추가 (붙여넣기/CSV)")
def bulk_create_gems(body: GemBulkCreate):
    added = []
    errors = []
    for i, line in enumerate(body.lines.strip().splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.replace("\t", ",").split(",")]
        if len(parts) < 2:
            errors.append(f"{i}번 줄: 열이 부족합니다 ({line!r})")
            continue
        try:
            will, pt = int(parts[0]), int(parts[1])
        except ValueError:
            errors.append(f"{i}번 줄: 숫자가 아닙니다 ({line!r})")
            continue
        if not (3 <= will <= 7 and 1 <= pt <= 5):
            errors.append(f"{i}번 줄: 범위 초과 (will={will}, pt={pt})")
            continue
        gem = store.add_gem(will, pt)
        added.append(gem_to_response(gem))
    return BulkResult(added=len(added), errors=errors, gems=added)

@router.delete("/{gem_id}", status_code=204, summary="젬 삭제")
def delete_gem(gem_id: int):
    if not store.remove_gem(gem_id):
        raise HTTPException(404, detail="젬을 찾을 수 없습니다.")

@router.delete("", status_code=204, summary="전체 젬 초기화")
def clear_gems():
    store.clear_gems()
