from app.api.routes.auth import router as auth_router
from app.api.routes.teams import router as teams_router
from app.api.routes.events import router as events_router
from app.api.routes.challenges import router as challenges_router

__all__ = [
    "auth_router",
    "teams_router",
    "events_router",
    "challenges_router",
]