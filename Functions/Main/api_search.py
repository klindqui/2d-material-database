from __future__ import annotations

import requests
import re
from typing import List, Dict, Any
import importlib

from Classes import report_class
from Classes import database_class

importlib.reload(report_class)
importlib.reload(database_class)

api_key = "012cf183af413f450f324ca7c004223b"
base_url = "https://api.springernature.com/openaccess/json"
headers = {
    "User-Agent": "2D-Materials-DB/1.0 (katlindquist6282@gmail.com)"
}
path = r"C:\Users\kwinw\OneDrive\Desktop\Junior S1\Yang. Lab\Structured Database for 2D Materials\Databases\original_database.json"


def api_search(query: str, 
               p: int, 
               *, 
               max_p: int = 100, 
               timeout: int = 20, 
            ) -> List[Dict[str, Any]]:
    
    if not isinstance(query, str) or not query.strip():
        print("Query must be a non-empty string")
        return []
    
    if not isinstance(p, int) or p <= 0:
        print("Please enter a positive integer.")
        return []
    
    p = min(p, max_p)

    params = {
        "q": query,
        "p": p,
        "api_key": api_key
    }

    try:
        resp = requests.get(
            base_url, 
            params = params, 
            headers = headers,
            timeout = timeout
            )
        resp.raise_for_status()
    except requests.RequestException as e:
        print("Network/API error:", e)
        return []
    
    try:
        data = resp.json()
    except ValueError:
        print("Failed to parse JSON from API response")
        return []

    records = data.get("records", [])
    if not records:
        print("No records returned by the API.")
        return []

    normalized: List[Dict[str, Any]] = []
    for rec in records:
        title = rec.get("title", "N/A")
        doi = rec.get("doi", "N/A")
        urls = rec.get("url", []) or []

        normalized.append({
            "title": title,
            "doi": doi,
            "links": urls, 
        })

    return normalized


def add_to_db(
        results: List[Dict[str, Any]], 
        original_db: database_class.Database
    ) -> None:

    if not results: 
        print("No results, not added to database")
        return
    
    for r in results:
        title = r.get("title", "N/A")
        doi = (r.get("doi") or "").strip()
        if not doi or doi == "N/A":
            continue
        urls = r.get("links", [])

        pdf = next((u.get("value") for u in urls if isinstance(u, dict) and str(u.get("format", "")).lower() == "pdf"), None)
        link_str = pdf or (urls[0].get("value") if urls and isinstance(urls[0], dict) else "")

        report = report_class.Report(doi, title, link_str)
        original_db.add_report(report)


def print_results(
        results: List[Dict[str, Any]]
        ) -> None:
    
    if not results:
        print("No results.")
        return

    for i, r in enumerate(results, start=1):
        print(f"[{i}] Title: {r.get('title', 'N/A')}")
        print(f"    DOI:   {r.get('doi', 'N/A')}")

        links = r.get("links", [])
        if links:
            print("    Links:")
            for u in links:
                if isinstance(u, dict):
                    fmt = (u.get("format") or "unknown").strip()
                    url = (u.get("value") or "").strip()
                    if url:
                        print(f"       - {fmt}: {url}")
                else:
                    print(f"       - {u}")
        else:
            print("    Links: N/A")

        print("-" * 60)


def run_api_search(
        original_db: database_class.Database
        ) -> None:
    
    while True:
        query = input("Please enter a search query: ").strip()
        if re.fullmatch(r"[A-Za-z0-9 ,.\-:+()/\[\]]+", query):
            break
        print("Invalid query, please retry.\n")
        continue

    while True:
        p_raw = input("Please enter the number of reports to search: ").strip()
        if p_raw.isdigit() and int(p_raw) > 0:
            p = int(p_raw)
            break
        print("Please enter a valid positive integer.\n")
        continue

    results = api_search(query, p)
    add_to_db(results = results, original_db = original_db)
    print_results(results)
    original_db.save(path)