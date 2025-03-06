import fitz  # PyMuPDF
import sys

input_pdf = sys.argv[1]

doc = fitz.open(input_pdf)
unique_links = set()

for page in doc:
    for link in page.links():
        if "uri" in link:
            url = link["uri"]
            if "javascript" not in url and "google" not in url:
                unique_links.add(url)

for url in unique_links:
    print(url)
