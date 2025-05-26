import fitz


def extract_text(pdf_contents: bytes) -> str:
    doc = fitz.open(stream=pdf_contents, filetype="pdf")

    text = ""
    for page in doc:
        text += page.get_text()

    return text
