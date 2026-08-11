from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from app.dependencies import get_current_user
from app.firebase import db
from app.models.schemas import SendMessageRequest, MessageOut
from app.websocket_manager import manager
from typing import List
from datetime import datetime, timezone
import uuid
from firebase_admin import auth as firebase_auth

router = APIRouter(tags=["messages"])


@router.get("/chats/{chat_id}/messages", response_model=List[MessageOut])
async def list_messages(chat_id: str, limit: int = 50, user=Depends(get_current_user)):
    chat_doc = db.collection("chats").document(chat_id).get()
    if not chat_doc.exists or user["uid"] not in chat_doc.to_dict().get("members", []):
        raise HTTPException(403, "Not a member of this chat")

    msgs_ref = (
        db.collection("chats").document(chat_id).collection("messages")
        .order_by("timestamp", direction="DESCENDING").limit(limit)
    )
    docs = msgs_ref.stream()
    result = []
    for d in docs:
        data = d.to_dict()
        result.append({"messageId": d.id, "chatId": chat_id, **data})
    result.reverse()
    return result


@router.post("/chats/{chat_id}/messages", response_model=MessageOut, status_code=201)
async def send_message(chat_id: str, payload: SendMessageRequest, user=Depends(get_current_user)):
    chat_ref = db.collection("chats").document(chat_id)
    chat_doc = chat_ref.get()
    if not chat_doc.exists or user["uid"] not in chat_doc.to_dict().get("members", []):
        raise HTTPException(403, "Not a member of this chat")

    message_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    data = {
        "senderId": user["uid"],
        "text": payload.text,
        "mediaUrl": payload.mediaUrl,     # PLACEHOLDER - comes from /media/upload response
        "mediaType": payload.mediaType,
        "timestamp": now,
        "replyTo": payload.replyTo,
        "reactions": {},
    }
    chat_ref.collection("messages").document(message_id).set(data)

    # update chat preview + unread counts for everyone except sender
    members = chat_doc.to_dict().get("members", [])
    unread = chat_doc.to_dict().get("unreadCounts", {})
    for m in members:
        if m != user["uid"]:
            unread[m] = unread.get(m, 0) + 1
    chat_ref.update({
        "lastMessage": payload.text or f"[{payload.mediaType or 'media'}]",
        "lastMessageTime": now,
        "unreadCounts": unread,
    })

    out = {"messageId": message_id, "chatId": chat_id, **data}
    await manager.broadcast(chat_id, out_to_json(out))
    return out


def out_to_json(msg: dict) -> dict:
    # datetime isn't directly JSON serializable for websocket send_json
    m = dict(msg)
    m["timestamp"] = m["timestamp"].isoformat()
    return m


@router.websocket("/ws/chats/{chat_id}")
async def chat_websocket(websocket: WebSocket, chat_id: str, token: str):
    """
    Connect from Flutter with: ws://<host>/ws/chats/{chat_id}?token=<Firebase ID token>
    Broadcasts new messages sent via POST /chats/{chat_id}/messages in real time.
    """
    try:
        firebase_auth.verify_id_token(token)
    except Exception:
        await websocket.close(code=4401)
        return

    await manager.connect(chat_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # keep-alive / typing indicators could be sent here
    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)
