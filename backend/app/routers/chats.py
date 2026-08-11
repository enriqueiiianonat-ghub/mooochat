from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.firebase import db
from app.models.schemas import CreateChatRequest, ChatOut
from typing import List
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("", response_model=List[ChatOut])
async def list_chats(user=Depends(get_current_user)):
    query = db.collection("chats").where("members", "array_contains", user["uid"])
    docs = query.stream()
    chats = []
    for d in docs:
        data = d.to_dict()
        chats.append({
            "chatId": d.id,
            "isGroup": data.get("isGroup", False),
            "name": data.get("name"),
            "avatarUrl": data.get("avatarUrl"),  # PLACEHOLDER for group icon / DM shows other user's avatar client-side
            "members": data.get("members", []),
            "lastMessage": data.get("lastMessage"),
            "lastMessageTime": data.get("lastMessageTime"),
            "unreadCount": data.get("unreadCounts", {}).get(user["uid"], 0),
        })
    chats.sort(key=lambda c: c.get("lastMessageTime") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return chats


@router.post("", response_model=ChatOut, status_code=201)
async def create_chat(payload: CreateChatRequest, user=Depends(get_current_user)):
    if user["uid"] not in payload.memberUids:
        payload.memberUids.append(user["uid"])

    chat_id = str(uuid.uuid4())
    data = {
        "isGroup": payload.isGroup,
        "name": payload.groupName if payload.isGroup else None,
        "avatarUrl": payload.groupAvatarUrl,  # PLACEHOLDER
        "members": payload.memberUids,
        "lastMessage": None,
        "lastMessageTime": datetime.now(timezone.utc),
        "unreadCounts": {uid: 0 for uid in payload.memberUids},
    }
    db.collection("chats").document(chat_id).set(data)
    return {"chatId": chat_id, **data}


@router.get("/{chat_id}", response_model=ChatOut)
async def get_chat(chat_id: str, user=Depends(get_current_user)):
    doc = db.collection("chats").document(chat_id).get()
    if not doc.exists:
        raise HTTPException(404, "Chat not found")
    data = doc.to_dict()
    if user["uid"] not in data.get("members", []):
        raise HTTPException(403, "Not a member of this chat")
    return {"chatId": chat_id, **data, "unreadCount": data.get("unreadCounts", {}).get(user["uid"], 0)}
