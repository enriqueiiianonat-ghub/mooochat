"""
Auth notes:
MoooChat uses Firebase Authentication directly from the Flutter client
(email/password, Google, etc via firebase_auth package). The backend does NOT
issue its own passwords - it only verifies the Firebase ID token per-request
(see app/dependencies.py::get_current_user).

This router just exposes a lightweight "sync profile" endpoint that
creates/updates the Firestore users/{uid} document the first time a client
signs in, so downstream routers (contacts, chats) have a profile to read.
"""
from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.firebase import db
from app.models.schemas import UserProfile
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sync-profile", response_model=UserProfile)
async def sync_profile(user=Depends(get_current_user)):
    ref = db.collection("users").document(user["uid"])
    doc = ref.get()
    if not doc.exists:
        data = {
            "uid": user["uid"],
            "name": user.get("name") or "New User",
            "email": user.get("email"),
            "avatarUrl": None,  # PLACEHOLDER - default_avatar.png shown client-side if null
            "presenceStatus": "online",
            "statusMessage": None,
            "location": None,
            "bio": None,
            "lastSeen": datetime.now(timezone.utc),
        }
        ref.set(data)
        return data
    ref.update({"presenceStatus": "online", "lastSeen": datetime.now(timezone.utc)})
    return doc.to_dict()
