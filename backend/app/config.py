import os
from dotenv import load_dotenv

load_dotenv()

FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "./serviceAccountKey.json")  # PLACEHOLDER
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "your-project-id.appspot.com")  # PLACEHOLDER

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,https://your-custom-domain.com"  # PLACEHOLDER - tighten before prod
).split(",")

JWT_SECRET = os.getenv("JWT_SECRET", "REPLACE_WITH_RANDOM_SECRET")  # PLACEHOLDER
