import json
import os

from scrapers.registry import scrape_url
from scrapers.utils import create_driver, get_filename_from_url, parse_url_entry


def scrape_all_pages(start_url, driver=None, metadata=None):
    own_driver = driver is None
    if own_driver:
        driver = create_driver()

    try:
        return scrape_url(driver, start_url, metadata=metadata)
    finally:
        if own_driver:
            driver.quit()


if __name__ == "__main__":
    if not os.path.exists("urls.txt"):
        print("Error: urls.txt not found.")
        raise SystemExit(1)

    with open("urls.txt", "r", encoding="utf-8") as f:
        entries = [parse_url_entry(line) for line in f]
    entries = [entry for entry in entries if entry]

    driver = create_driver()
    try:
        for entry in entries:
            url = entry["url"]
            filename = get_filename_from_url(url)
            print(f"--- Starting: {url} ---")
            try:
                data = scrape_url(driver, url, metadata=entry)
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                print(f"Saved {len(data)} questions to {filename}")
            except Exception as exc:
                print(f"Failed to scrape {url}: {exc}")
    finally:
        driver.quit()
