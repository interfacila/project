from sqlalchemy import create_engine, event, Index
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./academic_ai.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable WAL mode so writers don't block readers (fixes UI freezing during OpenAlex sync).
    busy_timeout gives 30s for any locked-write to settle instead of failing immediately."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    # Ensure newly added indexes are also created on pre-existing databases.
    # `create_all` only creates missing indexes for tables it just created,
    # so we explicitly create each index with `checkfirst=True` to be safe.
    for table in Base.metadata.tables.values():
        for index in table.indexes:
            try:
                index.create(bind=engine, checkfirst=True)
            except Exception:  # noqa: BLE001 - best-effort index creation
                pass
    create_indexes()


def create_indexes():
    """Explicit named indexes for hot-path columns used by search/sort.

    These supplement the column-level `index=True` declarations in models.py.
    Idempotent via `checkfirst=True`; safe to run on every startup.
    """
    from models import Publication, Academic, University

    indexes = [
        Index("idx_pub_year", Publication.year),
        Index("idx_pub_citations", Publication.citation_count),
        Index("idx_pub_doi", Publication.doi),
        Index("idx_pub_title", Publication.title),
        Index("idx_pub_authors", Publication.authors),
        Index("idx_acad_uni", Academic.university_id),
        Index("idx_acad_name", Academic.full_name),
        Index("idx_acad_dept", Academic.department),
        Index("idx_acad_research", Academic.research_areas),
        Index("idx_uni_name", University.name),
        Index("idx_uni_city", University.city),
        Index("idx_uni_region", University.region),
    ]

    created = 0
    for idx in indexes:
        try:
            idx.create(engine, checkfirst=True)
            created += 1
        except Exception:  # noqa: BLE001 - best-effort, non-fatal
            pass
    print(f"[OK] {created}/{len(indexes)} named indexes ensured")
