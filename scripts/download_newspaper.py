import datetime

import os

import sys

from unittest.mock import MagicMock

from playwright.sync_api import sync_playwright
 
# Ensure the root directory is in the python path for imports

sys.path.append(os.getcwd())
 
# Mock the settings before they are imported by anything else

# This bypasses Pydantic's environment variable validation for OpenAI and Gmail

# which are not needed for just downloading newspapers.

mock_settings = MagicMock()

sys.modules['src.config.settings'] = mock_settings

mock_settings.settings = MagicMock()
 
from src.downloader.udayavani import Udayavani

from src.config.newspaper import newspaper_settings
 
class CustomUdayavani(Udayavani):

    """

    Subclass of Udayavani that ignores HTTPS errors for the specific website.

    """

    def __enter__(self) -> "CustomUdayavani":

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(headless=self.headless)

        # Added ignore_https_errors=True here to bypass the certificate issue

        self.context = self.browser.new_context(

            accept_downloads=True,

            ignore_https_errors=True

        )

        self.page = self.context.new_page()

        return self
 
def download_range(start_date: datetime.date, end_date: datetime.date):

    """

    Downloads newspapers for each day in the given range (inclusive).

    """

    # Ensure news directory exists

    news_dir = newspaper_settings.NEWS_DIR

    os.makedirs(news_dir, exist_ok=True)
 
    print(f"🚀 Starting download range: {start_date} to {end_date}")

    print(f"📂 PDFs will be saved to: {os.path.abspath(news_dir)}")
 
    # Using CustomUdayavani in a context manager

    with CustomUdayavani(headless=True) as downloader:

        current_date = start_date

        while current_date <= end_date:

            date_str = current_date.strftime("%Y-%m-%d")

            print(f"\n--- Processing Date: {date_str} ---")
 
            try:

                # The download method handles its own error printing

                downloader.download(date_str)

            except Exception as e:

                print(f"❌ Unexpected error for {date_str}: {e}")
 
            current_date += datetime.timedelta(days=1)
 
    print("\n✅ Bulk download process completed.")
 
if __name__ == "__main__":

    # Define the requested date range

    start = datetime.date(2025, 5, 1)

    end = datetime.date(2025, 8, 31)
 
    download_range(start, end)
 
