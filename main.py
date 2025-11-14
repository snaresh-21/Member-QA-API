# main.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import os

# Imports from your logic & loader modules
from data_loader import fetch_messages
from qa_logic import answer_question, filter_by_name


app = FastAPI(
    title="Member QA API",
    version="1.2.0",
    description=(
        "A lightweight Question-Answering API that interprets member messages "
        "to answer questions like trip plans, cars owned, or favorite restaurants."
    )
)

origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Response Schema ----------
class AskResponse(BaseModel):
    answer: str


# ---------- Health Check ----------
@app.get("/healthz")
def healthz():
    """Simple health check endpoint."""
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}


# ---------- Main QA Endpoint ----------
@app.get("/ask", response_model=AskResponse)
def ask(
    question: str = Query(..., description="Example: 'When is Layla planning her trip?'")
):
    """
    Accept a natural-language question and return an inferred answer.
    """
    try:
        print(f"\n🟩 Incoming question: {question}")

        # Fetch the latest member messages
        corpus = fetch_messages()
        if not corpus:
            print("⚠️ No data fetched from API.")
            raise HTTPException(status_code=502, detail="Failed to fetch messages from API.")

        print(f"✅ Loaded {len(corpus)} messages.")
        print(f"🔹 Sample record keys: {list(corpus[0].keys()) if corpus else 'N/A'}")

        # Generate the answer
        answer = answer_question(question, corpus)
        if not answer:
            answer = "Sorry, I couldn’t find an answer based on the available messages."

        print(f"💬 Final Answer: {answer}\n")
        return AskResponse(answer=answer)

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# ---------- Inspect Messages ----------
@app.get("/inspect")
def inspect(
    name: str = Query("", description="Optional member name to filter messages")
):
    """
    Inspect a subset of messages from the API.
    Useful for debugging and understanding the data.
    """
    try:
        corpus = fetch_messages()
        if not corpus:
            raise HTTPException(status_code=502, detail="Failed to fetch messages from API.")

        sample = corpus[:5]
        if name:
            sample = filter_by_name(corpus, name)[:5]

        return {"count": len(corpus), "sample": sample}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inspecting data: {e}")
