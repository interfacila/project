"""
OpenAlex API Integration Module
Fetches academic data (works, authors, institutions) from OpenAlex.
OpenAlex is a free, open catalog of the global research system.
API docs: https://docs.openalex.org/
"""

import time
from typing import Optional

import requests
from sqlalchemy.orm import Session

from models import Academic, Publication, University

OPENALEX_BASE = "https://api.openalex.org"
HEADERS = {
    "User-Agent": "AkademikAI/1.0 (mailto:admin@akademikai.com)",
    "Accept": "application/json",
}
PER_PAGE = 50
REQUEST_DELAY = 0.15


def _get(endpoint: str, params: dict | None = None) -> dict:
    url = f"{OPENALEX_BASE}{endpoint}"
    params = params or {}
    params.setdefault("per_page", PER_PAGE)
    resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    time.sleep(REQUEST_DELAY)
    return resp.json()


# ── Institutions ─────────────────────────────────────────────────────────────

def fetch_institutions(
    db: Session,
    search: str = "",
    country_code: str = "",
    page: int = 1,
    per_page: int = PER_PAGE,
) -> dict:
    """Fetch institutions from OpenAlex and save to DB."""
    params: dict = {"page": page, "per_page": per_page}
    if search:
        params["search"] = search
    if country_code:
        params["filter"] = f"country_code:{country_code}"

    data = _get("/institutions", params)
    saved = 0

    for item in data.get("results", []):
        openalex_id = item.get("id", "")
        name = item.get("display_name", "")
        if not name:
            continue

        existing = db.query(University).filter(University.name == name).first()
        if existing:
            if not existing.website and item.get("homepage_url"):
                existing.website = item["homepage_url"]
            continue

        geo = item.get("geo", {}) or {}
        city = geo.get("city", "")
        country = geo.get("country", "")
        region = country if country else ""

        uni_type = "Devlet"
        if item.get("type") == "company":
            uni_type = "Ozel"
        elif item.get("type") == "nonprofit":
            uni_type = "Vakif"

        uni = University(
            name=name,
            city=city,
            region=region,
            university_type=uni_type,
            website=item.get("homepage_url", ""),
        )
        db.add(uni)
        saved += 1

    db.commit()
    return {
        "total": data.get("meta", {}).get("count", 0),
        "fetched": len(data.get("results", [])),
        "saved": saved,
        "page": page,
    }


# ── Authors ──────────────────────────────────────────────────────────────────

def fetch_authors(
    db: Session,
    search: str = "",
    institution_id: str = "",
    page: int = 1,
    per_page: int = PER_PAGE,
) -> dict:
    """Fetch authors from OpenAlex and save to DB."""
    params: dict = {"page": page, "per_page": per_page}
    if search:
        params["search"] = search

    filters = []
    if institution_id:
        filters.append(f"last_known_institutions.id:{institution_id}")
    if filters:
        params["filter"] = ",".join(filters)

    data = _get("/authors", params)
    saved = 0

    for item in data.get("results", []):
        name = item.get("display_name", "")
        if not name:
            continue

        existing = db.query(Academic).filter(Academic.full_name == name).first()
        if existing:
            continue

        last_inst = (item.get("last_known_institutions") or [{}])
        inst_name = ""
        uni_id = None
        if last_inst and len(last_inst) > 0:
            inst_name = last_inst[0].get("display_name", "")
            if inst_name:
                uni = db.query(University).filter(
                    University.name == inst_name
                ).first()
                if uni:
                    uni_id = uni.id

        topics = item.get("topics", []) or []
        research_areas = ", ".join(
            t.get("display_name", "") for t in topics[:5] if t.get("display_name")
        )

        works_count = item.get("works_count", 0)
        cited_by = item.get("cited_by_count", 0)

        academic = Academic(
            full_name=name,
            title="",
            department="",
            faculty="",
            university_id=uni_id,
            research_areas=research_areas,
            source="OpenAlex",
            profile_url=item.get("id", ""),
        )
        db.add(academic)
        saved += 1

    db.commit()
    return {
        "total": data.get("meta", {}).get("count", 0),
        "fetched": len(data.get("results", [])),
        "saved": saved,
        "page": page,
    }


# ── Works (Publications) ────────────────────────────────────────────────────

def fetch_works(
    db: Session,
    search: str = "",
    author_id: str = "",
    institution_id: str = "",
    from_year: Optional[int] = None,
    to_year: Optional[int] = None,
    page: int = 1,
    per_page: int = PER_PAGE,
) -> dict:
    """Fetch works from OpenAlex and save to DB."""
    params: dict = {"page": page, "per_page": per_page}
    if search:
        params["search"] = search

    filters = []
    if author_id:
        filters.append(f"author.id:{author_id}")
    if institution_id:
        filters.append(f"institutions.id:{institution_id}")
    if from_year:
        filters.append(f"from_publication_date:{from_year}-01-01")
    if to_year:
        filters.append(f"to_publication_date:{to_year}-12-31")
    if filters:
        params["filter"] = ",".join(filters)

    data = _get("/works", params)
    saved = 0

    for item in data.get("results", []):
        title = item.get("title", "")
        if not title:
            continue

        doi = item.get("doi", "") or ""
        if doi:
            existing = db.query(Publication).filter(Publication.doi == doi).first()
            if existing:
                continue

        existing_title = db.query(Publication).filter(
            Publication.title == title
        ).first()
        if existing_title:
            continue

        authorships = item.get("authorships", []) or []
        authors_str = ", ".join(
            a.get("author", {}).get("display_name", "")
            for a in authorships[:10]
            if a.get("author", {}).get("display_name")
        )

        # Try to link to an academic in our DB
        academic_id = None
        if authorships:
            first_author_name = (
                authorships[0].get("author", {}).get("display_name", "")
            )
            if first_author_name:
                acad = db.query(Academic).filter(
                    Academic.full_name == first_author_name
                ).first()
                if acad:
                    academic_id = acad.id

        year = item.get("publication_year")
        journal = ""
        source = item.get("primary_location", {}) or {}
        if source.get("source"):
            journal = source["source"].get("display_name", "")

        pub_type_map = {
            "journal-article": "Makale",
            "book-chapter": "Kitap Bolumu",
            "proceedings-article": "Bildiri",
            "book": "Kitap",
            "dissertation": "Tez",
            "dataset": "Veri Seti",
            "preprint": "On Baski",
        }
        raw_type = item.get("type", "")
        pub_type = pub_type_map.get(raw_type, "Makale")

        pub = Publication(
            title=title,
            authors=authors_str,
            journal=journal,
            year=year,
            doi=doi,
            abstract="",
            citation_count=item.get("cited_by_count", 0),
            publication_type=pub_type,
            academic_id=academic_id,
            source="OpenAlex",
            url=item.get("id", ""),
        )
        db.add(pub)
        saved += 1

    db.commit()
    return {
        "total": data.get("meta", {}).get("count", 0),
        "fetched": len(data.get("results", [])),
        "saved": saved,
        "page": page,
    }


# ── Bulk Sync ────────────────────────────────────────────────────────────────

def sync_openalex_data(
    db: Session,
    search: str = "",
    country_code: str = "TR",
    max_pages: int = 3,
) -> dict:
    """
    Full sync: fetch institutions, then authors, then works from OpenAlex.
    Defaults to Turkish institutions but can be customized.
    """
    results = {
        "institutions": {"total_saved": 0, "total_fetched": 0},
        "authors": {"total_saved": 0, "total_fetched": 0},
        "works": {"total_saved": 0, "total_fetched": 0},
    }

    # 1. Fetch institutions
    for page in range(1, max_pages + 1):
        try:
            r = fetch_institutions(
                db, search=search, country_code=country_code, page=page
            )
            results["institutions"]["total_saved"] += r["saved"]
            results["institutions"]["total_fetched"] += r["fetched"]
            if r["fetched"] < PER_PAGE:
                break
        except Exception as e:
            print(f"Institution fetch error page {page}: {e}")
            break

    # 2. Fetch authors from those institutions
    for page in range(1, max_pages + 1):
        try:
            filter_str = ""
            if country_code:
                filter_str = f"last_known_institutions.country_code:{country_code}"

            params: dict = {"page": page, "per_page": PER_PAGE}
            if search:
                params["search"] = search
            if filter_str:
                params["filter"] = filter_str

            data = _get("/authors", params)
            saved = 0

            for item in data.get("results", []):
                name = item.get("display_name", "")
                if not name:
                    continue

                existing = db.query(Academic).filter(
                    Academic.full_name == name
                ).first()
                if existing:
                    continue

                last_inst = item.get("last_known_institutions") or []
                uni_id = None
                if last_inst:
                    inst_name = last_inst[0].get("display_name", "")
                    if inst_name:
                        uni = db.query(University).filter(
                            University.name == inst_name
                        ).first()
                        if uni:
                            uni_id = uni.id

                topics = item.get("topics", []) or []
                research_areas = ", ".join(
                    t.get("display_name", "")
                    for t in topics[:5]
                    if t.get("display_name")
                )

                academic = Academic(
                    full_name=name,
                    title="",
                    department="",
                    faculty="",
                    university_id=uni_id,
                    research_areas=research_areas,
                    source="OpenAlex",
                    profile_url=item.get("id", ""),
                )
                db.add(academic)
                saved += 1

            db.commit()
            results["authors"]["total_saved"] += saved
            results["authors"]["total_fetched"] += len(
                data.get("results", [])
            )
            if len(data.get("results", [])) < PER_PAGE:
                break
        except Exception as e:
            print(f"Author fetch error page {page}: {e}")
            break

    # 3. Fetch works
    for page in range(1, max_pages + 1):
        try:
            filter_str = ""
            if country_code:
                filter_str = (
                    f"institutions.country_code:{country_code}"
                )

            params_w: dict = {"page": page, "per_page": PER_PAGE}
            if search:
                params_w["search"] = search
            if filter_str:
                params_w["filter"] = filter_str

            data = _get("/works", params_w)
            saved = 0

            for item in data.get("results", []):
                title = item.get("title", "")
                if not title:
                    continue

                doi = item.get("doi", "") or ""
                if doi:
                    existing = db.query(Publication).filter(
                        Publication.doi == doi
                    ).first()
                    if existing:
                        continue

                existing_t = db.query(Publication).filter(
                    Publication.title == title
                ).first()
                if existing_t:
                    continue

                authorships = item.get("authorships", []) or []
                authors_str = ", ".join(
                    a.get("author", {}).get("display_name", "")
                    for a in authorships[:10]
                    if a.get("author", {}).get("display_name")
                )

                academic_id = None
                if authorships:
                    first_name = (
                        authorships[0]
                        .get("author", {})
                        .get("display_name", "")
                    )
                    if first_name:
                        acad = db.query(Academic).filter(
                            Academic.full_name == first_name
                        ).first()
                        if acad:
                            academic_id = acad.id

                year = item.get("publication_year")
                journal = ""
                loc = item.get("primary_location", {}) or {}
                if loc.get("source"):
                    journal = loc["source"].get("display_name", "")

                pub = Publication(
                    title=title,
                    authors=authors_str,
                    journal=journal,
                    year=year,
                    doi=doi,
                    abstract="",
                    citation_count=item.get("cited_by_count", 0),
                    publication_type="Makale",
                    academic_id=academic_id,
                    source="OpenAlex",
                    url=item.get("id", ""),
                )
                db.add(pub)
                saved += 1

            db.commit()
            results["works"]["total_saved"] += saved
            results["works"]["total_fetched"] += len(
                data.get("results", [])
            )
            if len(data.get("results", [])) < PER_PAGE:
                break
        except Exception as e:
            print(f"Works fetch error page {page}: {e}")
            break

    return results


def search_openalex_works(query: str, page: int = 1, per_page: int = 25) -> dict:
    """Search OpenAlex works without saving to DB. Returns raw results."""
    params = {"search": query, "page": page, "per_page": per_page}
    return _get("/works", params)


def search_openalex_authors(query: str, page: int = 1, per_page: int = 25) -> dict:
    """Search OpenAlex authors without saving to DB. Returns raw results."""
    params = {"search": query, "page": page, "per_page": per_page}
    return _get("/authors", params)


def search_openalex_institutions(
    query: str, page: int = 1, per_page: int = 25
) -> dict:
    """Search OpenAlex institutions without saving to DB."""
    params = {"search": query, "page": page, "per_page": per_page}
    return _get("/institutions", params)
