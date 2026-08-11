"""
Calls: PLACEHOLDER / STUB.

Real audio/video calling needs a WebRTC signaling layer (this router can act
as the signaling channel over websockets) plus a TURN/STUN server
(e.g. Twilio, or your own coturn instance - PLACEHOLDER: add credentials here).
For now this just logs call metadata to Firestore so the Calls tab has data
to display; wire up WebRTC once you're ready.
"""
from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.firebase import db
from app.models.schemas import CallOut
from typing import List
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/calls", tags=["calls"])


@router.get("", response_model=List[CallOut])
async def list_calls(user=Depends(get_current_user)):
    query = db.collection("calls").where("participants", "array_contains", user["uid"]) \
        .order_by("startTime", direction="DESCENDING").limit(50)
    docs = query.stream()
    return [{"callId": d.id, **d.to_dict()} for d in docs]


@router.post("", response_model=CallOut, status_code=201)
async def log_call(participants: List[str], call_type: str = "audio", user=Depends(get_current_user)):
    call_id = str(uuid.uuid4())
    data = {
        "participants": participants,
        "type": call_type,
        "startTime": datetime.now(timezone.utc),
        "endTime": None,
    }
    db.collection("calls").document(call_id).set(data)
    return {"callId": call_id, **data}
