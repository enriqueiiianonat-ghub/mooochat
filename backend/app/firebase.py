"""
Firebase Admin SDK initialization.
Provides shared Firestore client + Cloud Storage bucket handle used across routers.
"""
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, storage
from app.config import FIREBASE_CREDENTIALS_PATH, FIREBASE_STORAGE_BUCKET

# Check for credentials in Render Environment Variables first
firebase_creds_env = os.environ.get("FIREBASE_CREDENTIALS")

if firebase_creds_env:
    # Production (Render): Parse raw JSON string from environment variable
    cred_dict = json.loads(firebase_creds_env)
    cred = credentials.Certificate(cred_dict)
elif os.path.exists(FIREBASE_CREDENTIALS_PATH):
    # Local Development: Fallback to reading the local JSON file path
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
else:
    raise RuntimeError(
        f"Firebase credentials not found. Set the 'FIREBASE_CREDENTIALS' environment "
        f"variable on Render or provide '{FIREBASE_CREDENTIALS_PATH}' locally."
    )

# Avoid initializing multiple times during app reloads
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "storageBucket": FIREBASE_STORAGE_BUCKET,
    })

db = firestore.client()
bucket = storage.bucket()