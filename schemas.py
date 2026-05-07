import datetime
from typing import Optional

from pydantic import BaseModel


# --- User Schemas ---
class UserCreate(BaseModel):
    username: str
    email: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


# --- File Schemas ---
class FileResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    description: str
    category: str
    owner_id: Optional[int] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class FileUpdate(BaseModel):
    description: Optional[str] = None
    category: Optional[str] = None


# --- AI Query Schemas ---
class AIQueryRequest(BaseModel):
    query: str
    file_id: Optional[int] = None
    user_id: Optional[int] = None


class AIQueryResponse(BaseModel):
    id: int
    query_text: str
    response_text: Optional[str] = None
    related_file_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


# --- Knowledge Base Schemas ---
class KnowledgeBaseCreate(BaseModel):
    title: str
    content: str
    source: Optional[str] = None
    category: str = "Genel"


class KnowledgeBaseResponse(BaseModel):
    id: int
    title: str
    content: str
    source: Optional[str] = None
    category: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class KnowledgeBaseUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None
