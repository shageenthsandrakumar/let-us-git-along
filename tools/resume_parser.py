import io
import logging
from pypdf import PdfReader

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract plain text from a PDF file (e.g. LinkedIn profile export)."""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
        full_text = "\n\n".join(pages)
        # Trim to ~8000 chars — enough signal, keeps token cost low
        return full_text[:8000].strip()
    except Exception as e:
        logger.error("PDF parsing failed: %s", e)
        return ""
