from playwright.sync_api import sync_playwright
from core.base import NewspaperDownloader  # adjust import if needed


class Udayavani(NewspaperDownloader):

    def __init__(self, headless: bool = True):
        super().__init__()
        self.language: str = "kannada"
        self.edition: str = "Manipal Edition"
        self.newspaper: str = "Udayavani"
        self.headless = headless

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(accept_downloads=True)
        self.page = self.context.new_page()
        return self

    def __exit__(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

            
    # def download_newspaper(self, date: str) -> None:
    #     """
    #     Downloads Udayavani Newspaper for given Date
    #     """
        






