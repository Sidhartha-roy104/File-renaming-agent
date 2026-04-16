# Data Flow Diagram (DFD) — Intelligent File Renaming Agent

This document describes the data flows within the **Intelligent File Renaming Agent** project (`agent.py` and `meta_analysis.py`). It covers a **Level 0 Context Diagram** and a **Level 1 Detailed DFD** for each module.

---

## 1. System Overview

The project consists of two Python scripts:

| Script | Purpose |
|---|---|
| `agent.py` | Scans a folder, analyses each supported file with a local LLM, and renames files to semantically meaningful names. |
| `meta_analysis.py` | Analyses a single `.txt` file, generates an AI description, and stores metadata via Windows Alternate Data Streams (ADS) or a sidecar `.meta.json` file. |

Both scripts communicate with a **local Ollama LLM runtime** (`llama3`). No data leaves the machine.

---

## 2. Level 0 — Context Diagram (agent.py)

The entire renaming system is treated as a single process. It interacts with three external entities.

```
                      ┌──────────────────────────────────────────┐
                      │                                          │
  ┌──────────┐        │   ┌──────────────────────────────────┐   │        ┌──────────────────────┐
  │          │ folder │   │                                  │   │ prompt │                      │
  │  User    │───────►│   │   Intelligent File Renaming      │───┼───────►│  Ollama LLM Runtime  │
  │(operator)│        │   │         Agent System             │   │        │      (llama3)         │
  │          │        │   │                                  │◄──┼────────│                      │
  └──────────┘        │   └──────────────────────────────────┘   │ JSON   └──────────────────────┘
                      │            │            ▲                │
                      │   renamed  │            │ raw file       │
                      │   files    │            │ content        │
                      │            ▼            │                │
                      │   ┌──────────────────────────────────┐   │
                      │   │       Local File System          │   │
                      │   │   (folder of .txt/.pdf/.docx)    │   │
                      │   └──────────────────────────────────┘   │
                      │                                          │
                      └──────────────────────────────────────────┘
```

### External Entities

| Entity | Role |
|---|---|
| **User (operator)** | Provides the target folder path via the CLI prompt. |
| **Local File System** | Source of original files; destination for renamed files. |
| **Ollama LLM Runtime** | Local AI service that receives prompts and returns structured JSON analysis. |

### Top-Level Data Flows

| Flow | Description |
|---|---|
| User → System | Folder path string entered at the CLI |
| System → File System | Read: list of files and their raw content |
| System → File System | Write: renamed file (via `os.rename`) |
| System → Ollama | Structured text prompt (filename + content excerpt) |
| Ollama → System | JSON string: `{ document_type, summary, keywords }` |
| System → User (console) | Progress messages, rename confirmations, or skip warnings |

---

## 3. Level 1 DFD — agent.py (File Renaming Pipeline)

Each numbered circle below is a discrete process within `agent.py`.

```
  User
   │
   │ folder path
   ▼
┌──────────────────┐
│  P1              │
│  Accept & Validate│
│  User Input      │
└────────┬─────────┘
         │ valid folder path
         ▼
┌──────────────────┐       ┌──────────────────────────┐
│  P2              │◄──────│  DS1: Local File System   │
│  File Discovery  │       │  (folder of files)        │
│  & Filtering     │──────►│                           │
└────────┬─────────┘       └──────────────────────────┘
         │ file path + extension
         │ (only .txt / .pdf / .docx)
         ▼
┌──────────────────┐       ┌──────────────────────────┐
│  P3              │◄──────│  DS1: Local File System   │
│  Text Extraction │       │  (file bytes)             │
│  (txt/pdf/docx)  │
└────────┬─────────┘
         │ raw text content (≤ 2000 chars)
         ▼
┌──────────────────┐
│  P4              │
│  Build LLM       │
│  Prompt          │
└────────┬─────────┘
         │ structured prompt string
         ▼
┌──────────────────┐       ┌──────────────────────────┐
│  P5              │──────►│  E1: Ollama LLM Runtime   │
│  LLM Analysis    │       │      (llama3)             │
│  (Ollama call)   │◄──────│                           │
└────────┬─────────┘       └──────────────────────────┘
         │ raw JSON string
         ▼
┌──────────────────┐
│  P6              │
│  Parse & Validate│
│  JSON Response   │
└────────┬─────────┘
         │ doc_type (str), keywords (list)
         ▼
┌──────────────────┐
│  P7              │
│  Generate New    │
│  Filename        │
│  (clean + join)  │
└────────┬─────────┘
         │ new filename string
         ▼
┌──────────────────┐       ┌──────────────────────────┐
│  P8              │──────►│  DS1: Local File System   │
│  Safe File       │       │  (renamed file)           │
│  Rename          │       └──────────────────────────┘
│  (no overwrite)  │
└──────────────────┘
```

### Process Descriptions

| ID | Process | Input | Output | Key Logic |
|---|---|---|---|---|
| **P1** | Accept & Validate User Input | Folder path (string from stdin) | Validated directory path | Exits if path is not a directory |
| **P2** | File Discovery & Filtering | Directory path | List of `(file, ext)` pairs | `os.listdir` + extension check against `SUPPORTED_EXTENSIONS` |
| **P3** | Text Extraction | File path + extension | Plain text string | Dispatches to `pdfplumber` (PDF), `python-docx` (DOCX), or built-in `open` (TXT) |
| **P4** | Build LLM Prompt | Filename, text excerpt | Formatted prompt string | Injects filename and up to 2 000 characters of content; requests strict JSON output |
| **P5** | LLM Analysis | Prompt string | Raw JSON string | Spawns `ollama run llama3` subprocess via `stdin`/`stdout` pipe |
| **P6** | Parse & Validate JSON | Raw JSON string | `doc_type` (str), `keywords` (list) | `json.loads`; falls back gracefully on parse failure; normalises non-list keywords |
| **P7** | Generate New Filename | `doc_type`, `keywords`, extension | New filename string | Removes generic words (`GENERIC_WORDS`), capitalises, joins with `_`, enforces max length |
| **P8** | Safe File Rename | Old path, new filename | Renamed file on disk | Skips if destination already exists (`os.path.exists`); uses `os.rename` |

### Data Stores

| ID | Store | Description |
|---|---|---|
| **DS1** | Local File System | The target folder supplied by the user; read for file content, written with renamed files |

---

## 4. Level 0 — Context Diagram (meta_analysis.py)

```
                      ┌──────────────────────────────────────────┐
                      │                                          │
  ┌──────────┐ choice │   ┌──────────────────────────────────┐   │ prompt  ┌──────────────────────┐
  │          │ + path │   │                                  │───┼────────►│  Ollama LLM Runtime  │
  │  User    │───────►│   │   TXT File Metadata Manager      │   │         │      (llama3)         │
  │(operator)│        │   │       (meta_analysis.py)         │◄──┼─────────│                      │
  │          │◄───────│   │                                  │   │ descr.  └──────────────────────┘
  └──────────┘ display│   └──────────────────────────────────┘   │
    metadata  output  │            │            ▲                │
                      │  metadata  │            │ .txt content   │
                      │  written   │            │ + file stats   │
                      │            ▼            │                │
                      │   ┌──────────────────────────────────┐   │
                      │   │       Local File System          │   │
                      │   │  (input .txt, output .meta.json  │   │
                      │   │   or Windows ADS stream)         │   │
                      │   └──────────────────────────────────┘   │
                      │                                          │
                      └──────────────────────────────────────────┘
```

---

## 5. Level 1 DFD — meta_analysis.py (Metadata Pipeline)

```
  User
   │
   │ choice (analyze / view) + file path
   ▼
┌──────────────────┐
│  P1              │
│  Accept User     │
│  Choice & Path   │
└────────┬─────────┘
         │ validated .txt file path + choice
         ▼
┌──────────────────┐       ┌──────────────────────────┐
│  P2              │◄──────│  DS2: Local File System   │
│  Extract File    │       │  (.txt file + OS stats)   │
│  Metadata        │
└────────┬─────────┘
         │ metadata dict (name, size, dates, content preview)
         ▼
┌──────────────────┐
│  P3              │
│  Build           │
│  Description     │
│  Prompt          │
└────────┬─────────┘
         │ prompt string
         ▼
┌──────────────────┐       ┌──────────────────────────┐
│  P4              │──────►│  E1: Ollama LLM Runtime   │
│  LLM Description │       │      (llama3)             │
│  Generation      │◄──────│                           │
└────────┬─────────┘       └──────────────────────────┘
         │ description string (2–3 sentences)
         ▼
┌──────────────────┐       ┌──────────────────────────────────────┐
│  P5              │──────►│  DS3a: Windows ADS stream             │
│  Store / Display │       │  (filepath:description.txt)           │
│  Metadata        │──────►│                                       │
│                  │       │  DS3b: Sidecar .meta.json file        │
└──────────────────┘       └──────────────────────────────────────┘
```

### Process Descriptions

| ID | Process | Input | Output | Key Logic |
|---|---|---|---|---|
| **P1** | Accept User Choice & Path | Menu choice (1/2) + file path from stdin | Validated `.txt` path + operation flag | Validates file existence and `.txt` extension |
| **P2** | Extract File Metadata | File path | Metadata dict: name, size (bytes/KB), created, modified, content preview | `os.stat` for filesystem metadata; reads first 1 000 characters for preview |
| **P3** | Build Description Prompt | Filename, content preview | Prompt string | Asks LLM for a concise 2–3 sentence description only |
| **P4** | LLM Description Generation | Prompt string | Plain-text description | Spawns `ollama run llama3` subprocess; returns `stdout` |
| **P5** | Store / Display Metadata | Description + metadata dict + storage method | Metadata persisted to ADS and/or `.meta.json` | Writes to `filepath:description.txt` (ADS) and/or `basename.meta.json` (sidecar JSON); displays via console |

### Data Stores

| ID | Store | Description |
|---|---|---|
| **DS2** | Local File System (input) | The `.txt` file to be analysed |
| **DS3a** | Windows ADS Stream | Hidden metadata stream attached to the original file (`filepath:description.txt`) |
| **DS3b** | Sidecar `.meta.json` | Companion JSON file containing description, analysis date, and OS metadata |

---

## 6. Key Data Items Glossary

| Data Item | Description |
|---|---|
| `folder path` | Absolute or relative path to the directory supplied by the user |
| `file path` | Full path to a single document within the folder |
| `raw text content` | Extracted plain text from `.txt`, `.pdf`, or `.docx` file (capped at 2 000 characters for the LLM) |
| `prompt` | Formatted string containing the filename, content excerpt, and strict JSON schema instructions |
| `JSON response` | LLM output: `{ "document_type": "…", "summary": "…", "keywords": […] }` |
| `doc_type` | Normalised document category string (e.g. `"invoice"`, `"contract"`) |
| `keywords` | List of meaningful terms extracted by the LLM |
| `new filename` | Generated string: `DocType_Keyword1_Keyword2…Keyword5.ext` (max 60 characters) |
| `description` | 2–3 sentence natural-language description of a `.txt` file produced by the LLM |
| `metadata dict` | Python dict of OS file stats: name, size, created/modified timestamps, content preview |

---

## 7. Design Constraints Reflected in the DFD

- **Local-only processing** — Ollama runs on the same machine; no data leaves the host (no network flows to external services).
- **No destructive writes** — P8 (`Safe File Rename`) checks for destination existence before renaming; no data is overwritten.
- **Strict LLM contract** — P4 (`Build LLM Prompt`) and P6 (`Parse & Validate JSON`) enforce a JSON-only response format; any deviation causes the file to be skipped without modification.
- **Bounded text input** — Only the first 2 000 characters of a file are sent to the LLM (`MAX_CHARS = 2000`), limiting token usage and latency.
