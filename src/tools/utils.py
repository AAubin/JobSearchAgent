import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)

import pdfplumber
from pathlib import Path

def load_resume(chemin: str = "cv.pdf") -> str:
    p = Path(chemin)
    if not p.exists():
        return "CV non trouvé."
    if p.suffix.lower() == ".pdf":
        with pdfplumber.open(p) as pdf:
            return "\n".join(
                page.extract_text() or "" for page in pdf.pages
            ).strip()
    return p.read_text(encoding="utf-8")
