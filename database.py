from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./academic_ai.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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
