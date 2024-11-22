import os
from markdown2 import markdown
from docx import Document
from fpdf import FPDF
from bs4 import BeautifulSoup

# Filnamn
INDEX_FILE = "index.md"
README_FILE = "README.md"
OUTPUT_DIR = "files"
OUTPUT_PREFIX = "MattiasSchertell"

def create_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def read_markdown_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)

def generate_html(md_content):
    html_content = markdown(md_content)
    html_file = os.path.join(OUTPUT_DIR, OUTPUT_PREFIX.".html")
    write_file(html_file, html_content)

def generate_docx(md_content):
    doc = Document()
    lines = md_content.splitlines()
    for line in lines:
        if line.startswith("# "):  # Header 1
            doc.add_heading(line[2:], level=1)
        elif line.startswith("## "):  # Header 2
            doc.add_heading(line[3:], level=2)
        elif line.startswith("### "):  # Header 3
            doc.add_heading(line[4:], level=3)
        else:
            doc.add_paragraph(line)
    docx_file = os.path.join(OUTPUT_DIR, OUTPUT_PREFIX.".docx")
    doc.save(docx_file)

def sanitize_content(content):
    # Ta bort tecken som inte stöds av "latin-1"
    return re.sub(r'[^\x00-\xFF]', '', content)
    
def generate_pdf(md_content):
    sanitized_content = sanitize_content(md_content)
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    soup = BeautifulSoup(markdown(md_content), "html.parser")
    for element in soup.descendants:
        if element.name == "h1":
            pdf.set_font("Arial", style="B", size=16)
            pdf.cell(200, 10, txt=element.text, ln=True, align="C")
        elif element.name == "h2":
            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(200, 10, txt=element.text, ln=True, align="L")
        elif element.name == "h3":
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(200, 10, txt=element.text, ln=True, align="L")
        elif element.name == "p":
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, txt=element.text)
    pdf_file = os.path.join(OUTPUT_DIR, OUTPUT_PREFIX.".pdf")
    pdf.output(pdf_file)

def update_readme(md_content):
    write_file(README_FILE, md_content)

def main():
    # Skapa output-mappen om den inte finns
    create_output_dir()

    # Läs innehåll från index.md
    md_content = read_markdown_file(INDEX_FILE)

    # Generera dokument
    generate_html(md_content)
    generate_docx(md_content)
    generate_pdf(md_content)

    # Uppdatera README.md
    update_readme(md_content)

if __name__ == "__main__":
    main()
