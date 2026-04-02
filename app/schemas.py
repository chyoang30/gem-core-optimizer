from pydantic import BaseModel, Field, field_validator
from typing import Optional

# ── 요청 스키마 ──────────────────────────────────────────

class GemCreate(BaseModel):
    will: int = Field(..., ge=3, le=7, description="필요 의지력 (3~7)")
    pt: int   = Field(..., ge=1, le=5, description="부여 포인트 (1~5)")

class GemBulkCreate(BaseModel):
    lines: str = Field(..., description="탭 또는 쉼표로 구분된 'will,pt' 줄 목록")

class CoreGradeUpdate(BaseModel):
    grade: str = Field(..., description="hero | legend | relic | ancient")

    @field_validator("grade")
    @classmethod
    def validate_grade(cls, v):
        if v not in ("hero", "legend", "relic", "ancient"):
            raise ValueError("등급은 hero, legend, relic, ancient 중 하나여야 합니다.")
        return v

class AssignRequest(BaseModel):
    gem_id: int = Field(..., description="배치할 젬 ID")

# ── 응답 스키마 ──────────────────────────────────────────

class GemResponse(BaseModel):
    id: int
    will: int
    pt: int
    used: bool

class SlotResponse(BaseModel):
    index: int
    gem: Optional[GemResponse]

class CoreResponse(BaseModel):
    id: int
    grade: str
    grade_name: str
    max_will: int
    used_will: int
    total_points: int
    active_effects: list[int]
    slots: list[Optional[GemResponse]]

class BulkResult(BaseModel):
    added: int
    errors: list[str]
    gems: list[GemResponse]

class OptimizeResult(BaseModel):
    total_effects: int
    cores: list[CoreResponse]
    message: str
