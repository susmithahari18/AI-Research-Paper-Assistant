from pypdf import PdfReader

def extract_text_from_pdf(pdf_file):

    reader = PdfReader(pdf_file)

    extracted_pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        if text:
            extracted_pages.append({
                "page": page_number,
                "text": text
            })

    return extracted_pages