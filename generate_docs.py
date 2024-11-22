##############################################################################################################################
# author: @mattische                                                                                                         #
# Hej! Masse här!                                                                                                            #
# detta script är en del av workflow/gihub action som genererar filer när jag pushar/uppdaterar innehållet i index.md        #
##############################################################################################################################

import os
import re
from markdown2 import markdown
from docx import Document
from fpdf import FPDF
from bs4 import BeautifulSoup
from weasyprint import HTML


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

# från md till html
def markdown_to_html(md_content):
    return markdown(md_content)

# från md till html - ink bootstrap
def generate_html(md_content):
    html_content = markdown_to_html_with_template(md_content)
    html_file = os.path.join(OUTPUT_DIR, "index.html")
    with open(html_file, "w", encoding="utf-8") as file:
        file.write(html_content)

# inkludera bootstrap cdn
def markdown_to_html_with_template(md_content):
    # Konvertera Markdown till HTML
    body_content = markdown(md_content)

    soup = BeautifulSoup(body_content, "html.parser")

    # tabeller
    for table in soup.find_all("table"):
        table["class"] = "table table-striped table-bordered"
        table["style"] = "margin-top: 1rem; width: 100%;"
    
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Generated Document</title>
        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" 
              integrity="sha384-rbsA2VBKQ9AR+I9AYhkfxQjCfSKV9VV2i59lFWEL8BnhE9r5qD65VohKp35uEF5e" 
              crossorigin="anonymous">
        <style>
            body {{
                padding: 2rem;
                font-family: Arial, sans-serif;
            }}
            h1, h2, h3 {{
                margin-top: 1.5rem;
                margin-bottom: 1rem;
            }}
            p {{
                margin-bottom: 1rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {soup}
        </div>
        <!-- Bootstrap JS -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" 
                integrity="sha384-OERcA2GHZg6UAAETMcFp2xn5p6b9BjNx16bX4R7aB9QdEWw5mCXK5kFnfNIKqM+A" 
                crossorigin="anonymous"></script>
    </body>
    </html>
    """
    
    return html_template


# från html till docx
def html_to_docx(html_content, output_path):
    doc = Document()
    soup = BeautifulSoup(html_content, "html.parser")

    for element in soup.descendants:
        if element.name == "h1":
            doc.add_heading(element.text, level=1)
        elif element.name == "h2":
            doc.add_heading(element.text, level=2)
        elif element.name == "h3":
            doc.add_heading(element.text, level=3)
        elif element.name == "strong":
            paragraph = doc.add_paragraph()  
            run = paragraph.add_run(element.text)
            run.bold = True  # Ställ in fetstil
        elif element.name == "ul":
            for li in element.find_all("li"):
                doc.add_paragraph(li.text, style="List Bullet")
        elif element.name == "ol":
            for li in element.find_all("li"):
                doc.add_paragraph(li.text, style="List Number")
        elif element.name == "table":
            rows = element.find_all("tr")
            if rows:
                table = doc.add_table(rows=len(rows), cols=len(rows[0].find_all(["td", "th"])))
                for i, row in enumerate(rows):
                    for j, cell in enumerate(row.find_all(["td", "th"])):
                        table.rows[i].cells[j].text = cell.get_text(strip=True)
        elif element.name == "p":
            doc.add_paragraph(element.text)

    doc.save(output_path)


# från html till pdf
def html_to_pdf(html_content, output_path):
    HTML(string=html_content).write_pdf(output_path)

# Ta bort tecken som inte stöds av "latin-1" (Unicode problem)
def sanitize_content(content):
    return re.sub(r'[^\x00-\xFF]', '', content)

# kopiera till README.md
def update_readme(md_content):
    write_file(README_FILE, md_content)

def main():
    # Skapa output mapp
    create_output_dir()

    md_content = read_markdown_file(INDEX_FILE)

    # md till html
    html_content = markdown_to_html_with_template(md_content)
    html_path = os.path.join(OUTPUT_DIR, OUTPUT_PREFIX + ".html")
    write_file(html_path, html_content)

    # docx, pdf från html
    docx_path = os.path.join(OUTPUT_DIR, OUTPUT_PREFIX + ".docx")
    pdf_path = os.path.join(OUTPUT_DIR, OUTPUT_PREFIX + ".pdf")
    html_to_docx(html_content, docx_path)
    html_to_pdf(html_content, pdf_path)
    

    # Uppdatera README.md
    update_readme(md_content)

if __name__ == "__main__":
    main()
