from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from app.utils import clean_text, calculate_similarity, get_missing_keywords
import pdfplumber
import io

app = FastAPI()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def generate_suggestion(score: float, missing_keywords: list[str]) -> str:
    if score >= 80:
        return "Strong match. Your resume aligns well with the job description."
    if score >= 60:
        return "Good match. Adding a few missing keywords could improve ATS alignment."
    if missing_keywords:
        top_missing = ", ".join(missing_keywords[:3])
        return f"Moderate match. Consider adding relevant terms such as {top_missing}."
    return "Low match. Tailor your resume more closely to the job description."

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    resume_content = await file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(resume_content)
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")
    elif filename.endswith(".txt"):
        try:
            resume_text = resume_content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                resume_text = resume_content.decode("latin-1")
            except Exception:
                raise HTTPException(status_code=400, detail="Could not read the text file.")
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a .txt or .pdf file."
        )

    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_description)

    score = calculate_similarity(resume_clean, job_clean)
    missing_keywords = get_missing_keywords(resume_clean, job_clean)

    return {
        "match_score": score,
        "matched": score >= 60,
        "missing_keywords": missing_keywords,
        "suggestion": generate_suggestion(score, missing_keywords)
    }