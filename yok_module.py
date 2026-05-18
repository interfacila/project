"""YÖK Akademik integration - scrapes akademik.yok.gov.tr for academic data."""

import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://akademik.yok.gov.tr/AkademikArama"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}


def search_yok_academic(name: str) -> dict:
    """Search YÖK Akademik for an academic by name.

    Returns a dict with profile info and publications found.
    """
    try:
        parts = name.strip().split()
        if len(parts) < 2:
            return {"profile": {}, "publications": [], "error": "Ad ve soyad gerekli"}

        search_url = f"{BASE_URL}/AkademisyenGoworma"
        form_data = {
            "islem": "",
            "Ession": "",
            "surname": parts[-1],
            "name": " ".join(parts[:-1]),
        }

        session = requests.Session()
        session.headers.update(HEADERS)
        resp = session.post(search_url, data=form_data, timeout=(5, 10))

        if resp.status_code != 200:
            return {"profile": {}, "publications": [], "error": f"HTTP {resp.status_code}"}

        soup = BeautifulSoup(resp.text, "html.parser")
        academics = []

        rows = soup.select("table tr") or soup.select(".gs_ai_chpr") or soup.select("a[href*='authorId']")
        for row in rows:
            link = row.find("a", href=True)
            if link and "authorId" in link.get("href", ""):
                href = link["href"]
                author_id = href.split("authorId=")[-1].split("&")[0] if "authorId=" in href else ""
                academics.append({
                    "name": link.get_text(strip=True),
                    "author_id": author_id,
                    "url": f"{BASE_URL}/{href}" if not href.startswith("http") else href,
                })

        if not academics:
            links = soup.find_all("a", href=True)
            for link in links:
                href = link.get("href", "")
                if "authorId" in href:
                    author_id = href.split("authorId=")[-1].split("&")[0]
                    academics.append({
                        "name": link.get_text(strip=True),
                        "author_id": author_id,
                        "url": f"{BASE_URL}/{href}" if not href.startswith("http") else href,
                    })

        if not academics:
            return {"profile": {}, "publications": [], "error": None}

        best_match = academics[0]
        profile = _fetch_profile(session, best_match["author_id"])
        profile["name"] = best_match["name"]
        profile["yok_url"] = best_match["url"]

        return {
            "profile": profile,
            "publications": profile.pop("publications", []),
            "total": profile.pop("total", 0),
            "error": None,
        }
    except requests.Timeout:
        return {"profile": {}, "publications": [], "error": "YÖK Akademik zaman aşımı"}
    except requests.ConnectionError:
        return {"profile": {}, "publications": [], "error": "YÖK Akademik bağlantı hatası"}
    except Exception as e:
        logger.error("YÖK Akademik error: %s", e)
        return {"profile": {}, "publications": [], "error": str(e)}


def _fetch_profile(session: requests.Session, author_id: str) -> dict:
    """Fetch academic profile from YÖK Akademik by authorId."""
    if not author_id:
        return {"publications": [], "total": 0}

    url = f"{BASE_URL}/AkademisyenGorevOgrenimBilgileri"
    params = {"islem": "direct", "authorId": author_id}

    try:
        resp = session.get(url, params=params, timeout=(5, 10))
        if resp.status_code != 200:
            return {"publications": [], "total": 0}

        soup = BeautifulSoup(resp.text, "html.parser")

        profile = {
            "author_id": author_id,
            "university": "",
            "faculty": "",
            "department": "",
            "title": "",
            "publications": [],
            "total": 0,
        }

        info_sections = soup.select(".panel-body") or soup.select("table")
        for section in info_sections:
            text = section.get_text(" ", strip=True)
            if "Üniversite" in text or "üniversite" in text:
                parts = text.split(":")
                if len(parts) > 1:
                    profile["university"] = parts[1].strip().split("\n")[0].strip()

        pubs = _fetch_publications(session, author_id)
        profile["publications"] = pubs
        profile["total"] = len(pubs)

        return profile
    except Exception as e:
        logger.error("YÖK profile fetch error: %s", e)
        return {"publications": [], "total": 0}


def _fetch_publications(session: requests.Session, author_id: str) -> list:
    """Fetch publications from YÖK Akademik academic profile."""
    publications = []

    pub_types = [
        ("getMakaleBilgisiV1", "Makale"),
        ("getBildiriBilgisiV1", "Bildiri"),
        ("getKitapBilgisiV1", "Kitap"),
    ]

    for endpoint, pub_type in pub_types:
        try:
            url = f"{BASE_URL}/AkademisyenYayinBilgileri"
            params = {"islem": endpoint, "authorId": author_id}
            resp = session.get(url, params=params, timeout=(5, 10))

            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select(".yayin-item") or soup.select("table tr") or soup.select("li")

            for item in items:
                title_elem = item.find("strong") or item.find("b") or item.find("a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                pub = {
                    "title": title,
                    "type": pub_type,
                    "authors": "",
                    "journal": "",
                    "year": "",
                }

                text = item.get_text(" ", strip=True)
                import re
                year_match = re.search(r"\b(19|20)\d{2}\b", text)
                if year_match:
                    pub["year"] = year_match.group()

                publications.append(pub)
        except Exception:
            continue

    return publications
