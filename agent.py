import os
import json
import subprocess
import re

# ==========================
# CONFIG
# ==========================

SUPPORTED_EXTENSIONS = [".txt", ".pdf", ".docx"]
MAX_CHARS = 2000
MAX_NAME_LENGTH = 60

GENERIC_WORDS = {
    "final", "latest", "version", "important",
    "document", "file", "new", "copy", "scan"
}

# ==========================
# TEXT EXTRACTION
# ==========================

def extract_text(path):
    ext = os.path.splitext(path)[1].lower()

    if ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext == ".pdf":
        import pdfplumber
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
        return text

    elif ext == ".docx":
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    return ""

# ==========================
# AI CALL (OLLAMA)
# ==========================

def ask_llm(prompt):
    process = subprocess.Popen(
        ["ollama", "run", "llama3"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )
    stdout, _ = process.communicate(prompt)
    return stdout.strip()

# ==========================
# PROMPT
# ==========================

def build_prompt(filename, content):
    return f"""
You are a strict document analyst AI.

Return ONLY valid JSON.
No markdown. No explanation.

Return format:
{{
  "document_type": "",
  "summary": "",
  "keywords": []
}}

Filename: {filename}

Content:
\"\"\"
{content[:MAX_CHARS]}
\"\"\"
"""

# ==========================
# INTELLIGENT NAMING ENGINE
# ==========================

def clean_words(words):
    cleaned = []
    for w in words:
        w = re.sub(r"[^a-zA-Z0-9]", "", w)
        if not w:
            continue
        if w.lower() in GENERIC_WORDS:
            continue
        cleaned.append(w.capitalize())
    return cleaned

def generate_filename(doc_type, keywords, extension):
    words = clean_words(keywords)

    if doc_type:
        words.insert(0, doc_type.capitalize())

    if not words:
        words = ["Untitled"]

    name = "_".join(words[:5])
    name = name[:MAX_NAME_LENGTH]

    return f"{name}{extension}"

# ==========================
# MAIN
# ==========================

def main():
    folder = input("Enter path to folder: ").strip()

    if not os.path.isdir(folder):
        print("❌ Invalid folder")
        return

    print("\n🧠 Intelligent agent running...\n")

    for file in os.listdir(folder):
        old_path = os.path.join(folder, file)
        ext = os.path.splitext(file)[1].lower()

        if not os.path.isfile(old_path) or ext not in SUPPORTED_EXTENSIONS:
            continue

        text = extract_text(old_path)
        if not text.strip():
            continue

        prompt = build_prompt(file, text)
        response = ask_llm(prompt)

        print("=" * 60)
        print(f"FILE: {file}")

        try:
            data = json.loads(response)

            doc_type = data.get("document_type", "").lower()
            keywords = data.get("keywords", [])

            if not isinstance(keywords, list):
                keywords = []

            new_name = generate_filename(doc_type, keywords, ext)
            new_path = os.path.join(folder, new_name)

            if os.path.exists(new_path):
                print(f"⚠️ Name exists, skipped → {new_name}")
                continue

            os.rename(old_path, new_path)

            print("TYPE:", doc_type)
            print("KEYWORDS:", keywords)
            print("✅ RENAMED →", new_name)

        except Exception:
            print("❌ AI failure, skipped")
            print(response)

    print("\n🎉 Agent finished cleanly.")

if __name__ == "__main__":
    main()
