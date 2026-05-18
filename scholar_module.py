"""Google Scholar integration using the scholarly library."""

import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

logger = logging.getLogger(__name__)

SCHOLAR_TIMEOUT = 10  # seconds


def _do_search(name: str) -> dict:
    """Run the scholarly search in a thread (blocks on network I/O)."""
    import socket
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(SCHOLAR_TIMEOUT)
    try:
        from scholarly import scholarly

        results = scholarly.search_author(name)
        author = next(results, None)
        if not author:
            return {"author_stats": {}, "publications": [], "error": None}

        filled = scholarly.fill(author, sections=["basics", "indices", "publications"])

        author_stats = {
            "h_index": filled.get("hindex", 0) or 0,
            "i10_index": filled.get("i10index", 0) or 0,
            "cited_by_count": filled.get("citedby", 0) or 0,
            "scholar_id": filled.get("scholar_id", ""),
            "name": filled.get("name", ""),
            "affiliation": filled.get("affiliation", ""),
            "interests": filled.get("interests", []),
            "url_picture": filled.get("url_picture", ""),
        }

        publications = []
        for pub in filled.get("publications", [])[:50]:
            bib = pub.get("bib", {})
            publications.append({
                "title": bib.get("title", ""),
                "authors": bib.get("author", ""),
                "journal": bib.get("journal", bib.get("venue", "")),
                "year": bib.get("pub_year", ""),
                "citations": pub.get("num_citations", 0),
                "url": pub.get("pub_url", pub.get("author_pub_id", "")),
            })

        return {
            "author_stats": author_stats,
            "publications": publications,
            "total": len(filled.get("publications", [])),
            "error": None,
        }
    finally:
        socket.setdefaulttimeout(old_timeout)


def search_google_scholar(name: str) -> dict:
    """Search Google Scholar for an academic by name with timeout.

    Returns a dict with author_stats and publications.
    """
    try:
        from scholarly import scholarly  # noqa: F401
    except ImportError:
        return {"author_stats": {}, "publications": [], "error": "scholarly kutuphanesi yuklu degil"}

    try:
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(_do_search, name)
        try:
            return future.result(timeout=SCHOLAR_TIMEOUT)
        except FutureTimeout:
            executor.shutdown(wait=False)
            return {"author_stats": {}, "publications": [], "error": "Google Scholar zaman asimi (sunucu engellemis olabilir)"}
        finally:
            executor.shutdown(wait=False)
    except FutureTimeout:
        return {"author_stats": {}, "publications": [], "error": "Google Scholar zaman asimi (sunucu engellemis olabilir)"}
    except StopIteration:
        return {"author_stats": {}, "publications": [], "error": None}
    except Exception as e:
        logger.error("Google Scholar error: %s", e)
        return {"author_stats": {}, "publications": [], "error": str(e)}
