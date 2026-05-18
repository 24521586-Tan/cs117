from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.core.supabase import get_supabase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/callback")
async def auth_callback(code: str = Query(...)):
    """Exchange OAuth code for a session and upsert user profile."""
    sb = get_supabase()

    try:
        session = sb.auth.exchange_code_for_session({"auth_code": code})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth exchange failed: {e}")

    user = session.user
    if not user:
        raise HTTPException(status_code=400, detail="No user in session")

    # Upsert profile
    sb.table("profiles").upsert(
        {
            "id": user.id,
            "email": user.email,
            "google_access_token": (user.user_metadata or {}).get("provider_token", ""),
            "google_refresh_token": (user.user_metadata or {}).get("provider_refresh_token", ""),
        },
        on_conflict="id",
    ).execute()

    access_token = session.session.access_token if session.session else ""
    return {"access_token": access_token, "user": {"id": user.id, "email": user.email}}
