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
    
    @strawberry.field
    def ai_usage_count(self) -> int:
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).date()
        if getattr(self, "last_ai_usage_date", None) == today:
            return getattr(self, "ai_usage_count", 0)
        return 0
    
    @strawberry.field
    def daily_ai_limit(self) -> int:
        from app.core.config import settings
        return settings.DAILY_AI_IMPORT_LIMIT
