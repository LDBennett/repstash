import strawberry
from typing import Optional
from app.domains.users.models import UnitPreference

@strawberry.enum
class GQLUnitPreference(strawberry.Enum):
    METRIC = "metric"
    IMPERIAL = "imperial"

@strawberry.type
class UserType:
    id: int
    email: str
    unit_preference: GQLUnitPreference
