from app.models.gem import Gem
from app.models.core import Core, GRADES
from app.schemas import GemResponse, CoreResponse

def gem_to_response(gem: Gem | None) -> GemResponse | None:
    if gem is None:
        return None
    return GemResponse(id=gem.id, will=gem.will, pt=gem.pt, used=gem.used)

def core_to_response(core: Core) -> CoreResponse:
    grade = GRADES[core.grade]
    return CoreResponse(
        id=core.id,
        grade=core.grade,
        grade_name=grade["name"],
        max_will=grade["max_will"],
        used_will=sum(s.will for s in core.slots if s),
        total_points=core.total_points(),
        active_effects=core.active_effects(),
        slots=[gem_to_response(s) for s in core.slots],
    )
