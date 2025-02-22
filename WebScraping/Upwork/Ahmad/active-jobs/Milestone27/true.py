import pdfplumber
import fitz #pyMuPDF
import tabula
import re


#pdf_path = "resources/TRUE SPEC SHEET.pdf"
pdf_path = "resources/Hatco Spec Sheet.pdf"

doc = fitz.open(pdf_path)
full_text = ""

for page_num in range(len(doc)):
    page = doc.load_page(page_num)
    full_text = page.
# with pdfplumber.open('resources\TRUE SPEC SHEET.pdf') as hatco:
#     text = ""
#     for page in hatco.pages:
#         text += page.extract_text()

#         print(text)

dfs = tabula.read_pdf(pdf_path, pages='2')
print(dfs)