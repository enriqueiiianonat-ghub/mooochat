"""
Firebase Admin SDK initialization.
Provides shared Firestore client + Cloud Storage bucket handle used across routers.
"""
import firebase_admin
from firebase_admin import credentials, firestore, storage
from app.config import FIREBASE_CREDENTIALS_PATH, FIREBASE_STORAGE_BUCKET

# PLACEHOLDER: make sure serviceAccountKey.json exists at FIREBASE_CREDENTIALS_PATH
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred, {
    "storageBucket": FIREBASE_STORAGE_BUCKET,
})

db = firestore.client()
bucket = storage.bucket()
