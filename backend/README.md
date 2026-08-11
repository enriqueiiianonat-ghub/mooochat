# MoooChat Backend (FastAPI)

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      (Windows)
   source venv/bin/activate   (macOS/Linux)
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in real values.
4. Download your Firebase service account JSON from
   Firebase Console > Project Settings > Service Accounts > Generate new private key,
   save it as `serviceAccountKey.json` in this folder (PLACEHOLDER - do not commit this file).
5. Run locally:
   ```
   uvicorn main:app --reload --port 8000
   ```

## Deploy (Render)

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Add the same env vars from `.env` in Render's dashboard (Environment tab).
- Upload `serviceAccountKey.json` contents as a Secret File in Render, or paste the JSON
  into an env var (FIREBASE_CREDENTIALS_JSON) and adjust `app/firebase.py` to load from
  the string instead of a file path.

## Structure

```
backend/
  main.py                 - app entrypoint, CORS, router registration
  app/config.py            - loads env vars
  app/firebase.py          - Firebase Admin SDK init (Firestore + Storage)
  app/dependencies.py       - auth dependency (verifies Firebase ID token)
  app/websocket_manager.py  - in-memory websocket connection manager (per chat room)
  app/models/schemas.py     - Pydantic request/response models
  app/routers/
    auth.py       - /auth/* endpoints
    users.py      - /users/* profile endpoints
    contacts.py   - /contacts/* endpoints
    chats.py      - /chats/* endpoints (list, create direct/group chat)
    messages.py   - /chats/{chat_id}/messages/* + websocket
    media.py      - /media/upload endpoint (Cloud Storage)
    calls.py      - /calls/* endpoints (placeholder/stub - see notes in file)
```
