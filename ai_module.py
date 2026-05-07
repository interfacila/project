import os
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from models import AIQuery, File, KnowledgeBase

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def get_openai_client():
    if not OPENAI_API_KEY:
        return None
    from openai import OpenAI
    return OpenAI(api_key=OPENAI_API_KEY)


def query_ai(
    db: Session,
    query_text: str,
    file_id: Optional[int] = None,
    user_id: Optional[int] = None,
) -> str:
    context_parts: list[str] = []

    # Gather context from knowledge base
    knowledge_entries = db.query(KnowledgeBase).limit(10).all()
    if knowledge_entries:
        kb_text = "\n".join(
            f"- {entry.title}: {entry.content[:300]}" for entry in knowledge_entries
        )
        context_parts.append(f"Bilgi Tabanı:\n{kb_text}")

    # Gather context from related file
    if file_id:
        file_record = db.query(File).filter(File.id == file_id).first()
        if file_record:
            context_parts.append(
                f"İlgili Dosya: {file_record.original_filename} "
                f"(Tür: {file_record.file_type}, "
                f"Kategori: {file_record.category}, "
                f"Açıklama: {file_record.description})"
            )

    # Recent files for general context
    recent_files = db.query(File).order_by(File.created_at.desc()).limit(5).all()
    if recent_files:
        files_text = "\n".join(
            f"- {f.original_filename} ({f.category})" for f in recent_files
        )
        context_parts.append(f"Son Dosyalar:\n{files_text}")

    context = "\n\n".join(context_parts) if context_parts else "Henüz veri yok."

    # Try OpenAI
    client = get_openai_client()
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Sen bir akademik asistan yapay zekasısın. "
                            "Veritabanındaki dosyalar ve bilgi tabanı ile ilgili "
                            "sorulara Türkçe olarak yardımcı ol. "
                            "Aşağıdaki bağlam bilgisini kullan:\n\n"
                            f"{context}"
                        ),
                    },
                    {"role": "user", "content": query_text},
                ],
                max_tokens=1000,
                temperature=0.7,
            )
            ai_response = response.choices[0].message.content or "Yanıt alınamadı."
        except Exception as e:
            ai_response = f"AI hatası: {e}"
    else:
        # Fallback: local simple response using database context
        ai_response = generate_local_response(db, query_text, context)

    # Save query to database
    ai_query = AIQuery(
        query_text=query_text,
        response_text=ai_response,
        related_file_id=file_id,
        user_id=user_id,
    )
    db.add(ai_query)
    db.commit()
    db.refresh(ai_query)

    return ai_response


def generate_local_response(db: Session, query: str, context: str) -> str:
    """Fallback AI response using database search when no OpenAI key is configured."""
    query_lower = query.lower()

    # Search files
    files = db.query(File).all()
    matching_files = [
        f
        for f in files
        if query_lower in f.original_filename.lower()
        or query_lower in (f.description or "").lower()
        or query_lower in (f.category or "").lower()
    ]

    # Search knowledge base
    knowledge = db.query(KnowledgeBase).all()
    matching_kb = [
        k
        for k in knowledge
        if query_lower in k.title.lower()
        or query_lower in k.content.lower()
        or query_lower in (k.category or "").lower()
    ]

    response_parts: list[str] = []

    if matching_files:
        response_parts.append("📁 Eşleşen dosyalar:")
        for f in matching_files[:5]:
            response_parts.append(
                f"  - {f.original_filename} (Kategori: {f.category})"
            )

    if matching_kb:
        response_parts.append("\n📚 Bilgi tabanından:")
        for k in matching_kb[:5]:
            response_parts.append(f"  - {k.title}: {k.content[:200]}...")

    if not response_parts:
        total_files = db.query(File).count()
        total_kb = db.query(KnowledgeBase).count()
        response_parts.append(
            f"Sorgunuzla eşleşen sonuç bulunamadı. "
            f"Veritabanında {total_files} dosya ve {total_kb} bilgi kaydı mevcut.\n\n"
            f"💡 İpucu: OpenAI API anahtarı ekleyerek daha gelişmiş AI yanıtları alabilirsiniz. "
            f"(.env dosyasına OPENAI_API_KEY ekleyin)"
        )

    return "\n".join(response_parts)
