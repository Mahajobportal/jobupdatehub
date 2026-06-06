"""
SarkariJob MH — Web Scraper
MajiNaukri.com se job data fetch karta hai
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

BASE_URL = "https://www.majhinaukri.in"

CATEGORY_MAP = {
    "police":  "police",
    "teacher": "teacher",
    "bank":    "banking",
    "health":  "health",
    "railway": "railway",
    "court":   "psu",
    "psu":     "psu",
}


def get_category(title: str) -> str:
    title_lower = title.lower()
    for keyword, cat in CATEGORY_MAP.items():
        if keyword in title_lower:
            return cat
    return "other"


def scrape_jobs(max_pages: int = 3) -> list[dict]:
    all_jobs = []

    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/page/{page}/" if page > 1 else f"{BASE_URL}/"
        print(f"[Scraper] Fetching page {page}: {url}")

        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"[Scraper] Error on page {page}: {e}")
            break

        soup = BeautifulSoup(res.text, "html.parser")

        # MajiNaukri post cards — adjust selectors if site changes
        posts = soup.select("article.post, div.post-item, div.entry, article")

        if not posts:
            print(f"[Scraper] No posts found on page {page}, stopping.")
            break

        for post in posts:
            try:
                # Title
                title_tag = post.select_one("h2.entry-title a, h3 a, .post-title a")
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                link  = title_tag.get("href", "")

                # Date
                date_tag = post.select_one("time, .entry-date, .post-date")
                date_str = date_tag.get_text(strip=True) if date_tag else "N/A"

                # Excerpt / description
                desc_tag = post.select_one(".entry-summary p, .post-excerpt, .entry-content p")
                desc = desc_tag.get_text(strip=True)[:300] if desc_tag else ""

                job = {
                    "title":    title,
                    "link":     link,
                    "date":     date_str,
                    "desc":     desc,
                    "category": get_category(title),
                    "badge":    "new",
                    "scraped_at": datetime.now().isoformat(),
                }
                all_jobs.append(job)

            except Exception as e:
                print(f"[Scraper] Parse error: {e}")
                continue

        # Polite delay — don't hammer the server
        time.sleep(2)

    print(f"[Scraper] Total jobs scraped: {len(all_jobs)}")
    return all_jobs


def save_to_json(jobs: list[dict], path: str = "jobs.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"[Scraper] Saved {len(jobs)} jobs → {path}")


if __name__ == "__main__":
    jobs = scrape_jobs(max_pages=3)
    save_to_json(jobs)
