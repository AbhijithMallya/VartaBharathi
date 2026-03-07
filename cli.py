import argparse
import os
from datetime import datetime
from src.downloader.udayavani import Udayavani
from src.sender.gmail import Gmail
from src.config import settings, newspaper_settings

def main() -> None:
    parser = argparse.ArgumentParser(description="Download newspaper and send via Gmail.")
    parser.add_argument(
        "--date", 
        type=str, 
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Date to download (YYYY-MM-DD). Defaults to today."
    )
    parser.add_argument(
        "--env", 
        type=str, 
        default=".env",
        help="Path to the .env file. Defaults to '.env'."
    )
    
    args = parser.parse_args()

    target_date = args.date
    news_dir = newspaper_settings.NEWS_DIR
    newspaper_name = newspaper_settings.udayavani.NEWSPAPER_NAME
    edition_short = newspaper_settings.udayavani.EDITION.split()[0]
    
    # Construct filename dynamically from config
    filename = f"{news_dir}/{newspaper_name}_{edition_short}_{target_date.replace('-', '')}.pdf"
    receiver_emails = settings.gmail.RECEIVERS

    # 1. Download Newspaper
    print(f"📥 Starting download for {target_date}...")
    try:
        with Udayavani(headless=True) as downloader:
            downloader.download(target_date)
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return

    # 2. Send via Email
    if not os.path.exists(filename):
        print(f"⚠️  PDF file not found: {filename}. Skipping email.")
        return

    sender = Gmail()
    email_content = f"Here's the {newspaper_name} {edition_short} edition PDF for {target_date}!"
    
    for email in receiver_emails:
        print(f"📧 Sending email to {email}...")
        sender.send(
            receiver=email,
            content=email_content,
            attachments=[filename]
        )

if __name__ == "__main__":
    main()
