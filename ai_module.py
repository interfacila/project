import os
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from models import AIQuery, Academic, File, KnowledgeBase, Publication, University

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def get_ai_client():
    if OPENROUTER_API_KEY:
        from openai import OpenAI
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        ), "openrouter"
    if OPENAI_API_KEY:
        from openai import OpenAI
        return OpenAI(api_key=OPENAI_API_KEY), "openai"
    return None, None


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

    # Gather academic context
    uni_count = db.query(University).count()
    acad_count = db.query(Academic).count()
    pub_count = db.query(Publication).count()
    context_parts.append(
        f"Akademik Veritabanı: {uni_count} üniversite, {acad_count} akademisyen, {pub_count} yayın kayıtlı."
    )

    # Search for related academics/universities based on query keywords
    query_words = query_text.lower().split()
    related_academics = []
    for word in query_words:
        if len(word) < 3:
            continue
        found = db.query(Academic).filter(
            Academic.full_name.ilike(f"%{word}%")
            | Academic.department.ilike(f"%{word}%")
            | Academic.research_areas.ilike(f"%{word}%")
        ).limit(5).all()
        related_academics.extend(found)

    # Deduplicate
    seen_ids = set()
    unique_academics = []
    for a in related_academics:
        if a.id not in seen_ids:
            seen_ids.add(a.id)
            unique_academics.append(a)

    if unique_academics:
        acad_text = "\n".join(
            f"- {a.title} {a.full_name} | {a.university.name if a.university else 'Bilinmeyen'} | "
            f"Bölüm: {a.department} | Araştırma: {a.research_areas}"
            for a in unique_academics[:10]
        )
        context_parts.append(f"İlgili Akademisyenler:\n{acad_text}")

    # Related universities
    related_unis = []
    for word in query_words:
        if len(word) < 3:
            continue
        found = db.query(University).filter(
            University.name.ilike(f"%{word}%")
            | University.city.ilike(f"%{word}%")
        ).limit(5).all()
        related_unis.extend(found)

    seen_uni_ids = set()
    unique_unis = []
    for u in related_unis:
        if u.id not in seen_uni_ids:
            seen_uni_ids.add(u.id)
            unique_unis.append(u)

    if unique_unis:
        uni_text = "\n".join(
            f"- {u.name} | {u.city}, {u.region} | Tür: {u.university_type}"
            for u in unique_unis[:10]
        )
        context_parts.append(f"İlgili Üniversiteler:\n{uni_text}")

    context = "\n\n".join(context_parts) if context_parts else "Henüz veri yok."

    # Try AI (OpenRouter or OpenAI)
    client, provider = get_ai_client()
    if client:
        try:
            model = "google/gemini-2.0-flash-001" if provider == "openrouter" else "gpt-4o-mini"
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Sen bir akademik asistan yapay zekasısın. "
                            "Dünya genelindeki üniversiteler, akademisyenler, "
                            "araştırma projeleri ve yayınlar hakkında kapsamlı "
                            "bilgiye sahipsin. Veritabanındaki dosyalar, bilgi tabanı "
                            "ve akademik veriler ile ilgili sorulara Türkçe olarak yardımcı ol. "
                            "Akademisyenlerin araştırma alanları, projeleri ve yayınları "
                            "hakkında detaylı bilgi ver.\n\n"
                            f"Bağlam:\n{context}"
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
    response_parts: list[str] = []

    # Search files
    files = db.query(File).all()
    matching_files = [
        f for f in files
        if query_lower in f.original_filename.lower()
        or query_lower in (f.description or "").lower()
    ]

    # Search knowledge base
    knowledge = db.query(KnowledgeBase).all()
    matching_kb = [
        k for k in knowledge
        if query_lower in k.title.lower() or query_lower in k.content.lower()
    ]

    # Search academics
    academics = db.query(Academic).all()
    matching_acad = [
        a for a in academics
        if query_lower in a.full_name.lower()
        or query_lower in (a.department or "").lower()
        or query_lower in (a.research_areas or "").lower()
    ]

    # Search universities
    universities = db.query(University).all()
    matching_uni = [
        u for u in universities
        if query_lower in u.name.lower()
        or query_lower in (u.city or "").lower()
    ]

    # Search publications
    publications = db.query(Publication).all()
    matching_pub = [
        p for p in publications
        if query_lower in p.title.lower()
        or query_lower in (p.authors or "").lower()
        or query_lower in (p.journal or "").lower()
    ]

    if matching_files:
        response_parts.append("📁 Eşleşen dosyalar:")
        for f in matching_files[:5]:
            response_parts.append(f"  - {f.original_filename} ({f.category})")

    if matching_kb:
        response_parts.append("\n📚 Bilgi tabanından:")
        for k in matching_kb[:5]:
            response_parts.append(f"  - {k.title}: {k.content[:200]}...")

    if matching_uni:
        response_parts.append("\n🏛️ Üniversiteler:")
        for u in matching_uni[:10]:
            response_parts.append(f"  - {u.name} | {u.city}, {u.region} | {u.university_type}")

    if matching_acad:
        response_parts.append("\n👨‍🏫 Akademisyenler:")
        for a in matching_acad[:10]:
            uni_name = a.university.name if a.university else "Bilinmeyen"
            response_parts.append(
                f"  - {a.title} {a.full_name} | {uni_name} | "
                f"Araştırma: {a.research_areas}"
            )

    if matching_pub:
        response_parts.append("\n📄 Yayınlar:")
        for p in matching_pub[:10]:
            response_parts.append(
                f"  - {p.title} | {p.journal} ({p.year}) | "
                f"Atıf: {p.citation_count}"
            )

    if not response_parts:
        total_files = db.query(File).count()
        total_uni = db.query(University).count()
        total_acad = db.query(Academic).count()
        total_pub = db.query(Publication).count()
        response_parts.append(
            f"Sorgunuzla eşleşen sonuç bulunamadı.\n"
            f"Veritabanında {total_files} dosya, {total_uni} üniversite, "
            f"{total_acad} akademisyen, {total_pub} yayın mevcut.\n\n"
            f"💡 İpucu: Daha spesifik anahtar kelimeler deneyin."
        )

    return "\n".join(response_parts)
