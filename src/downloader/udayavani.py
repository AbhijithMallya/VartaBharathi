from typing import Any

from playwright.sync_api import sync_playwright
from src.core.base import NewspaperDownloader  # adjust import if needed


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

    def __exit__(self, exc_type, exc_value, traceback):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

            
    def download(self, date: str) -> None:
        """
        Downloads Udayavani Newspaper for given Date
        """
        try:
            self.page.goto(
                "https://www.tradingref.com/udayavani",
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
            print("🔤 Selecting Language: Kannada...")
            self.page.wait_for_function(
                "() => !document.getElementById('languageSelect').disabled",
                timeout=30000
            )
            self.page.select_option("#languageSelect", value="kannada")

            # 3. Select Newspaper
            print("📰 Selecting Newspaper: Udayavani...")
            self.page.wait_for_function(
                "() => !document.getElementById('newspaperSelect').disabled",
                timeout=30000
            )
            self.page.select_option("#newspaperSelect", label="Udayavani")

            # 4. Select Edition
            print("📍 Selecting Edition: Manipal Edition...")
            self.page.wait_for_function(
                "() => !document.getElementById('editionSelect').disabled",
                timeout=30000
            )
            self.page.select_option("#editionSelect", label="Manipal Edition")

            # 5. Generate & Download
            print("⏳ Generating PDF... (This may take up to 60 seconds)")

            with self.page.expect_download(timeout=120000) as download_info:
                self.page.click('button:has-text("Generate & Download PDF")')

            download = download_info.value

            # 6. Save file
            filename = f"Udayavani_Manipal_{date.replace('-', '')}.pdf"
            download.save_as(filename)

            print(f"✅ Success! PDF saved as: {filename}")
            print(f"🔗 Source URL: {download.url}")

        except Exception as e:
            print(f"❌ Error occurred: {e}")