# Delete this file later

from playwright.sync_api import sync_playwright
from datetime import datetime


def download_udayavani_pdf(target_date="2026-03-02"):
    with sync_playwright() as p:
        # Launch browser (headless=True for background running)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        print(f"🚀 Navigating to TradingRef for {target_date}...")

        try:
            page.goto(
                "https://www.tradingref.com/udayavani",
                wait_until="networkidle",
                timeout=60000,
            )

            # 1. Select Date
            print("📅 Selecting Date...")
            page.wait_for_selector('input[placeholder="Select date"]')

            page.evaluate(f"""
                const input = document.querySelector('input[placeholder="Select date"]');
                if (input._flatpickr) {{
                    input._flatpickr.setDate('{target_date}', true);
                }} else {{
                    input.value = '{target_date}';
                    input.dispatchEvent(new Event('change'));
                }}
            """)

            # 2. Select Language
            print("🔤 Selecting Language: Kannada...")
            page.wait_for_function(
                "() => !document.getElementById('languageSelect').disabled",
                timeout=30000
            )
            page.select_option("#languageSelect", value="kannada")

            # 3. Select Newspaper
            print("📰 Selecting Newspaper: Udayavani...")
            page.wait_for_function(
                "() => !document.getElementById('newspaperSelect').disabled",
                timeout=30000
            )
            page.select_option("#newspaperSelect", label="Udayavani")

            # 4. Select Edition
            print("📍 Selecting Edition: Manipal Edition...")
            page.wait_for_function(
                "() => !document.getElementById('editionSelect').disabled",
                timeout=30000
            )
            page.select_option("#editionSelect", label="Manipal Edition")

            # 5. Generate & Download
            print("⏳ Generating PDF... (This may take up to 60 seconds)")

            with page.expect_download(timeout=120000) as download_info:
                page.click('button:has-text("Generate & Download PDF")')

            download = download_info.value

            # 6. Save file
            filename = f"Udayavani_Manipal_{target_date.replace('-', '')}.pdf"
            download.save_as(filename)

            print(f"✅ Success! PDF saved as: {filename}")
            print(f"🔗 Source URL: {download.url}")

        except Exception as e:
            print(f"❌ Error occurred: {e}")

        finally:
            browser.close()


if __name__ == "__main__":
    target = "2026-01-01"
    download_udayavani_pdf(target)