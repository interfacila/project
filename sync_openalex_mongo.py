#!/usr/bin/env python3
"""
Bulk sync script: Fetch all Turkish universities, academics, and publications
from OpenAlex and store them in MongoDB.

Usage:
    python sync_openalex_mongo.py                       # Full sync (unis + academics + publications)
    python sync_openalex_mongo.py --only unis            # Only universities
    python sync_openalex_mongo.py --only academics       # Only academics
    python sync_openalex_mongo.py --only publications    # Only publications
    python sync_openalex_mongo.py --resume               # Resume from last cursor
    python sync_openalex_mongo.py --stats                # Show current stats

OpenAlex data for Turkey:
    ~553 institutions
    ~571,000 academics
    ~1,680,000 publications
"""

import argparse
import datetime
import sys
import time

import requests
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

from mongo_db import get_mongo_db, get_sync_status, init_mongo_indexes, update_sync_status

OPENALEX_BASE = "https://api.openalex.org"
HEADERS = {
    "User-Agent": "AkademikAI/1.0 (mailto:admin@akademikai.com)",
    "Accept": "application/json",
}
PER_PAGE = 200
REQUEST_DELAY = 0.1  # polite delay between requests
COUNTRY_CODE = "TR"


def _get(endpoint: str, params: dict) -> dict:
    url = f"{OPENALEX_BASE}{endpoint}"
    params.setdefault("per_page", PER_PAGE)
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            time.sleep(REQUEST_DELAY)
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 429:
                wait = 2 ** (attempt + 1)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            raise
        except requests.exceptions.ConnectionError:
            wait = 5 * (attempt + 1)
            print(f"  Connection error, retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"Failed after 3 attempts: {endpoint}")


def sync_universities():
    """Fetch all Turkish institutions from OpenAlex into MongoDB."""
    db = get_mongo_db()
    print("\n" + "=" * 60)
    print("  SYNCING TURKISH UNIVERSITIES FROM OPENALEX")
    print("=" * 60)

    # Check for resume
    status = get_sync_status("universities")
    cursor = status.get("last_cursor", "*")
    total_saved = status.get("total_saved", 0)
    total_fetched = status.get("total_fetched", 0)

    if cursor != "*":
        print(f"  Resuming from cursor, already fetched: {total_fetched}")

    params = {
        "filter": f"country_code:{COUNTRY_CODE}",
        "per_page": PER_PAGE,
        "cursor": cursor,
    }

    page = 0
    api_total = 0

    while True:
        data = _get("/institutions", params)
        results = data.get("results", [])
        if not results:
            break

        api_total = data.get("meta", {}).get("count", 0)
        page += 1
        total_fetched += len(results)

        # Prepare bulk upserts
        operations = []
        for item in results:
            openalex_id = item.get("id", "")
            name = item.get("display_name", "")
            if not name:
                continue

            geo = item.get("geo", {}) or {}
            inst_type = item.get("type", "")

            uni_type = "Devlet"
            if inst_type == "company":
                uni_type = "Ozel"
            elif inst_type == "nonprofit":
                uni_type = "Vakif"
            elif inst_type == "facility":
                uni_type = "Tesis"
            elif inst_type == "healthcare":
                uni_type = "Saglik"
            elif inst_type == "archive":
                uni_type = "Arsiv"

            doc = {
                "openalex_id": openalex_id,
                "name": name,
                "city": geo.get("city", ""),
                "region": geo.get("region", ""),
                "country": geo.get("country", ""),
                "country_code": geo.get("country_code", "TR"),
                "latitude": geo.get("latitude"),
                "longitude": geo.get("longitude"),
                "type": inst_type,
                "university_type": uni_type,
                "homepage_url": item.get("homepage_url", ""),
                "image_url": item.get("image_url", ""),
                "works_count": item.get("works_count", 0),
                "cited_by_count": item.get("cited_by_count", 0),
                "ror": item.get("ror", ""),
                "lineage": [
                    lid for lid in (item.get("lineage") or [])
                ],
                "associated_institutions": [
                    {
                        "id": ai.get("id", ""),
                        "name": ai.get("display_name", ""),
                        "relationship": ai.get("relationship", ""),
                    }
                    for ai in (item.get("associated_institutions") or [])[:20]
                ],
                "updated_at": datetime.datetime.utcnow(),
            }

            operations.append(
                UpdateOne(
                    {"openalex_id": openalex_id},
                    {"$set": doc, "$setOnInsert": {"created_at": datetime.datetime.utcnow()}},
                    upsert=True,
                )
            )

        if operations:
            try:
                result = db.universities.bulk_write(operations, ordered=False)
                total_saved += result.upserted_count + result.modified_count
            except BulkWriteError as e:
                total_saved += e.details.get("nUpserted", 0) + e.details.get("nModified", 0)

        # Progress
        pct = (total_fetched / api_total * 100) if api_total else 0
        print(f"  [{pct:5.1f}%] Fetched: {total_fetched}/{api_total} | Page: {page}")

        # Save cursor for resume
        next_cursor = data.get("meta", {}).get("next_cursor")
        update_sync_status("universities", {
            "last_cursor": next_cursor or "*",
            "total_fetched": total_fetched,
            "total_saved": total_saved,
            "api_total": api_total,
            "last_sync": datetime.datetime.utcnow(),
        })

        if not next_cursor:
            break
        params["cursor"] = next_cursor

    # Mark complete
    update_sync_status("universities", {
        "last_cursor": "*",
        "total_fetched": total_fetched,
        "total_saved": total_saved,
        "api_total": api_total,
        "completed": True,
        "completed_at": datetime.datetime.utcnow(),
    })

    print(f"\n  Universities sync complete!")
    print(f"  Total from API: {api_total}")
    print(f"  Total fetched: {total_fetched}")
    print(f"  Total saved/updated: {total_saved}")
    return {"api_total": api_total, "fetched": total_fetched, "saved": total_saved}


def sync_academics():
    """Fetch all Turkish academics from OpenAlex into MongoDB."""
    db = get_mongo_db()
    print("\n" + "=" * 60)
    print("  SYNCING TURKISH ACADEMICS FROM OPENALEX")
    print("=" * 60)

    # Check for resume
    status = get_sync_status("academics")
    cursor = status.get("last_cursor", "*")
    total_saved = status.get("total_saved", 0)
    total_fetched = status.get("total_fetched", 0)

    if cursor != "*":
        print(f"  Resuming from cursor, already fetched: {total_fetched}")

    params = {
        "filter": f"last_known_institutions.country_code:{COUNTRY_CODE}",
        "per_page": PER_PAGE,
        "cursor": cursor,
    }

    page = 0
    api_total = 0
    batch_start = time.time()

    while True:
        data = _get("/authors", params)
        results = data.get("results", [])
        if not results:
            break

        api_total = data.get("meta", {}).get("count", 0)
        page += 1
        total_fetched += len(results)

        # Prepare bulk upserts
        operations = []
        for item in results:
            openalex_id = item.get("id", "")
            name = item.get("display_name", "")
            if not name:
                continue

            last_inst = item.get("last_known_institutions") or []
            affiliations = item.get("affiliations") or []
            topics = item.get("topics") or []
            summary_stats = item.get("summary_stats") or {}

            doc = {
                "openalex_id": openalex_id,
                "name": name,
                "display_name_alternatives": item.get("display_name_alternatives", []),
                "works_count": item.get("works_count", 0),
                "cited_by_count": item.get("cited_by_count", 0),
                "h_index": summary_stats.get("h_index", 0),
                "i10_index": summary_stats.get("i10_index", 0),
                "2yr_mean_citedness": summary_stats.get("2yr_mean_citedness", 0),
                "last_known_institutions": [
                    {
                        "id": inst.get("id", ""),
                        "name": inst.get("display_name", ""),
                        "country_code": inst.get("country_code", ""),
                        "type": inst.get("type", ""),
                        "ror": inst.get("ror", ""),
                    }
                    for inst in last_inst
                ],
                "university_openalex_id": last_inst[0].get("id", "") if last_inst else "",
                "university_name": last_inst[0].get("display_name", "") if last_inst else "",
                "affiliations": [
                    {
                        "institution_id": aff.get("institution", {}).get("id", ""),
                        "institution_name": aff.get("institution", {}).get("display_name", ""),
                        "country_code": aff.get("institution", {}).get("country_code", ""),
                        "years": aff.get("years", []),
                    }
                    for aff in affiliations[:30]
                ],
                "topics": [
                    {
                        "name": t.get("display_name", ""),
                        "field": t.get("field", {}).get("display_name", ""),
                        "subfield": t.get("subfield", {}).get("display_name", ""),
                        "domain": t.get("domain", {}).get("display_name", ""),
                    }
                    for t in topics[:10]
                ],
                "research_areas": ", ".join(
                    t.get("display_name", "") for t in topics[:5] if t.get("display_name")
                ),
                "field": topics[0].get("field", {}).get("display_name", "") if topics else "",
                "subfield": topics[0].get("subfield", {}).get("display_name", "") if topics else "",
                "orcid": item.get("orcid", ""),
                "updated_at": datetime.datetime.utcnow(),
            }

            operations.append(
                UpdateOne(
                    {"openalex_id": openalex_id},
                    {"$set": doc, "$setOnInsert": {"created_at": datetime.datetime.utcnow()}},
                    upsert=True,
                )
            )

        if operations:
            try:
                result = db.academics.bulk_write(operations, ordered=False)
                total_saved += result.upserted_count + result.modified_count
            except BulkWriteError as e:
                total_saved += e.details.get("nUpserted", 0) + e.details.get("nModified", 0)

        # Progress
        pct = (total_fetched / api_total * 100) if api_total else 0
        elapsed = time.time() - batch_start
        rate = total_fetched / elapsed if elapsed > 0 else 0
        eta_seconds = (api_total - total_fetched) / rate if rate > 0 else 0
        eta_min = eta_seconds / 60

        print(
            f"  [{pct:5.1f}%] Fetched: {total_fetched:,}/{api_total:,} | "
            f"Rate: {rate:.0f}/s | ETA: {eta_min:.1f}min"
        )

        # Save cursor for resume
        next_cursor = data.get("meta", {}).get("next_cursor")
        update_sync_status("academics", {
            "last_cursor": next_cursor or "*",
            "total_fetched": total_fetched,
            "total_saved": total_saved,
            "api_total": api_total,
            "last_sync": datetime.datetime.utcnow(),
        })

        if not next_cursor:
            break
        params["cursor"] = next_cursor

    # Mark complete
    update_sync_status("academics", {
        "last_cursor": "*",
        "total_fetched": total_fetched,
        "total_saved": total_saved,
        "api_total": api_total,
        "completed": True,
        "completed_at": datetime.datetime.utcnow(),
    })

    print(f"\n  Academics sync complete!")
    print(f"  Total from API: {api_total:,}")
    print(f"  Total fetched: {total_fetched:,}")
    print(f"  Total saved/updated: {total_saved:,}")
    return {"api_total": api_total, "fetched": total_fetched, "saved": total_saved}


def sync_publications():
    """Fetch all Turkish publications from OpenAlex into MongoDB."""
    db = get_mongo_db()
    print("\n" + "=" * 60)
    print("  SYNCING TURKISH PUBLICATIONS FROM OPENALEX")
    print("=" * 60)

    # Check for resume
    status = get_sync_status("publications")
    cursor = status.get("last_cursor", "*")
    total_saved = status.get("total_saved", 0)
    total_fetched = status.get("total_fetched", 0)

    if cursor != "*":
        print(f"  Resuming from cursor, already fetched: {total_fetched}")

    params = {
        "filter": f"institutions.country_code:{COUNTRY_CODE}",
        "per_page": PER_PAGE,
        "cursor": cursor,
        "sort": "publication_year:desc",
    }

    page = 0
    api_total = 0
    batch_start = time.time()

    while True:
        data = _get("/works", params)
        results = data.get("results", [])
        if not results:
            break

        api_total = data.get("meta", {}).get("count", 0)
        page += 1
        total_fetched += len(results)

        # Prepare bulk upserts
        operations = []
        for item in results:
            openalex_id = item.get("id", "")
            title = item.get("title", "")
            if not title:
                continue

            authorships = item.get("authorships", []) or []
            authors = []
            author_ids = []
            institution_ids = []
            for auth in authorships[:20]:
                author_obj = auth.get("author", {})
                if author_obj.get("display_name"):
                    authors.append({
                        "name": author_obj.get("display_name", ""),
                        "openalex_id": author_obj.get("id", ""),
                        "orcid": author_obj.get("orcid", ""),
                    })
                    if author_obj.get("id"):
                        author_ids.append(author_obj["id"])
                for inst in auth.get("institutions", []):
                    if inst.get("id") and inst["id"] not in institution_ids:
                        institution_ids.append(inst["id"])

            journal = ""
            loc = item.get("primary_location", {}) or {}
            if loc.get("source"):
                journal = loc["source"].get("display_name", "")

            oa = item.get("open_access", {}) or {}

            doc = {
                "openalex_id": openalex_id,
                "title": title,
                "authors": authors,
                "authors_str": ", ".join(a["name"] for a in authors[:10]),
                "author_openalex_ids": author_ids,
                "institution_openalex_ids": institution_ids,
                "journal": journal,
                "year": item.get("publication_year"),
                "doi": item.get("doi", ""),
                "type": item.get("type", ""),
                "cited_by_count": item.get("cited_by_count", 0),
                "is_open_access": oa.get("is_oa", False),
                "oa_url": oa.get("oa_url", ""),
                "url": item.get("id", ""),
                "abstract_inverted_index": bool(item.get("abstract_inverted_index")),
                "concepts": [
                    {"name": c.get("display_name", ""), "score": c.get("score", 0)}
                    for c in (item.get("concepts") or [])[:10]
                ],
                "updated_at": datetime.datetime.utcnow(),
            }

            operations.append(
                UpdateOne(
                    {"openalex_id": openalex_id},
                    {"$set": doc, "$setOnInsert": {"created_at": datetime.datetime.utcnow()}},
                    upsert=True,
                )
            )

        if operations:
            try:
                result = db.publications.bulk_write(operations, ordered=False)
                total_saved += result.upserted_count + result.modified_count
            except BulkWriteError as e:
                total_saved += e.details.get("nUpserted", 0) + e.details.get("nModified", 0)

        # Progress
        pct = (total_fetched / api_total * 100) if api_total else 0
        elapsed = time.time() - batch_start
        rate = total_fetched / elapsed if elapsed > 0 else 0
        eta_seconds = (api_total - total_fetched) / rate if rate > 0 else 0
        eta_min = eta_seconds / 60

        print(
            f"  [{pct:5.1f}%] Fetched: {total_fetched:,}/{api_total:,} | "
            f"Rate: {rate:.0f}/s | ETA: {eta_min:.1f}min"
        )

        # Save cursor for resume
        next_cursor = data.get("meta", {}).get("next_cursor")
        update_sync_status("publications", {
            "last_cursor": next_cursor or "*",
            "total_fetched": total_fetched,
            "total_saved": total_saved,
            "api_total": api_total,
            "last_sync": datetime.datetime.utcnow(),
        })

        if not next_cursor:
            break
        params["cursor"] = next_cursor

    # Mark complete
    update_sync_status("publications", {
        "last_cursor": "*",
        "total_fetched": total_fetched,
        "total_saved": total_saved,
        "api_total": api_total,
        "completed": True,
        "completed_at": datetime.datetime.utcnow(),
    })

    print(f"\n  Publications sync complete!")
    print(f"  Total from API: {api_total:,}")
    print(f"  Total fetched: {total_fetched:,}")
    print(f"  Total saved/updated: {total_saved:,}")
    return {"api_total": api_total, "fetched": total_fetched, "saved": total_saved}


def show_stats():
    """Show current MongoDB stats."""
    db = get_mongo_db()
    uni_count = db.universities.count_documents({})
    acad_count = db.academics.count_documents({})
    pub_count = db.publications.count_documents({})

    uni_status = get_sync_status("universities")
    acad_status = get_sync_status("academics")
    pub_status = get_sync_status("publications")

    print("\n" + "=" * 60)
    print("  MONGODB STATS")
    print("=" * 60)
    print(f"  Universities in MongoDB:  {uni_count:,}")
    print(f"  Academics in MongoDB:     {acad_count:,}")
    print(f"  Publications in MongoDB:  {pub_count:,}")
    print()

    for label, status in [("Universite", uni_status), ("Akademisyen", acad_status), ("Yayin", pub_status)]:
        if status:
            completed = "Tamamlandi" if status.get("completed") else "Devam ediyor"
            print(f"  {label} sync: {completed}")
            print(f"    API toplam: {status.get('api_total', 0):,}")
            print(f"    Cekilen: {status.get('total_fetched', 0):,}")
            if status.get("last_sync"):
                print(f"    Son sync: {status['last_sync']}")

    # Sample data
    if acad_count > 0:
        print("\n  Son eklenen 3 akademisyen:")
        for a in db.academics.find().sort("created_at", -1).limit(3):
            print(f"    - {a.get('name', '')} | {a.get('university_name', '')} | h-index: {a.get('h_index', 0)}")

    if pub_count > 0:
        print("\n  Son eklenen 3 yayin:")
        for p in db.publications.find().sort("created_at", -1).limit(3):
            print(f"    - {p.get('title', '')[:80]} | {p.get('journal', '')} | {p.get('year', '')} | Atif: {p.get('cited_by_count', 0)}")

    if uni_count > 0:
        print("\n  Son eklenen 3 universite:")
        for u in db.universities.find().sort("created_at", -1).limit(3):
            print(f"    - {u.get('name', '')} | {u.get('city', '')} | works: {u.get('works_count', 0):,}")


def reset_sync(sync_type: str = "all"):
    """Reset sync status (for re-running from scratch)."""
    db = get_mongo_db()
    if sync_type in ("all", "universities"):
        db.sync_status.delete_one({"sync_type": "universities"})
        print("  Universities sync status reset.")
    if sync_type in ("all", "academics"):
        db.sync_status.delete_one({"sync_type": "academics"})
        print("  Academics sync status reset.")
    if sync_type in ("all", "publications"):
        db.sync_status.delete_one({"sync_type": "publications"})
        print("  Publications sync status reset.")


def main():
    parser = argparse.ArgumentParser(description="Sync Turkish academic data from OpenAlex to MongoDB")
    parser.add_argument("--only", choices=["unis", "academics", "publications"], help="Sync only universities, academics, or publications")
    parser.add_argument("--resume", action="store_true", help="Resume from last sync point")
    parser.add_argument("--stats", action="store_true", help="Show current stats")
    parser.add_argument("--reset", choices=["all", "unis", "academics", "publications"], help="Reset sync status")
    args = parser.parse_args()

    if args.stats:
        show_stats()
        return

    if args.reset:
        reset_sync(args.reset)
        return

    # Initialize indexes
    init_mongo_indexes()

    if not args.resume:
        # Reset cursors for fresh sync
        if not args.only or args.only == "unis":
            reset_sync("universities")
        if not args.only or args.only == "academics":
            reset_sync("academics")
        if not args.only or args.only == "publications":
            reset_sync("publications")

    start_time = time.time()

    if not args.only or args.only == "unis":
        sync_universities()

    if not args.only or args.only == "academics":
        sync_academics()

    if not args.only or args.only == "publications":
        sync_publications()

    elapsed = time.time() - start_time
    print(f"\n  Total time: {elapsed / 60:.1f} minutes")
    print()
    show_stats()


if __name__ == "__main__":
    main()
