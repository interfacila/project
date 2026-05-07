import os
import uuid
from pathlib import Path
from typing import Optional

import aiofiles
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse as FastAPIFileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from ai_module import query_ai
from database import get_db, init_db
from models import File as FileModel
from models import KnowledgeBase, User
from schemas import (
    AIQueryRequest,
    AIQueryResponse,
    FileResponse,
    FileUpdate,
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
    UserCreate,
    UserResponse,
)

app = FastAPI(
    title="Akademik AI Aggregator",
    description="Akademik dosya yönetimi ve yapay zeka destekli bilgi sistemi",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def startup():
    init_db()


# ─── Frontend ────────────────────────────────────────────────────────────────

@app.get("/")
async def serve_frontend():
    return FastAPIFileResponse("static/index.html")


# ─── User Endpoints ─────────────────────────────────────────────────────────

@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Kullanıcı zaten mevcut")
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/api/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# ─── File Endpoints ──────────────────────────────────────────────────────────

@app.post("/api/files", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(""),
    category: str = Form("Genel"),
    owner_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
):
    ext = Path(file.filename or "unknown").suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / unique_name

    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    db_file = FileModel(
        filename=unique_name,
        original_filename=file.filename or "unknown",
        file_type=file.content_type or "application/octet-stream",
        file_size=len(content),
        file_path=str(file_path),
        description=description,
        category=category,
        owner_id=owner_id,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


@app.get("/api/files", response_model=list[FileResponse])
def list_files(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(FileModel)
    if category:
        query = query.filter(FileModel.category == category)
    if search:
        query = query.filter(
            FileModel.original_filename.ilike(f"%{search}%")
            | FileModel.description.ilike(f"%{search}%")
        )
    return query.order_by(FileModel.created_at.desc()).all()


@app.get("/api/files/{file_id}", response_model=FileResponse)
def get_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    return db_file


@app.put("/api/files/{file_id}", response_model=FileResponse)
def update_file(file_id: int, update: FileUpdate, db: Session = Depends(get_db)):
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    if update.description is not None:
        db_file.description = update.description
    if update.category is not None:
        db_file.category = update.category
    db.commit()
    db.refresh(db_file)
    return db_file


@app.delete("/api/files/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    file_path = Path(db_file.file_path)
    if file_path.exists():
        file_path.unlink()
    db.delete(db_file)
    db.commit()
    return {"detail": "Dosya silindi"}


@app.get("/api/files/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    return FastAPIFileResponse(
        path=db_file.file_path,
        filename=db_file.original_filename,
        media_type=db_file.file_type or "application/octet-stream",
    )


# ─── Knowledge Base Endpoints ───────────────────────────────────────────────

@app.post("/api/knowledge", response_model=KnowledgeBaseResponse)
def create_knowledge(entry: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    db_entry = KnowledgeBase(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@app.get("/api/knowledge", response_model=list[KnowledgeBaseResponse])
def list_knowledge(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(KnowledgeBase)
    if category:
        query = query.filter(KnowledgeBase.category == category)
    if search:
        query = query.filter(
            KnowledgeBase.title.ilike(f"%{search}%")
            | KnowledgeBase.content.ilike(f"%{search}%")
        )
    return query.order_by(KnowledgeBase.created_at.desc()).all()


@app.put("/api/knowledge/{entry_id}", response_model=KnowledgeBaseResponse)
def update_knowledge(
    entry_id: int,
    update: KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
):
    db_entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Bilgi kaydı bulunamadı")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(db_entry, field, value)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@app.delete("/api/knowledge/{entry_id}")
def delete_knowledge(entry_id: int, db: Session = Depends(get_db)):
    db_entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Bilgi kaydı bulunamadı")
    db.delete(db_entry)
    db.commit()
    return {"detail": "Bilgi kaydı silindi"}


# ─── AI Endpoints ────────────────────────────────────────────────────────────

@app.post("/api/ai/query", response_model=AIQueryResponse)
def ai_query(request: AIQueryRequest, db: Session = Depends(get_db)):
    response_text = query_ai(
        db=db,
        query_text=request.query,
        file_id=request.file_id,
        user_id=request.user_id,
    )
    from models import AIQuery

    last_query = (
        db.query(AIQuery)
        .order_by(AIQuery.created_at.desc())
        .first()
    )
    return last_query


@app.get("/api/ai/history", response_model=list[AIQueryResponse])
def ai_history(db: Session = Depends(get_db)):
    from models import AIQuery

    return db.query(AIQuery).order_by(AIQuery.created_at.desc()).limit(50).all()


# ─── Stats ───────────────────────────────────────────────────────────────────

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    from models import AIQuery

    return {
        "total_files": db.query(FileModel).count(),
        "total_users": db.query(User).count(),
        "total_queries": db.query(AIQuery).count(),
        "total_knowledge": db.query(KnowledgeBase).count(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
