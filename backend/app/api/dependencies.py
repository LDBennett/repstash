from fastapi import Request, HTTPException
from clerk_backend_api import AuthenticateRequestOptions, Clerk
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.domains.users.models import User
from sqlalchemy import select

clerk_client = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None # Unauthenticated but allows public queries

    try:
        # Verify the session token using Clerk SDK
        request_state = clerk_client.authenticate_request(
            request, 
            AuthenticateRequestOptions()
        )
        if not request_state.is_signed_in or not request_state.payload:
            raise HTTPException(status_code=401, detail="Invalid or expired auth token")

        clerk_id = request_state.payload.get("sub")

        # Provision or fetch user
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.clerk_id == clerk_id))
            user = result.scalar_one_or_none()

            if not user:
                # Auto-provision user on first authenticated request
                email = request_state.payload.get("email", f"{clerk_id}@placeholder.com")
                user = User(clerk_id=clerk_id, email=email)
                session.add(user)
                await session.commit()
                await session.refresh(user)
                
            return user
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
