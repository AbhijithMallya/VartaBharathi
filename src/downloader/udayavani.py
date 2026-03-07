from typing import Any, Optional, Type
from types import TracebackType
import os

from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page
from src.core.base import NewspaperDownloader
from src.config.newspaper import newspaper_settings


class Udayavani(NewspaperDownloader):

    def __init__(self, headless: bool = True):
        super().__init__()
        config = newspaper_settings.udayavani
        self.language: str = config.LANGUAGE
        self.edition: str = config.EDITION
        self.newspaper: str = config.NEWSPAPER_NAME
        self.headless: bool = headless

        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def __enter__(self) -> "Udayavani":
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(accept_downloads=True)
        self.page = self.context.new_page()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def download(self, date: str) -> None:
        """
        Downloads Udayavani Newspaper for given Date
        """
        if not self.page:
            raise RuntimeError("Browser not initialized. Use as a context manager.")

        try:
            self.page.goto(
                newspaper_settings.udayavani.BASE_URL,
                wait_until="networkidle",
                timeout=60000,
            )

            # 1. Select Date
            print(f"📅 Selecting Date...{date}")
            self.page.wait_for_selector('input[placeholder="Select date"]')

            self.page.evaluate(f"""
                const input = document.querySelector('input[placeholder="Select date"]');
                if (input._flatpickr) {{
                    input._flatpickr.setDate('{date}', true);
                }} else {{
                    input.value = '{date}';
                    input.dispatchEvent(new Event('change'));
                }}
            """)

            # 2. Select Language
            print(f"🔤 Selecting Language: {self.language}...")
            self.page.wait_for_function(
                "() => !document.getElementById('languageSelect').disabled",
                timeout=30000
            )
            self.page.select_option("#languageSelect", value=self.language)

            # 3. Select Newspaper
            print(f"📰 Selecting Newspaper: {self.newspaper}...")
            self.page.wait_for_function(
                "() => !document.getElementById('newspaperSelect').disabled",
                timeout=30000
            )
            self.page.select_option("#newspaperSelect", label=self.newspaper)

            # 4. Select Edition
            print(f"📍 Selecting Edition: {self.edition}...")
            self.page.wait_for_function(
                "() => !document.getElementById('editionSelect').disabled",
                timeout=30000
            )
            self.page.select_option("#editionSelect", label=self.edition)

            # 5. Generate & Download
            print("⏳ Generating PDF... (This may take up to 60 seconds)")

            with self.page.expect_download(timeout=120000) as download_info:
                self.page.click('button:has-text("Generate & Download PDF")')

            download = download_info.value

            # 6. Save file
            news_dir = newspaper_settings.NEWS_DIR
            os.makedirs(news_dir, exist_ok=True)
            filename = f"{news_dir}/{self.newspaper}_{self.edition.split()[0]}_{date.replace('-', '')}.pdf"
            download.save_as(filename)

            print(f"✅ Success! PDF saved as: {filename}")
            print(f"🔗 Source URL: {download.url}")

        except Exception as e:
            print(f"❌ Error occurred: {e}")