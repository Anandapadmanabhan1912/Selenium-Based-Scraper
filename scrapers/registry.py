from scrapers.geeksforgeeks import GeeksforGeeksScraper
from scrapers.generic import GenericScraper
from scrapers.indiabix import IndiaBixScraper

SCRAPERS = [
    IndiaBixScraper,
    GeeksforGeeksScraper,
    GenericScraper,
]


def get_scrapers_for_url(url):
    matched = [scraper for scraper in SCRAPERS if scraper.can_handle(url)]
    if not matched:
        return [GenericScraper]
    return matched


def scrape_url(driver, url, metadata=None):
    metadata = metadata or {}
    all_data = []
    scrapers = get_scrapers_for_url(url)

    for scraper_cls in scrapers:
        if scraper_cls is GenericScraper and len(scrapers) > 1:
            continue
        scraper = scraper_cls()
        data = scraper.scrape(driver, url, metadata=metadata)
        if data:
            all_data = data
            print(f"  Used scraper: {scraper.site_name} ({len(data)} questions)")
            break

    if not all_data and GenericScraper not in scrapers:
        scraper = GenericScraper()
        all_data = scraper.scrape(driver, url, metadata=metadata)
        if all_data:
            print(f"  Used scraper: generic ({len(all_data)} questions)")

    return all_data
