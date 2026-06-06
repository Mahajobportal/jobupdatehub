"""
SarkariJob MH — Scraper with sample data fallback
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}

SAMPLE_JOBS = [
    {"title": "Maharashtra Police Constable Bharti 2025", "org": "Maharashtra Police Recruitment Board", "link": "https://mahapolice.gov.in", "date": "15 July 2025", "desc": "17,471 posts. 12th Pass. Age 18-28. Salary 21,700-69,100/month.", "category": "police", "badge": "hot", "posts": "17,471", "qual": "12th Pass", "loc": "Maharashtra"},
    {"title": "MPSC Rajyaseva Pariksha 2025", "org": "Maharashtra Public Service Commission", "link": "https://mpsc.gov.in", "date": "30 June 2025", "desc": "Group A and B posts. 824 vacancies. Graduate level exam.", "category": "other", "badge": "new", "posts": "824", "qual": "Graduate", "loc": "Maharashtra"},
    {"title": "SBI Clerk Recruitment 2025", "org": "State Bank of India", "link": "https://sbi.co.in", "date": "18 July 2025", "desc": "13,735 posts across India. Graduate required. Salary 26,000+.", "category": "banking", "badge": "hot", "posts": "13,735", "qual": "Graduate", "loc": "All India"},
    {"title": "NHM Maharashtra Nurse Recruitment 2025", "org": "National Health Mission Maharashtra", "link": "https://nhmmaharashtra.org", "date": "5 July 2025", "desc": "Nurse, ANM, Staff Nurse posts. 2,800 vacancies. Walk-in interview.", "category": "health", "badge": "new", "posts": "2,800", "qual": "GNM / BSc Nursing", "loc": "Rural Maharashtra"},
    {"title": "RRB NTPC 2025 Railway Recruitment", "org": "Railway Recruitment Board", "link": "https://rrbapply.gov.in", "date": "20 July 2025", "desc": "11,558 posts. 12th and Graduate level. Junior Clerk, Station Master.", "category": "railway", "badge": "hot", "posts": "11,558", "qual": "12th / Graduate", "loc": "All India"},
    {"title": "Bombay High Court Clerk Bharti 2025", "org": "Bombay High Court", "link": "https://bombayhighcourt.nic.in", "date": "10 June 2025", "desc": "312 posts. Typing required. Mumbai/Nagpur posting.", "category": "psu", "badge": "new", "posts": "312", "qual": "Graduate + Typing", "loc": "Mumbai / Nagpur"},
    {"title": "ZP Pune Group C Bharti 2025", "org": "Zilla Parishad Pune", "link": "https://pune.gov.in", "date": "25 July 2025", "desc": "Various posts. Local candidates preferred.", "category": "other", "badge": "new", "posts": "450", "qual": "10th / 12th Pass", "loc": "Pune, Maharashtra"},
    {"title": "MSRTC Driver & Conductor Bharti 2025", "org": "Maharashtra State Road Transport", "link": "https://msrtc.gov.in", "date": "1 August 2025", "desc": "Driver and Conductor recruitment. Heavy vehicle license required.", "category": "other", "badge": "hot", "posts": "3,200", "qual": "10th Pass + License", "loc": "Maharashtra"},
]


def scrape_jobs(max_pages=3):
    all_jobs = []
    try:
        url = "https://www.majhinaukri.in/"
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        posts = soup.select("article, .post-item")
        for post in posts[:20]:
            title_tag = post.select_one("h2 a, h3 a, .entry-title a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag.get("href", "")
            date_tag = post.select_one("time, .entry-date")
            date_str = date_tag.get_text(strip=True) if date_tag else "N/A"
            desc_tag = post.select_one(".entry-summary p, p")
            desc = desc_tag.get_text(strip=True)[:250] if desc_tag else ""
            all_jobs.append({"title": title, "link": link, "date": date_str, "desc": desc, "category": "other", "badge": "new", "scraped_at": datetime.now().isoformat()})
    except Exception as e:
        print(f"[Scraper] Live scraping failed: {e}")

    if not all_jobs:
        print("[Scraper] Using sample data")
        all_jobs = SAMPLE_JOBS

    return all_jobs


def save_to_json(jobs, path="jobs.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"[Scraper] Saved {len(jobs)} jobs")


if __name__ == "__main__":
    jobs = scrape_jobs()
    save_to_json(jobs)
