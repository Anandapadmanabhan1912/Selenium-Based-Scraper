import re
from html import unescape
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )


def get_site_host(url):
    return urlparse(url).netloc.lower().removeprefix("www.")


def get_filename_from_url(url):
    clean_url = url.strip("/").split("/")[-1] or "output"
    clean_url = re.sub(r"[^\w\-.]", "_", clean_url)
    return f"{clean_url}.json"


def parse_url_entry(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    parts = [part.strip() for part in line.split("|")]
    if parts[-1].startswith("http"):
        entry = {
            "url": parts[-1],
            "domain": "",
            "subdomain": "",
            "companyTags": [],
        }
        if len(parts) == 2:
            entry["domain"] = parts[0]
        elif len(parts) >= 3:
            entry["domain"] = parts[0]
            entry["subdomain"] = parts[1]
        return entry

    if line.startswith("http"):
        return {
            "url": line,
            "domain": "",
            "subdomain": "",
            "companyTags": [],
        }
    return None


def strip_html(text):
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def title_from_slug(slug):
    return " ".join(word.capitalize() for word in re.sub(r"[_\-]+", " ", slug or "").split())


def make_question_record(
    question,
    options,
    correct="",
    explanation="",
    domain="",
    subdomain="",
    topic="",
    difficulty="",
    image_link="",
    company_tags=None,
):
    return {
        "domain": domain.strip(),
        "subdomain": subdomain.strip(),
        "topic": topic.strip(),
        "difficulty": difficulty.strip(),
        "question": question.strip(),
        "opt1": options[0].strip() if len(options) > 0 else "",
        "opt2": options[1].strip() if len(options) > 1 else "",
        "opt3": options[2].strip() if len(options) > 2 else "",
        "opt4": options[3].strip() if len(options) > 3 else "",
        "Correct Opt": correct.strip(),
        "Explaination": explanation.strip(),
        "imageLink": image_link.strip(),
        "companyTags": list(company_tags or []),
    }


def apply_metadata_defaults(records, metadata):
    metadata = metadata or {}
    override_domain = metadata.get("domain", "")
    override_subdomain = metadata.get("subdomain", "")
    override_tags = metadata.get("companyTags") or []

    for record in records:
        if override_domain and not record.get("domain"):
            record["domain"] = override_domain
        if override_subdomain and not record.get("subdomain"):
            record["subdomain"] = override_subdomain
        if override_tags and not record.get("companyTags"):
            record["companyTags"] = list(override_tags)
    return records
