import json
import time
import os
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from pypdf import PdfReader, PdfWriter

# --- CONFIGURATION ---
GEMINI_API_KEY = "<#api_key_here#>"
PDF_PATH = "Udayavani_Manipal_20260101.pdf"
TEMP_DIR = "split_pages_{}".format(int(time.time()))  # Unique temp dir for each run
GEMINI_MODEL="gemini-2.5-flash-lite"
client = genai.Client(api_key=GEMINI_API_KEY)

# --- SCHEMAS (Refined) ---
class NewsStory(BaseModel):
    headline: str
    location: Optional[str]
    category: str
    key_points: List[str]
    event_details: Optional[str]

class Advertisement(BaseModel):
    brand: str
    offer_details: str

class PageAnalysis(BaseModel):
    page_number: int
    main_theme: str
    news_articles: List[NewsStory]
    offers_and_discounts: List[Advertisement]
    temple_and_cultural_events: List[str]

# --- PDF SPLITTING UTILITY ---
def split_pdf(path):
    if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
    reader = PdfReader(path)
    paths = []
    for i in range(len(reader.pages)):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])
        p = os.path.join(TEMP_DIR, f"p{i+1}.pdf")
        with open(p, "wb") as f: writer.write(f)
        paths.append(p)
    return paths

# --- HTML TEMPLATE BUILDER ---
def build_html_email(user_name, data):
    """Wraps the news data in a professional, responsive HTML container."""
    
    # 1. Custom AI Greeting (Witty/Warm)
    prompt = f"Write a 2-sentence warm greeting for {user_name} for their morning newspaper briefing. Tone: Cheerful & Sophisticated."
    header_text = client.models.generate_content(model=GEMINI_MODEL, contents=[prompt]).text

    # Start HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; color: #333; }}
            .container {{ max-width: 600px; margin: auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
            .header {{ background: #1a3a3a; color: white; padding: 40px 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; letter-spacing: 1px; }}
            .greeting {{ padding: 20px; font-style: italic; color: #555; border-bottom: 1px solid #eee; text-align: center; }}
            .section {{ padding: 25px; border-bottom: 8px solid #f4f7f6; }}
            .page-label {{ font-size: 12px; font-weight: bold; color: #1a3a3a; text-transform: uppercase; background: #e0eceb; padding: 4px 10px; border-radius: 20px; display: inline-block; margin-bottom: 15px; }}
            .news-card {{ margin-bottom: 20px; }}
            .news-headline {{ font-size: 18px; font-weight: 700; color: #111; margin-bottom: 5px; }}
            .news-loc {{ font-size: 13px; color: #00796b; font-weight: bold; margin-bottom: 8px; }}
            .bullet {{ margin-left: 0; padding-left: 0; list-style: none; }}
            .bullet li {{ margin-bottom: 5px; position: relative; padding-left: 20px; font-size: 14px; line-height: 1.5; }}
            .bullet li::before {{ content: "•"; color: #00796b; position: absolute; left: 0; font-weight: bold; }}
            .event-box {{ background: #fffbe6; border-left: 4px solid #ffc107; padding: 10px 15px; margin-top: 10px; font-size: 13px; border-radius: 4px; }}
            .offer-tag {{ background: #fff0f0; color: #d32f2f; border: 1px solid #f8bbd0; padding: 10px; border-radius: 8px; display: block; margin-top: 10px; font-size: 13px; }}
            .footer {{ text-align: center; padding: 30px; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>UDAYAVANI DAILY</h1>
                <p style="margin-top:10px; opacity: 0.8;">Custom Briefing for {user_name}</p>
            </div>
            <div class="greeting">
                "{header_text.strip()}"
            </div>
    """

    for page in data:
        # Filter for quality
        if not page['news_articles'] and not page['temple_and_cultural_events']:
            continue

        html += f"""
        <div class="section">
            <span class="page-label">Page {page['page_number']} | {page['main_theme']}</span>
        """

        # News Articles
        for news in page['news_articles']:
            html += f"""
            <div class="news-card">
                <div class="news-headline">{news['headline']}</div>
                <div class="news-loc">📍 {news['location'] or 'General'} • {news['category']}</div>
                <ul class="bullet">
            """
            for pt in news['key_points']:
                html += f"<li>{pt}</li>"
            html += "</ul>"
            
            if news['event_details']:
                html += f'<div class="event-box"><strong>Event Detail:</strong> {news["event_details"]}</div>'
            html += "</div>"

        # Temple & Culture
        if page['temple_and_cultural_events']:
            html += '<div style="margin-top:20px; font-weight:bold; color:#1a3a3a;">🛕 Temple & Cultural Highlights</div>'
            html += '<ul class="bullet" style="margin-top:10px;">'
            for event in page['temple_and_cultural_events']:
                html += f"<li>{event}</li>"
            html += "</ul>"

        # Offers
        if page['offers_and_discounts']:
            for ad in page['offers_and_discounts']:
                html += f"""
                <div class="offer-tag">
                    <strong>🛍️ OFFER: {ad['brand']}</strong><br>{ad['offer_details']}
                </div>
                """
        
        html += "</div>"

    html += """
            <div class="footer">
                You are receiving this because your AI assistant processed today's Udayavani. <br>
                © 2026 Gemini News Assistant
            </div>
        </div>
    </body>
    </html>
    """
    return html

# --- MAIN RUNNER ---
def run_analysis(name):
    print(f"Splitting PDF for {name}...")
    page_files = split_pdf(PDF_PATH)
    full_report = []

    for i, page_path in enumerate(page_files):
        print(f"Analyzing Page {i+1}...")
        uploaded = client.files.upload(file=page_path)
        
        prompt = "Extract local updates, temple/lunch events, cultural news, and retail offers. Use provided schema."
        
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[uploaded, prompt],
                config={"response_mime_type": "application/json", "response_schema": PageAnalysis},
            )
            full_report.append(response.parsed.model_dump())
            client.files.delete(name=uploaded.name)
        except Exception as e:
            print(f"Error on page {i+1}: {e}")

    # Final HTML Save
    final_html = build_html_email(name, full_report)
    with open(f"briefing_{name}.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    
    print(f"Beautiful HTML report generated: briefing_{name}.html")

if __name__ == "__main__":
    run_analysis("Abhishek")
