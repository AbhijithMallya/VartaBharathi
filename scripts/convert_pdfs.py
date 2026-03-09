import fitz  # PyMuPDF
import os
from pathlib import Path

def convert_pdfs(news_dir="news"):
    news_path = Path(news_dir)
    pdf_files = sorted(list(news_path.glob("*.pdf")))
    
    if not pdf_files:
        print("No PDF files found in news/ directory.")
        return

    for pdf_file in pdf_files:
        print(f"Processing {pdf_file.name}...")
        try:
            doc = fitz.open(pdf_file)
            for i, page in enumerate(doc):
                # 300 DPI for high quality (lossless-like clarity)
                # Default PDF resolution is 72 DPI, so 300/72 is the scale factor
                zoom = 300 / 72
                mat = fitz.Matrix(zoom, zoom)
                
                # Get pixmap with the specified matrix (high DPI)
                # alpha=False ensures no transparency (saves as standard RGB)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # output name: {pdf_name}_page_{num}.png
                output_filename = f"{pdf_file.stem}_page_{i+1}.png"
                output_path = news_path / output_filename
                
                pix.save(str(output_path))
                print(f"  Saved {output_filename}")
            doc.close()
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")

if __name__ == "__main__":
    convert_pdfs()
