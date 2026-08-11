from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.firebase import db
from app.models.schemas import UserProfile, UpdateUserProfile
from typing import List

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfile)
async def get_me(user=Depends(get_current_user)):
    doc = db.collection("users").document(user["uid"]).get()
    if not doc.exists:
        raise HTTPException(404, "Profile not found. Call /auth/sync-profile first.")
    return doc.to_dict()


@router.patch("/me", response_model=UserProfile)
async def update_me(payload: UpdateUserProfile, user=Depends(get_current_user)):
    ref = db.collection("users").document(user["uid"])
    updates = {k: v for k, v in payload.dict().items() if v is not None}
    ref.update(updates)
    return ref.get().to_dict()


@router.get("/search", response_model=List[UserProfile])
async def search_users(q: str, user=Depends(get_current_user)):
    """
    Look up other users by exact email, or by name prefix (case-sensitive -
    Firestore has no built-in case-insensitive/full-text search; for that at
    scale later, consider Algolia or Typesense synced from Firestore).
    """
    q = q.strip()
    if not q:
        return []

    results = {}

    email_matches = db.collection("users").where("email", "==", q).limit(10).stream()
    for d in email_matches:
        results[d.id] = d.to_dict()

    name_matches = (
        db.collection("users")
        .where("name", ">=", q)
        .where("name", "<=", q + "\uf8ff")
        .limit(10)
        .stream()
    )
    for d in name_matches:
        results[d.id] = d.to_dict()

    results.pop(user["uid"], None)  # don't show yourself in your own search
    return list(results.values())


@router.get("/{uid}", response_model=UserProfile)
async def get_user(uid: str, user=Depends(get_current_user)):
    doc = db.collection("users").document(uid).get()
    if not doc.exists:
        raise HTTPException(404, "User not found")
    return doc.to_dict()
