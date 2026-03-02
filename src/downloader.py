import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import os

async def download_udayavani_pdf(target_date="2026-03-02"):
    async with async_playwright() as p:
        # Launch the browser (headless=True for background running)
        browser = await p.chromium.launch(headless=True) 
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        print(f"🚀 Navigating to TradingRef for {target_date}...")
        try:
            await page.goto("https://www.tradingref.com/udayavani", wait_until="networkidle", timeout=60000)

            # 1. Select the Date via the Flatpickr input
            print("📅 Selecting Date...")
            await page.wait_for_selector('input[placeholder="Select date"]')
            
            # We use evaluate to inject the date directly into the Flatpickr instance
            await page.evaluate(f"""
                const input = document.querySelector('input[placeholder="Select date"]');
                if (input._flatpickr) {{
                    input._flatpickr.setDate('{target_date}', true);
                }} else {{
                    input.value = '{target_date}';
                    input.dispatchEvent(new Event('change'));
                }}
            """)

            # 2. Select Language (Wait for the JS to enable the dropdown)
            print("🔤 Selecting Language: Kannada...")
            await page.wait_for_function("() => !document.getElementById('languageSelect').disabled", timeout=30000)
            await page.select_option("#languageSelect", value="kannada")

            # 3. Select Newspaper
            print("📰 Selecting Newspaper: Udayavani...")
            await page.wait_for_function("() => !document.getElementById('newspaperSelect').disabled", timeout=30000)
            await page.select_option("#newspaperSelect", label="Udayavani")

            # 4. Select Edition (Strict Match for 'Manipal Edition')
            print("📍 Selecting Edition: Manipal Edition...")
            await page.wait_for_function("() => !document.getElementById('editionSelect').disabled", timeout=30000)
            await page.select_option("#editionSelect", label="Manipal Edition")

            # 5. Trigger PDF Generation and Capture the Download
            print("⏳ Generating PDF... (This may take up to 60 seconds)")
            
            # Prepare to catch the download event
            async with page.expect_download(timeout=120000) as download_info:
                await page.click('button:has-text("Generate & Download PDF")')
            
            download = await download_info.value
            
            # 6. Save the file
            filename = f"Udayavani_Manipal_{target_date.replace('-', '')}.pdf"
            await download.save_as(filename)
            
            print(f"✅ Success! PDF saved as: {filename}")
            print(f"🔗 Source URL: {download.url}")

        except Exception as e:
            print(f"❌ Error occurred: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    # You can change the date here or use datetime.now().strftime("%Y-%m-%d")
    target = "2026-01-01"
    asyncio.run(download_udayavani_pdf(target))
