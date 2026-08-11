from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.firebase import db
from app.models.schemas import AddContactRequest, ContactOut
from typing import List

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("", response_model=List[ContactOut])
async def list_contacts(user=Depends(get_current_user)):
    contacts_ref = db.collection("users").document(user["uid"]).collection("contactList")
    docs = contacts_ref.stream()
    result = []
    for d in docs:
        contact_uid = d.id
        profile = db.collection("users").document(contact_uid).get()
        if profile.exists:
            p = profile.to_dict()
            result.append({
                "uid": contact_uid,
                "name": p.get("name"),
                "avatarUrl": p.get("avatarUrl"),
                "status": p.get("presenceStatus"),
            })
    return result


@router.post("", status_code=201)
async def add_contact(payload: AddContactRequest, user=Depends(get_current_user)):
    target = db.collection("users").document(payload.contactUid).get()
    if not target.exists:
        raise HTTPException(404, "User to add not found")

    db.collection("users").document(user["uid"]).collection("contactList").document(
        payload.contactUid
    ).set({"addedAt": None})  # PLACEHOLDER: use firestore.SERVER_TIMESTAMP in real impl

    # optional: mutual add so both see each other in Contacts
    db.collection("users").document(payload.contactUid).collection("contactList").document(
        user["uid"]
    ).set({"addedAt": None})  # PLACEHOLDER

    return {"detail": "Contact added"}


@router.delete("/{contact_uid}")
async def remove_contact(contact_uid: str, user=Depends(get_current_user)):
    db.collection("users").document(user["uid"]).collection("contactList").document(
        contact_uid
    ).delete()
    return {"detail": "Contact removed"}
