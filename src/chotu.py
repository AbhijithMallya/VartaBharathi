import json
import os
import base64
from io import BytesIO
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from pdf2image import convert_from_path

# --- CONFIGURATION ---
PDF_PATH = "Udayavani_Manipal_20260101.pdf"
GEMINI_MODEL = "qwen3-vl:8b" # Kept variable name same to avoid breaking references
client = OpenAI(
    base_url="http://10.11.51.231:11434/v1",
    api_key="ollama" 
)

# --- SCHEMAS (Strictly Original) ---
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

# --- SYSTEM INSTRUCTION FOR LLM ---
system_instruction = """
You are an expert at analyzing newspaper content. Your task is to extract information from the provided newspaper page image and format it as a JSON object strictly according to the following Pydantic schemas.

The JSON output should adhere to the `PageAnalysis` schema. Ensure all fields are present. If a list field has no content, return an empty list. If a string field has no content, return an empty string. If an integer field has no content, return 0.

```python
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
```
"""

# --- PDF TO IMAGE UTILITY ---
# Replaces split_pdf because local vision models need image buffers/bytes
def get_pdf_pages_as_base64(path):
    images = convert_from_path(path, dpi=200)
    base64_pages = []
    for img in images:
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        base64_pages.append(base64.b64encode(buffered.getvalue()).decode('utf-8'))
    return base64_pages

# --- HTML TEMPLATE BUILDER (Strictly Original) ---
def build_html_email(user_name, data):
    # 1. Custom AI Greeting
    prompt = f"Write a 2-sentence warm greeting for {user_name} for their morning newspaper briefing. Tone: Cheerful & Sophisticated."
    header_res = client.chat.completions.create(
        model=GEMINI_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    header_text = header_res.choices[0].message.content

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
        if not page['news_articles'] and not page['temple_and_cultural_events']:
            continue

        html += f"""
        <div class="section">
            <span class="page-label">Page {page['page_number']} | {page['main_theme']}</span>
        """

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
            
            if news.get('event_details'):
                html += f'<div class="event-box"><strong>Event Detail:</strong> {news["event_details"]}</div>'
            html += "</div>"

        if page['temple_and_cultural_events']:
            html += '<div style="margin-top:20px; font-weight:bold; color:#1a3a3a;">🛕 Temple & Cultural Highlights</div>'
            html += '<ul class="bullet" style="margin-top:10px;">'
            for event in page['temple_and_cultural_events']:
                html += f"<li>{event}</li>"
            html += "</ul>"

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
    print(f"Processing PDF for {name}...")
    # Get images instead of splitting files
    encoded_images = get_pdf_pages_as_base64(PDF_PATH)
    full_report = []

    for i, base64_image in enumerate(encoded_images):
        print(f"Analyzing Page {i+1}...")
        
        
        try:
            # Using OpenAI Chat Completions for Vision
            response = client.chat.completions.create(
                model=GEMINI_MODEL,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract local updates, temple/lunch events, cultural news, and retail offers from the image. Your output MUST be a JSON object conforming to the `PageAnalysis` schema."},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            },
                        ],
                    }
                ],
                # Emulating Gemini's response_schema via OpenAI's JSON mode
                response_format={"type": "json_object"}
            )
            
            # Parse response into the Pydantic model to match original logic
            page_data = PageAnalysis.model_validate_json(response.choices[0].message.content)
            full_report.append(page_data.model_dump())
            
        except Exception as e:
            print(f"Error on page {i+1}: {e}")
            if 'response' in locals() and response.choices and response.choices[0].message.content:
                print(f"Raw LLM response content: {response.choices[0].message.content}")

    # Final HTML Save (Original Logic)
    final_html = build_html_email(name, full_report)
    with open(f"briefing_{name}.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    
    print(f"Beautiful HTML report generated: briefing_{name}.html")

if __name__ == "__main__":
    run_analysis("Abhishek")