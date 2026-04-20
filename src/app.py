from dotenv import load_dotenv
load_dotenv()

from pathlib import Path

from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.rag.answerer import answer
from src.rag.ingest import ingest_pdf
from src.rag.retriever import retrieve
from src.rag.store import collection

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory="src/ui/templates")

app = FastAPI(title="RAG Document Q&A")


class AskRequest(BaseModel):
    question: str


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "collections": [collection.name],
    }


@app.post("/ingest")
async def ingest(file: UploadFile):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        return {"status": "error", "message": "Only PDF files are accepted"}

    save_path = UPLOAD_DIR / file.filename
    content = await file.read()
    save_path.write_bytes(content)

    try:
        chunks = ingest_pdf(str(save_path))
    except Exception as e:
        save_path.unlink(missing_ok=True)
        return {"status": "error", "message": str(e)}
    finally:
        save_path.unlink(missing_ok=True)

    if chunks == 0:
        return {"status": "error", "message": "No text could be extracted from this PDF. It may be image-based or scanned."}

    return {
        "status": "ingested",
        "chunks": chunks,
        "filename": file.filename,
    }


@app.post("/ask")
async def ask(body: AskRequest):
    try:
        chunks = retrieve(body.question)
        result = await answer(body.question, chunks)
        return result
    except Exception as e:
        return {"answer": f"Error: {e}", "sources": []}
