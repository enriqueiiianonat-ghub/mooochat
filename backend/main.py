from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import ALLOWED_ORIGINS
from app.routers import auth, users, contacts, chats, messages, media, calls

app = FastAPI(title="MoooChat API", version="0.1.0")

# Define explicitly allowed origins alongside your config setting
origins = [
    "https://mooochat.com",
    "https://www.mooochat.com",
    "http://localhost:8080",  # Common Flutter web dev port
    "http://localhost:3000",
]

# Merge with ALLOWED_ORIGINS if it is defined as a list, or fall back to the explicit origins
if isinstance(ALLOWED_ORIGINS, list):
    origins = list(set(origins + ALLOWED_ORIGINS))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(contacts.router)
app.include_router(chats.router)
app.include_router(messages.router)
app.include_router(media.router)
app.include_router(calls.router)


@app.get("/")
async def root():
    return {"status": "MoooChat API running"}