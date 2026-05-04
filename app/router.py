import os
from rag_pipeline import build_knowledge_base, ask as ask_pdf
from csv_pipeline import load_csv, ask_csv

SUPPORTED_EXTENSIONS = {"pdf": "rag", "csv": "csv"}

# simple cache (prevents reloading every time)
CACHE = {"pdf": None, "csv": None, "current_file": None}


# ── DETECT FILE TYPE ─────────────────────
def detect_file_type(file_path):
    ext = file_path.rsplit(".", 1)[-1].lower()
    return SUPPORTED_EXTENSIONS.get(ext, None)


# ── MAIN ROUTER ──────────────────────────
def route(file_path, question, output_dir="."):
    if not os.path.exists(file_path):
        return {"error": "File not found."}

    if not question or len(question.strip()) < 3:
        return {"error": "Please ask a valid question."}

    file_type = detect_file_type(file_path)

    if file_type is None:
        return {"error": "Unsupported file type. Upload a PDF or CSV."}

    if file_type == "rag":
        return handle_pdf(file_path, question, output_dir)

    elif file_type == "csv":
        return handle_csv(file_path, question, output_dir)


# ── HANDLE PDF (RAG) ─────────────────────
def handle_pdf(file_path, question, output_dir):
    global CACHE

    # avoid rebuilding DB repeatedly
    if CACHE["current_file"] != file_path:
        chroma_dir = os.path.join(output_dir, "chroma_db")
        build_knowledge_base(pdf_path=file_path, chroma_dir=chroma_dir)

        CACHE["pdf"] = True
        CACHE["current_file"] = file_path

    answer, sources = ask_pdf(question)

    return {
        "type": "pdf",
        "answer": answer,
        "sources": [s.page_content for s in sources] if sources else [],
    }


# ── HANDLE CSV ───────────────────────────
def handle_csv(file_path, question, output_dir):
    global CACHE

    # load once
    if CACHE["current_file"] != file_path:
        df = load_csv(file_path)
        CACHE["csv"] = df
        CACHE["current_file"] = file_path

    df = CACHE["csv"]

    result, chart = ask_csv(question, df, output_dir)

    return {"type": "csv", "answer": result, "chart": chart}
