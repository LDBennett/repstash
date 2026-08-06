from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Import models for SQLAlchemy registry
import app.domains.users.models
import app.domains.exercises.models
import app.domains.imports.models
import app.domains.workouts.models

from strawberry.fastapi import GraphQLRouter
from app.api.graphql import schema

from app.api.dependencies import get_current_user
from app.core.database import get_db
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# `get_db` is declared as a dependency both here and inside `get_current_user`;
# FastAPI resolves each `Depends(get_db)` once per request and caches the
# result, so both ends of this graph share the same AsyncSession.
# Note: SQLAlchemy's AsyncSession isn't safe for concurrent use from multiple
# coroutines. A GraphQL request with several top-level fields can run them
# concurrently — today every query/mutation this app sends has exactly one
# top-level field, so this is fine, but keep it in mind if that changes.
async def get_graphql_context(
    request: Request,
    session: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    return {"request": request, "user": user, "session": session}

graphql_app = GraphQLRouter(schema, context_getter=get_graphql_context)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graphql_app, prefix="/graphql")

# Mount the static frontend dist folder if it exists
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.isdir(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if os.path.isdir(frontend_dist):
        return FileResponse(os.path.join(frontend_dist, "index.html"))
    return {"message": "Welcome to RepStash API. Frontend is not built yet."}
