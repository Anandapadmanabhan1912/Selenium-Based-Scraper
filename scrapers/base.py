from abc import ABC, abstractmethod


class BaseScraper(ABC):
    site_name = "unknown"

    @classmethod
    @abstractmethod
    def can_handle(cls, url):
        pass

    @abstractmethod
    def scrape(self, driver, start_url):
        pass

