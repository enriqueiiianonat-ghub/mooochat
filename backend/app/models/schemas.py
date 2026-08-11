from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ---------- Users ----------
class UserProfile(BaseModel):
    uid: str
    name: str
    email: Optional[str] = None
    avatarUrl: Optional[str] = None  # PLACEHOLDER default: assets/images/default_avatar.png
    presenceStatus: Optional[str] = "offline"  # online | away | busy | offline
    statusMessage: Optional[str] = None        # freeform, e.g. "In a meeting"
    location: Optional[str] = None             # freeform, e.g. "Manila, PH"
    bio: Optional[str] = None
    lastSeen: Optional[datetime] = None


class UpdateUserProfile(BaseModel):
    name: Optional[str] = None
    avatarUrl: Optional[str] = None
    presenceStatus: Optional[str] = None
    statusMessage: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None


# ---------- Contacts ----------
class AddContactRequest(BaseModel):
    contactUid: str


class ContactOut(BaseModel):
    uid: str
    name: str
    avatarUrl: Optional[str] = None
    status: Optional[str] = None


# ---------- Chats ----------
class CreateChatRequest(BaseModel):
    memberUids: List[str]     # includes the creator
    isGroup: bool = False
    groupName: Optional[str] = None
    groupAvatarUrl: Optional[str] = None  # PLACEHOLDER


class ChatOut(BaseModel):
    chatId: str
    isGroup: bool
    name: Optional[str] = None
    avatarUrl: Optional[str] = None
    members: List[str]
    lastMessage: Optional[str] = None
    lastMessageTime: Optional[datetime] = None
    unreadCount: Optional[int] = 0


# ---------- Messages ----------
class SendMessageRequest(BaseModel):
    text: Optional[str] = None
    mediaUrl: Optional[str] = None   # PLACEHOLDER - set after /media/upload
    mediaType: Optional[str] = None  # image | video | file
    replyTo: Optional[str] = None    # messageId being replied to


class MessageOut(BaseModel):
    messageId: str
    chatId: str
    senderId: str
    text: Optional[str] = None
    mediaUrl: Optional[str] = None
    mediaType: Optional[str] = None
    timestamp: datetime
    replyTo: Optional[str] = None
    reactions: Optional[dict] = {}


# ---------- Calls (stub) ----------
class CallOut(BaseModel):
    callId: str
    participants: List[str]
    type: str  # audio | video
    startTime: datetime
    endTime: Optional[datetime] = None
