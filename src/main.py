from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="SOL Agent (stub)")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/sol/status")
def status():
    return {"ok": True, "version": "stub", "services": ["sol_agent"]}

class ResumeReq(BaseModel):
    task: Optional[str] = None
@app.post("/sol/resume")
def resume(req: ResumeReq):
    return {"resumed": req.task or "default"}

class SaveReq(BaseModel):
    name: str
    notes: Optional[str] = None
@app.post("/sol/save")
def save(req: SaveReq):
    return {"saved": req.name, "notes": req.notes}

class LoadReq(BaseModel):
    model: Optional[str] = None
    profile: Optional[str] = None
@app.post("/sol/load")
def load(req: LoadReq):
    return {"loaded": {"model": req.model, "profile": req.profile}}

def _mem_body():
    return '{"id":1,"text":"placeholder"}\n{"id":2,"text":"placeholder2"}\n'

@app.post("/sol/memory/export")
def mem_export_post():
    return Response(content=_mem_body(), media_type="application/x-ndjson")

@app.get("/sol/memory/export")
def mem_export_get():
    return Response(content=_mem_body(), media_type="application/x-ndjson")
