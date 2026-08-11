"""
Media upload endpoint - uploads to Firebase Cloud Storage and returns a public
(or signed) URL to store on the message/profile document.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.dependencies import get_current_user
from app.firebase import bucket
import uuid

router = APIRouter(prefix="/media", tags=["media"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "video/mp4", "application/pdf"}  # PLACEHOLDER - adjust as needed


@router.post("/upload")
async def upload_media(file: UploadFile = File(...), user=Depends(get_current_user)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported file type: {file.content_type}")

    ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
    blob_path = f"chat_media/{user['uid']}/{uuid.uuid4()}.{ext}"  # PLACEHOLDER path scheme
    blob = bucket.blob(blob_path)

    contents = await file.read()
    blob.upload_from_string(contents, content_type=file.content_type)
    blob.make_public()  # PLACEHOLDER: switch to signed URLs if content should be private

    return {
        "url": blob.public_url,
        "path": blob_path,
        "contentType": file.content_type,
    }


@router.post("/upload-avatar")
async def upload_avatar(file: UploadFile = File(...), user=Depends(get_current_user)):
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(400, "Avatar must be an image")

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    blob_path = f"avatars/{user['uid']}.{ext}"  # PLACEHOLDER - overwrite existing avatar
    blob = bucket.blob(blob_path)
    contents = await file.read()
    blob.upload_from_string(contents, content_type=file.content_type)
    blob.make_public()

    return {"url": blob.public_url, "path": blob_path}
