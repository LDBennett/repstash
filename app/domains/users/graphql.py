import strawberry
import enum

@strawberry.enum
class GQLUnitPreference(enum.Enum):
    METRIC = "metric"
    IMPERIAL = "imperial"

@strawberry.type
class UserType:
    id: int
    email: str
    unit_preference: GQLUnitPreference
