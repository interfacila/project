import threading
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
from database import SessionLocal, get_db, init_db
from models import Academic, File as FileModel
from models import KnowledgeBase, Publication, University, User
from openalex_module import (
    fetch_authors,
    fetch_institutions,
    fetch_works,
    search_openalex_authors,
    search_openalex_institutions,
    search_openalex_works,
    sync_openalex_data,
)
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
    description="Akademik dosya yonetimi ve yapay zeka destekli bilgi sistemi",
    version="2.0.0",
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

# Track background sync status
_sync_status: dict = {
    "running": False,
    "last_result": None,
    "error": None,
    "phase": None,
    "phase_fetched": 0,
    "phase_total": 0,
    "progress": {},
}
_sync_lock = threading.Lock()


def _auto_sync_if_empty():
    """Auto-sync Turkish data from OpenAlex if the database is empty."""
    db = SessionLocal()
    try:
        uni_count = db.query(University).count()
        acad_count = db.query(Academic).count()
        if uni_count > 0 and acad_count > 0:
            print(f"[AutoSync] DB already has {uni_count} universities, {acad_count} academics. Skipping.")
            return

        print("[AutoSync] Empty database detected. Starting full Turkish data sync...")
        with _sync_lock:
            if _sync_status["running"]:
                return
            _sync_status["running"] = True
            _sync_status["error"] = None
            _sync_status["phase"] = "starting"

        def _progress_cb(phase: str, fetched: int, total: int, results: dict):
            with _sync_lock:
                _sync_status["phase"] = phase
                _sync_status["phase_fetched"] = fetched
                _sync_status["phase_total"] = total
                _sync_status["progress"] = {
                    k: v.copy() for k, v in results.items()
                }

        sync_db = SessionLocal()
        try:
            result = sync_openalex_data(
                sync_db, country_code="TR", progress_cb=_progress_cb,
            )
            with _sync_lock:
                _sync_status["last_result"] = result
                _sync_status["phase"] = "completed"
            print(f"[AutoSync] Completed: {result}")
        except Exception as e:
            with _sync_lock:
                _sync_status["error"] = str(e)
                _sync_status["phase"] = "error"
            print(f"[AutoSync] Error: {e}")
        finally:
            sync_db.close()
            with _sync_lock:
                _sync_status["running"] = False
    finally:
        db.close()


@app.on_event("startup")
def startup():
    init_db()
    thread = threading.Thread(target=_auto_sync_if_empty, daemon=True)
    thread.start()


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


# ─── University Endpoints ────────────────────────────────────────────────────

@app.get("/api/universities")
def list_universities(
    search: Optional[str] = None,
    city: Optional[str] = None,
    region: Optional[str] = None,
    university_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(University)
    if search:
        query = query.filter(
            University.name.ilike(f"%{search}%")
            | University.city.ilike(f"%{search}%")
        )
    if city:
        query = query.filter(University.city.ilike(f"%{city}%"))
    if region:
        query = query.filter(University.region.ilike(f"%{region}%"))
    if university_type:
        query = query.filter(University.university_type == university_type)
    results = query.order_by(University.name).all()
    return [
        {
            "id": u.id, "name": u.name, "city": u.city, "region": u.region,
            "type": u.university_type, "website": u.website,
            "established": u.established_year, "academic_count": len(u.academics),
        }
        for u in results
    ]


@app.get("/api/universities/{uni_id}")
def get_university(uni_id: int, db: Session = Depends(get_db)):
    uni = db.query(University).filter(University.id == uni_id).first()
    if not uni:
        raise HTTPException(status_code=404, detail="Üniversite bulunamadı")
    return {
        "id": uni.id, "name": uni.name, "city": uni.city, "region": uni.region,
        "type": uni.university_type, "website": uni.website,
        "established": uni.established_year,
        "academics": [
            {"id": a.id, "name": a.full_name, "title": a.title, "department": a.department}
            for a in uni.academics
        ],
    }


# ─── Academic Endpoints ─────────────────────────────────────────────────────

@app.get("/api/academics")
def list_academics(
    search: Optional[str] = None,
    university_id: Optional[int] = None,
    title: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Academic)
    if search:
        query = query.filter(
            Academic.full_name.ilike(f"%{search}%")
            | Academic.department.ilike(f"%{search}%")
            | Academic.research_areas.ilike(f"%{search}%")
        )
    if university_id:
        query = query.filter(Academic.university_id == university_id)
    if title:
        query = query.filter(Academic.title.ilike(f"%{title}%"))
    results = query.order_by(Academic.full_name).all()
    return [
        {
            "id": a.id, "name": a.full_name, "title": a.title,
            "department": a.department, "faculty": a.faculty,
            "university": a.university.name if a.university else None,
            "university_id": a.university_id,
            "research_areas": a.research_areas, "email": a.email,
            "source": a.source,
        }
        for a in results
    ]


@app.get("/api/academics/{academic_id}")
def get_academic(academic_id: int, db: Session = Depends(get_db)):
    acad = db.query(Academic).filter(Academic.id == academic_id).first()
    if not acad:
        raise HTTPException(status_code=404, detail="Akademisyen bulunamadı")
    return {
        "id": acad.id, "name": acad.full_name, "title": acad.title,
        "department": acad.department, "faculty": acad.faculty,
        "university": acad.university.name if acad.university else None,
        "research_areas": acad.research_areas, "email": acad.email,
        "profile_url": acad.profile_url,
        "publications": [
            {"id": p.id, "title": p.title, "journal": p.journal, "year": p.year}
            for p in acad.publications
        ],
    }


@app.get("/api/academics/{academic_id}/publications/openalex")
def get_academic_publications_from_openalex(academic_id: int, db: Session = Depends(get_db)):
    """Fetch publications from OpenAlex using the academic's OpenAlex author ID."""
    acad = db.query(Academic).filter(Academic.id == academic_id).first()
    if not acad:
        raise HTTPException(status_code=404, detail="Akademisyen bulunamadı")

    if not acad.profile_url:
        return {"results": [], "total": 0, "author_stats": {}}

    openalex_id = acad.profile_url
    if openalex_id.startswith("https://openalex.org/"):
        openalex_id = openalex_id.replace("https://openalex.org/", "")

    try:
        from openalex_module import _get

        # Fetch author profile for h-index, i10-index, cited_by_count, affiliations
        author_stats = {}
        affiliation_info = {}
        try:
            author_data = _get(f"/authors/{openalex_id}", {})
            summary = author_data.get("summary_stats", {})
            author_stats = {
                "h_index": summary.get("h_index", 0),
                "i10_index": summary.get("i10_index", 0),
                "cited_by_count": author_data.get("cited_by_count", 0),
                "works_count": author_data.get("works_count", 0),
            }

            # Extract affiliation info
            last_institutions = author_data.get("last_known_institutions", [])
            if last_institutions:
                inst = last_institutions[0]
                affiliation_info["university"] = inst.get("display_name", "")
                affiliation_info["country"] = inst.get("country_code", "")

            # Extract topics as field/department info
            topics = author_data.get("topics", [])
            if topics:
                top_topic = topics[0]
                affiliation_info["field"] = top_topic.get("field", {}).get("display_name", "")
                affiliation_info["subfield"] = top_topic.get("subfield", {}).get("display_name", "")
                affiliation_info["domain"] = top_topic.get("domain", {}).get("display_name", "")

            # All affiliations history
            affiliations = author_data.get("affiliations", [])
            affiliation_info["affiliations"] = [
                {
                    "institution": aff.get("institution", {}).get("display_name", ""),
                    "country": aff.get("institution", {}).get("country_code", ""),
                    "years": aff.get("years", []),
                }
                for aff in affiliations
            ]
        except Exception:
            pass

        # Fetch publications
        data = _get("/works", {"filter": f"author.id:{openalex_id}", "per_page": 50, "sort": "publication_year:desc"})
        results = []
        for item in data.get("results", []):
            authorships = item.get("authorships", []) or []
            authors_str = ", ".join(
                a.get("author", {}).get("display_name", "")
                for a in authorships[:5]
                if a.get("author", {}).get("display_name")
            )
            journal = ""
            loc = item.get("primary_location", {}) or {}
            if loc.get("source"):
                journal = loc["source"].get("display_name", "")
            results.append({
                "title": item.get("title", ""),
                "authors": authors_str,
                "journal": journal,
                "year": item.get("publication_year"),
                "doi": item.get("doi", ""),
                "citations": item.get("cited_by_count", 0),
                "type": item.get("type", ""),
                "url": item.get("id", ""),
            })
        return {
            "results": results,
            "total": data.get("meta", {}).get("count", 0),
            "author_stats": author_stats,
            "affiliation_info": affiliation_info,
        }
    except (KeyError, ValueError, ConnectionError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/academics/{academic_id}/publications/scholar")
def get_academic_publications_from_scholar(academic_id: int, db: Session = Depends(get_db)):
    """Fetch publications from Google Scholar using the academic's name."""
    acad = db.query(Academic).filter(Academic.id == academic_id).first()
    if not acad:
        raise HTTPException(status_code=404, detail="Akademisyen bulunamadı")

    try:
        from scholar_module import search_google_scholar
        result = search_google_scholar(acad.full_name)
        return result
    except (ConnectionError, TimeoutError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/academics/{academic_id}/publications/yok")
def get_academic_publications_from_yok(academic_id: int, db: Session = Depends(get_db)):
    """Fetch publications from YÖK Akademik using the academic's name."""
    acad = db.query(Academic).filter(Academic.id == academic_id).first()
    if not acad:
        raise HTTPException(status_code=404, detail="Akademisyen bulunamadı")

    try:
        from yok_module import search_yok_academic
        result = search_yok_academic(acad.full_name)
        return result
    except (ConnectionError, TimeoutError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ─── Publication Endpoints ───────────────────────────────────────────────────

@app.get("/api/publications")
def list_publications(
    search: Optional[str] = None,
    academic_id: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Publication)
    if search:
        query = query.filter(
            Publication.title.ilike(f"%{search}%")
            | Publication.authors.ilike(f"%{search}%")
            | Publication.journal.ilike(f"%{search}%")
        )
    if academic_id:
        query = query.filter(Publication.academic_id == academic_id)
    if year:
        query = query.filter(Publication.year == year)
    results = query.order_by(Publication.year.desc()).all()
    return [
        {
            "id": p.id, "title": p.title, "authors": p.authors,
            "journal": p.journal, "year": p.year, "doi": p.doi,
            "type": p.publication_type, "citations": p.citation_count,
            "academic": p.academic.full_name if p.academic else None,
        }
        for p in results
    ]


# ─── OpenAlex Endpoints ─────────────────────────────────────────────────────

@app.post("/api/openalex/sync")
def openalex_sync(
    search: str = "",
    country_code: str = "TR",
):
    """Trigger a full OpenAlex sync (institutions + authors + works)."""
    with _sync_lock:
        if _sync_status["running"]:
            return {"detail": "Senkronizasyon zaten devam ediyor", "status": "running"}
        _sync_status["running"] = True
        _sync_status["error"] = None
        _sync_status["phase"] = "starting"

    def _progress_cb(phase: str, fetched: int, total: int, results: dict):
        with _sync_lock:
            _sync_status["phase"] = phase
            _sync_status["phase_fetched"] = fetched
            _sync_status["phase_total"] = total
            _sync_status["progress"] = {
                k: v.copy() for k, v in results.items()
            }

    def _run_sync():
        sync_db = SessionLocal()
        try:
            result = sync_openalex_data(
                sync_db, search=search, country_code=country_code,
                progress_cb=_progress_cb,
            )
            with _sync_lock:
                _sync_status["last_result"] = result
                _sync_status["phase"] = "completed"
        except Exception as e:
            with _sync_lock:
                _sync_status["error"] = str(e)
                _sync_status["phase"] = "error"
        finally:
            sync_db.close()
            with _sync_lock:
                _sync_status["running"] = False

    thread = threading.Thread(target=_run_sync, daemon=True)
    thread.start()

    return {"detail": "Senkronizasyon baslatildi", "status": "started"}


@app.get("/api/openalex/sync/status")
def openalex_sync_status():
    """Check the status of the current or last OpenAlex sync."""
    return _sync_status


@app.get("/api/openalex/search/works")
def openalex_search_works_endpoint(query: str, page: int = 1):
    """Search OpenAlex works directly (live search, not saved to DB)."""
    try:
        data = search_openalex_works(query, page=page)
        results = []
        for item in data.get("results", []):
            authorships = item.get("authorships", []) or []
            authors_str = ", ".join(
                a.get("author", {}).get("display_name", "")
                for a in authorships[:5]
                if a.get("author", {}).get("display_name")
            )
            journal = ""
            loc = item.get("primary_location", {}) or {}
            if loc.get("source"):
                journal = loc["source"].get("display_name", "")

            results.append({
                "title": item.get("title", ""),
                "authors": authors_str,
                "journal": journal,
                "year": item.get("publication_year"),
                "doi": item.get("doi", ""),
                "citations": item.get("cited_by_count", 0),
                "type": item.get("type", ""),
                "url": item.get("id", ""),
                "open_access": item.get("open_access", {}).get("is_oa", False),
            })
        return {
            "total": data.get("meta", {}).get("count", 0),
            "results": results,
            "page": page,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/openalex/search/authors")
def openalex_search_authors_endpoint(query: str, page: int = 1):
    """Search OpenAlex authors directly."""
    try:
        data = search_openalex_authors(query, page=page)
        results = []
        for item in data.get("results", []):
            last_inst = item.get("last_known_institutions") or []
            institution = last_inst[0].get("display_name", "") if last_inst else ""
            topics = item.get("topics", []) or []
            areas = ", ".join(
                t.get("display_name", "") for t in topics[:5]
                if t.get("display_name")
            )
            results.append({
                "name": item.get("display_name", ""),
                "institution": institution,
                "works_count": item.get("works_count", 0),
                "cited_by_count": item.get("cited_by_count", 0),
                "research_areas": areas,
                "url": item.get("id", ""),
            })
        return {
            "total": data.get("meta", {}).get("count", 0),
            "results": results,
            "page": page,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/openalex/search/institutions")
def openalex_search_institutions_endpoint(query: str, page: int = 1):
    """Search OpenAlex institutions directly."""
    try:
        data = search_openalex_institutions(query, page=page)
        results = []
        for item in data.get("results", []):
            geo = item.get("geo", {}) or {}
            results.append({
                "name": item.get("display_name", ""),
                "city": geo.get("city", ""),
                "country": geo.get("country", ""),
                "type": item.get("type", ""),
                "works_count": item.get("works_count", 0),
                "cited_by_count": item.get("cited_by_count", 0),
                "url": item.get("id", ""),
                "homepage": item.get("homepage_url", ""),
            })
        return {
            "total": data.get("meta", {}).get("count", 0),
            "results": results,
            "page": page,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/openalex/import/works")
def openalex_import_works(
    search: str = "",
    page: int = 1,
    per_page: int = 50,
    db: Session = Depends(get_db),
):
    """Import works from OpenAlex into local DB."""
    result = fetch_works(db, search=search, page=page, per_page=per_page)
    return result


@app.post("/api/openalex/import/authors")
def openalex_import_authors(
    search: str = "",
    page: int = 1,
    per_page: int = 50,
    db: Session = Depends(get_db),
):
    """Import authors from OpenAlex into local DB."""
    result = fetch_authors(db, search=search, page=page, per_page=per_page)
    return result


@app.post("/api/openalex/import/institutions")
def openalex_import_institutions(
    search: str = "",
    country_code: str = "",
    page: int = 1,
    per_page: int = 50,
    db: Session = Depends(get_db),
):
    """Import institutions from OpenAlex into local DB."""
    result = fetch_institutions(
        db, search=search, country_code=country_code, page=page, per_page=per_page,
    )
    return result


# ─── Stats ───────────────────────────────────────────────────────────────────

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    from models import AIQuery

    return {
        "total_files": db.query(FileModel).count(),
        "total_users": db.query(User).count(),
        "total_queries": db.query(AIQuery).count(),
        "total_knowledge": db.query(KnowledgeBase).count(),
        "total_universities": db.query(University).count(),
        "total_academics": db.query(Academic).count(),
        "total_publications": db.query(Publication).count(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
