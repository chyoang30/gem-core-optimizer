from fastapi import APIRouter, HTTPException
from app import store
from app.schemas import CoreGradeUpdate, AssignRequest, CoreResponse
from app.serializers import core_to_response

router = APIRouter()

@router.get("", response_model=list[CoreResponse], summary="코어 3개 현황 조회")
def list_cores():
    return [core_to_response(c) for c in store.get_cores()]

@router.get("/{core_id}", response_model=CoreResponse, summary="특정 코어 조회")
def get_core(core_id: int):
    core = store.get_core(core_id)
    if not core:
        raise HTTPException(404, detail="코어를 찾을 수 없습니다.")
    return core_to_response(core)

@router.patch("/{core_id}/grade", response_model=CoreResponse, summary="코어 등급 변경")
def update_grade(core_id: int, body: CoreGradeUpdate):
    core = store.set_core_grade(core_id, body.grade)
    if not core:
        raise HTTPException(404, detail="코어를 찾을 수 없습니다.")
    return core_to_response(core)

@router.post("/{core_id}/assign", response_model=CoreResponse, status_code=201, summary="슬롯에 젬 배치")
def assign_gem(core_id: int, body: AssignRequest):
    core, err = store.assign_gem_to_slot(core_id, body.gem_id)
    if err:
        raise HTTPException(400, detail=err)
    return core_to_response(core)

@router.delete("/{core_id}/slots/{slot_index}", response_model=CoreResponse, summary="슬롯에서 젬 제거")
def remove_slot(core_id: int, slot_index: int):
    core, err = store.remove_from_slot(core_id, slot_index)
    if err:
        raise HTTPException(400, detail=err)
    return core_to_response(core)
