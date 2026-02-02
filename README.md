# Intelligent File Renaming Agent

An AI-assisted document renaming agent that **reads the actual content of files**, understands their purpose, and renames them into **meaningful, structured, and human-readable filenames**.

This project is designed for engineers who want order, traceability, and semantic clarity in document-heavy directories — without manual effort.

---

## Why This Exists

File systems decay fast.

Folders end up with files named:

- `final_v2_latest.pdf`
- `scan1234.docx`
- `important_copy.txt`

These names carry **no semantic value**.

This agent fixes that by:
- Reading file content
- Understanding document intent
- Extracting keywords
- Generating clean, consistent filenames

The result is a filesystem that reflects **what the documents actually are**, not when or how they were saved.

---

## What the Agent Does

For each supported file in a folder, the agent:

1. Extracts textual content from the file
2. Sends the content to a local LLM (via Ollama)
3. Asks the model to strictly return structured JSON
4. Parses:
   - document type
   - summary
   - keywords
5. Filters noisy or generic terms
6. Generates a concise, readable filename
7. Renames the file safely (no overwrites)

All processing happens **locally**.

---

## Supported File Types

- `.txt`
- `.pdf`
- `.docx`

(Extensible by design)

---

## Naming Strategy (High-Level)

Generated filenames follow this structure:

Rules applied:
- Generic words like `final`, `latest`, `document`, `copy`, etc. are removed
- Keywords are normalized and capitalized
- Maximum filename length enforced
- Maximum keyword count enforced
- Existing filenames are never overwritten

### Example

Before: final_version_new.pdf
After: Invoice_Payment_Terms_Client.pdf


This is **not** a rule-only or regex-based tool.  
Semantic understanding is provided by the LLM.

---

## Requirements

### System
- Python 3.9+
- Windows / macOS / Linux

### Python Dependencies
- pdfplumber
- python-docx

### LLM Runtime
- Ollama installed
- `llama3` model available locally

---

## Installation

1. Clone the repository
2. Install Python dependencies:

   pip install pdfplumber python-docx
3. Ensure Ollama is installed and the model is available:

   ollama run llama3



---

## Usage

Run the agent:

When prompted, provide the absolute or relative path to the folder containing files.

The agent will:
- Process supported files
- Rename them intelligently
- Skip files it cannot safely analyze

All actions are logged to the console.

---

## Design Principles

- **Local-first**: No cloud APIs, no external data sharing
- **Strict outputs**: JSON-only LLM responses enforced
- **Safe by default**: No overwrites, no destructive behavior
- **Readable results**: Filenames optimized for humans
- **Minimal abstractions**: Clear, inspectable logic

---

## Non-Goals

- Not an OCR engine
- Not a UI-based document manager
- Not a cloud or SaaS product

This is a **focused engineering utility**, not a demo or toy project.

---

## Possible Enhancements

- Dry-run / preview mode
- Configurable naming templates
- Folder-level categorization
- Metadata tagging
- Pluggable LLM backends
- Execution audit logs

---

## License

MIT License

Free to use, modify, and extend.

---

## Author’s Note

This project intentionally avoids unnecessary frameworks and hype.
The goal is correctness, clarity, and real-world usefulness.

If you care about clean systems and meaningful automation, this tool fits naturally into your workflow.

