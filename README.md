# Member-QA API (FastAPI + Docker)

A lightweight question-answering API that reads public **member messages** and answers natural-language questions like:

- “When is Layla planning her trip to London?”
- “How many cars does Vikram Desai have?”
- “What are Amira’s favorite restaurants?”

The service exposes `/ask` and returns:
```json
{ "answer": "..." }

Features

FastAPI app with interactive docs (/docs, /redoc)

/ask: NL question → heuristic extraction (dates, counts, favorites)

/inspect: peek at the messages corpus (with optional name filter)

/healthz: simple health check (used by hosts like Render)

Dockerized with Gunicorn + Uvicorn workers

CORS configurable via ALLOWED_ORIGINS

Robust loader that supports {"items":[...]} and common alternates



Quickstart
A) Run locally (no Docker)

PowerShell

pip install -r requirements.txt
$env:MESSAGES_API_URL="https://november7-730026606190.europe-west1.run.app/messages"
uvicorn main:app --port 10000 --reload


bash

pip install -r requirements.txt
export MESSAGES_API_URL="https://november7-730026606190.europe-west1.run.app/messages"
uvicorn main:app --port 10000 --reload


Open:

http://localhost:10000/healthz

http://localhost:10000/docs

B) Docker (recommended)

Build:

docker build -t member-qa-api:latest .


Run:

docker run --rm -p 10000:10000 \
  -e PORT=10000 \
  -e ENV=prod \
  -e MESSAGES_API_URL=https://november7-730026606190.europe-west1.run.app/messages \
  -e ALLOWED_ORIGINS="*" \
  --name member-qa member-qa-api:latest
