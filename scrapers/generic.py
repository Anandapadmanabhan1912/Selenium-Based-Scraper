import re
import time

from selenium.webdriver.common.by import By

from scrapers.base import BaseScraper
from scrapers.text_parser import parse_mcqs_from_lines
from scrapers.utils import apply_metadata_defaults, get_site_host

CONTENT_SELECTORS = {
    "gyansetu.in": [".entry-content", "article"],
    "geeksforgeeks.org": ["article .text", "article"],
    "indiabix.com": [".bix-div-container"],
    "default": [
        ".entry-content",
        ".post-content",
        "article .text",
        "article",
        "main .content",
        "main",
        "#content",
        ".content",
    ],
}


class GenericScraper(BaseScraper):
    site_name = "generic"

    @classmethod
    def can_handle(cls, url):
        return True

    def scrape(self, driver, start_url, metadata=None):
        metadata = metadata or {}
        site_host = get_site_host(start_url)
        selectors = CONTENT_SELECTORS.get(site_host, CONTENT_SELECTORS["default"])

        print(f"  [{self.site_name}] Scraping article: {start_url}")
        driver.get(start_url)
        time.sleep(4)

        text = self._extract_text(driver, selectors)
        if not text:
            print(f"  [{self.site_name}] No readable content found")
            return []

        domain = metadata.get("domain") or self._domain_from_page(driver)
        default_subdomain = metadata.get("subdomain", "")
        lines = [line for line in text.splitlines()]
        questions = parse_mcqs_from_lines(
            lines,
            domain=domain,
            default_subdomain=default_subdomain,
            metadata=metadata,
        )
        questions = apply_metadata_defaults(questions, metadata)
        print(f"  [{self.site_name}] Parsed {len(questions)} questions from text")
        return questions

    def _extract_text(self, driver, selectors):
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if not elements:
                continue
            text = elements[0].text.strip()
            if len(text) > 100:
                return text
        return driver.find_element(By.TAG_NAME, "body").text

    def _domain_from_page(self, driver):
        title = (driver.title or "").split("|")[0].strip()
        title = re.sub(r"\b(MCQs?|Quiz|Practice|Objective Type)\b", "", title, flags=re.I)
        title = re.sub(r"\s+", " ", title).strip(" -")
        return title
