import os
import io
import docx
from pdfminer.high_level import extract_text
from security.encryption import decrypt_file


# ---------- PDF TEXT EXTRACTION (ROBUST) ----------
def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = decrypt_file(encrypted_data)

    try:
        text = extract_text(io.BytesIO(decrypted_data))
        return text if text else ""
    except Exception:
        return ""


# ---------- DOCX TEXT EXTRACTION ----------
def extract_text_from_docx(file_path):
    with open(file_path, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = decrypt_file(encrypted_data)

    try:
        doc_stream = io.BytesIO(decrypted_data)
        document = docx.Document(doc_stream)

        text = " ".join(para.text for para in document.paragraphs)
        return text
    except Exception:
        return ""


# ---------- MAIN PARSER ----------
def parse_resumes(resume_folder):
    resumes = {}

    for filename in os.listdir(resume_folder):
        file_path = os.path.join(resume_folder, filename)

        text = ""

        if filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file_path)

        elif filename.lower().endswith(".docx"):
            text = extract_text_from_docx(file_path)

        # ---------- VALIDATION ----------
        if not text or len(text.strip()) < 50:
            print(f"⚠️ Skipping {filename}: No readable text found")
            continue

        resumes[filename] = text

    return resumes
