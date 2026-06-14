import json
import re
import time
from urllib.request import Request, urlopen

from selenium.webdriver.common.by import By

from scrapers.base import BaseScraper
from scrapers.utils import apply_metadata_defaults, make_question_record, strip_html, title_from_slug


class GeeksforGeeksScraper(BaseScraper):
    site_name = "geeksforgeeks"

    @classmethod
    def can_handle(cls, url):
        return "geeksforgeeks.org" in url

    def scrape(self, driver, start_url, metadata=None):
        metadata = metadata or {}
        if "/quizzes/" in start_url:
            return self._scrape_quiz(driver, start_url, metadata)
        return []

    def _scrape_quiz(self, driver, start_url, metadata):
        all_data = []
        print(f"  [{self.site_name}] Scraping quiz: {start_url}")
        driver.get(start_url)
        time.sleep(4)

        quiz_data = self._load_quiz_data(driver)
        if not quiz_data:
            print(f"  [{self.site_name}] Could not load quiz data from page")
            return all_data

        domain, subdomain, topic = self._domain_subdomain_topic(
            start_url, quiz_data, metadata
        )
        all_data.extend(
            self._parse_quiz_payload(
                quiz_data,
                domain,
                subdomain,
                topic,
                metadata.get("companyTags"),
            )
        )

        next_url = quiz_data.get("next")
        while next_url:
            print(f"  [{self.site_name}] Fetching page: {next_url}")
            quiz_data = self._fetch_quiz_api(next_url)
            if not quiz_data:
                break
            all_data.extend(
                self._parse_quiz_payload(
                    quiz_data,
                    domain,
                    subdomain,
                    topic,
                    metadata.get("companyTags"),
                )
            )
            next_url = quiz_data.get("next")

        return apply_metadata_defaults(all_data, metadata)

    def _load_quiz_data(self, driver):
        try:
            script = driver.find_element(By.ID, "__NEXT_DATA__")
            page_props = json.loads(script.get_attribute("innerHTML"))["props"]["pageProps"]
            return page_props.get("quizData")
        except Exception:
            return None

    def _fetch_quiz_api(self, url):
        try:
            request = Request(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/122.0.0.0 Safari/537.36"
                    )
                },
            )
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            print(f"  [{self.site_name}] API fetch failed: {exc}")
            return None

    def _parse_quiz_payload(self, quiz_data, domain, subdomain, topic, company_tags=None):
        records = []
        results = quiz_data.get("results") or []
        for item in results:
            answers = sorted(item.get("answers") or [], key=lambda a: a.get("sort_order", 0))
            options = [strip_html(a.get("answer", "")) for a in answers]
            correct = ""
            for index, answer in enumerate(answers):
                if answer.get("correct"):
                    correct = ["A", "B", "C", "D"][index] if index < 4 else ""
                    break
            records.append(
                make_question_record(
                    strip_html(item.get("question", "")),
                    options,
                    correct,
                    strip_html(item.get("explanation", "")),
                    domain=domain,
                    subdomain=subdomain,
                    topic=topic,
                    image_link=self._extract_image_link(item.get("question", "")),
                    company_tags=company_tags,
                )
            )
        return records

    @staticmethod
    def _domain_subdomain_topic(start_url, quiz_data, metadata):
        quiz = quiz_data.get("quiz") or {}
        quiz_title = str(quiz.get("title") or quiz.get("name") or "").strip()
        slug = start_url.rstrip("/").split("/")[-1]
        slug_title = title_from_slug(slug)

        domain = metadata.get("domain") or ""
        subdomain = metadata.get("subdomain") or ""
        topic = ""

        if not domain:
            if " MCQ" in quiz_title:
                domain = quiz_title.replace(" MCQ", "").strip()
            else:
                domain = slug_title.replace(" Mcq", "").strip()

        if not subdomain and quiz_title:
            subdomain = quiz_title

        if quiz_title and quiz_title != subdomain:
            topic = quiz_title

        return domain, subdomain, topic

    @staticmethod
    def _extract_image_link(question_html):
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', question_html or "", re.I)
        return match.group(1) if match else ""
