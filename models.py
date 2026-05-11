import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    files = relationship("File", back_populates="owner")
    queries = relationship("AIQuery", back_populates="user")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_type = Column(String(100))
    file_size = Column(Integer)
    file_path = Column(String(1000), nullable=False)
    description = Column(Text, default="")
    category = Column(String(200), default="Genel")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="files")


class AIQuery(Base):
    __tablename__ = "ai_queries"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text)
    related_file_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="queries")
    related_file = relationship("File")


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(500))
    category = Column(String(200), default="Genel")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    city = Column(String(200), index=True)
    region = Column(String(200), index=True)
    university_type = Column(String(100), index=True)  # Devlet / Vakıf
    website = Column(String(500))
    phone = Column(String(100))
    email = Column(String(200))
    rector = Column(String(300))
    established_year = Column(Integer)
    faculty_count = Column(Integer)
    student_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    academics = relationship("Academic", back_populates="university")


class Academic(Base):
    __tablename__ = "academics"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(500), nullable=False, index=True)
    title = Column(String(200), index=True)  # Prof. Dr., Doç. Dr., Dr. Öğr. Üyesi, vb.
    department = Column(String(500), index=True)
    faculty = Column(String(500))
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=True, index=True)
    email = Column(String(300))
    phone = Column(String(100))
    website = Column(String(500))
    research_areas = Column(Text)
    profile_url = Column(String(500))
    source = Column(String(200))  # YÖK Akademik, Google Scholar, vb.
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    university = relationship("University", back_populates="academics")
    publications = relationship("Publication", back_populates="academic")


class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    authors = Column(Text)
    journal = Column(String(500), index=True)
    year = Column(Integer, index=True)
    doi = Column(String(300))
    abstract = Column(Text)
    citation_count = Column(Integer, default=0)
    publication_type = Column(String(200), index=True)  # Makale, Tez, Bildiri, Kitap
    academic_id = Column(Integer, ForeignKey("academics.id"), nullable=True, index=True)
    source = Column(String(200))
    url = Column(String(500))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    academic = relationship("Academic", back_populates="publications")
