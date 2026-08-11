from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import ALLOWED_ORIGINS
from app.routers import auth, users, contacts, chats, messages, media, calls

app = FastAPI(title="MoooChat API", version="0.1.0")

# PLACEHOLDER: tighten allow_origins to your real custom domain before shipping,
# e.g. ["https://moooChat.com"] instead of "*" - see Devgloyd CORS pattern.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
