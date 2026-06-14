import time
from urllib.parse import urldefrag, urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scrapers.base import BaseScraper
from scrapers.utils import apply_metadata_defaults, make_question_record, title_from_slug


class IndiaBixScraper(BaseScraper):
    site_name = "indiabix"

    @classmethod
    def can_handle(cls, url):
        return "indiabix.com" in url

    @staticmethod
    def normalize_url(url):
        url = url.rstrip("/")
        if "questions-and-answers" in url:
            url = url.split("/questions-and-answers")[0]
        return url + "/"

    def scrape(self, driver, start_url, metadata=None):
        metadata = metadata or {}
        all_data = []
        current_url = self.normalize_url(start_url)
        domain, subdomain = self._domain_subdomain_from_url(
            start_url, metadata.get("domain"), metadata.get("subdomain")
        )

        while current_url:
            print(f"  [{self.site_name}] Scraping: {current_url}")
            driver.get(current_url)

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "bix-div-container"))
                )
            except Exception:
                print(f"  [{self.site_name}] No questions found on {current_url}")
                break

            time.sleep(2)
            all_data.extend(
                self._parse_page(driver, domain, subdomain, metadata.get("companyTags"))
            )

            next_url = self._get_next_url(driver, current_url)
            if not next_url or next_url == current_url:
                break
            current_url = next_url

        return apply_metadata_defaults(all_data, metadata)

    def _parse_page(self, driver, domain, subdomain, company_tags=None):
        records = []
        containers = driver.find_elements(By.CLASS_NAME, "bix-div-container")
        for container in containers:
            try:
                q_elem = container.find_element(By.CLASS_NAME, "bix-td-qtxt")
                qtxt = q_elem.text
                opts = [
                    o.text
                    for o in container.find_elements(By.CLASS_NAME, "bix-td-option-val")
                ]
                ans = container.find_element(By.CLASS_NAME, "jq-hdnakq").get_attribute(
                    "value"
                )
                exp = container.find_element(By.CLASS_NAME, "bix-ans-description").text
                image_link = ""
                images = q_elem.find_elements(By.TAG_NAME, "img")
                if images:
                    image_link = images[0].get_attribute("src") or ""
                records.append(
                    make_question_record(
                        qtxt,
                        opts,
                        ans or "",
                        exp,
                        domain=domain,
                        subdomain=subdomain,
                        image_link=image_link,
                        company_tags=company_tags,
                    )
                )
            except Exception:
                continue
        return records

    @staticmethod
    def _domain_subdomain_from_url(url, override_domain="", override_subdomain=""):
        parts = [part for part in urlparse(url).path.split("/") if part]
        domain = override_domain or (title_from_slug(parts[0]) if parts else "General")
        subdomain = override_subdomain or (
            title_from_slug(parts[1]) if len(parts) > 1 else ""
        )
        if subdomain in {"Questions And Answers", "Questions-and-answers"}:
            subdomain = title_from_slug(parts[0]) if parts else ""
        return domain, subdomain

    def _get_next_url(self, driver, current_url):
        try:
            pagination = driver.find_elements(
                By.CSS_SELECTOR, "ul.pagination li.page-item a"
            )
            current_base = self._normalize_page_url(current_url)
            for link in reversed(pagination):
                href = link.get_attribute("href") or ""
                text = (link.text or "").strip().lower()
                if text != "next":
                    continue
                href, _fragment = urldefrag(href)
                if not href or href.endswith("#") or "javascript" in href:
                    continue
                if self._normalize_page_url(href) == current_base:
                    continue
                return href
        except Exception:
            pass
        return None

    @staticmethod
    def _normalize_page_url(url):
        url, _ = urldefrag(url.rstrip("/"))
        path = urlparse(url).path.rstrip("/")
        return path or "/"
