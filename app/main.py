from fastapi import FastAPI
from app.core.config import settings

# Import models for SQLAlchemy registry
import app.domains.users.models
import app.domains.exercises.models
import app.domains.imports.models
import app.domains.workouts.models

import strawberry
from strawberry.fastapi import GraphQLRouter
from app.api.graphql import schema

graphql_app = GraphQLRouter(schema)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
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
