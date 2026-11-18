# Walkthrough

This guide takes you from a fresh checkout to a working summarization run.

## 1. Prerequisites

- Python 3.10+ (tested on 3.12)
- A Google Gemini API key from <https://aistudio.google.com/apikey>
- GitHub CLI (`gh`) if you plan to publish the project

## 2. Install

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
```

Edit `.env` and set `GEMINI_API_KEY`. Keep this file out of git.

## 3. Validate credentials

```powershell
.venv\Scripts\python.exe scripts\validate_phase0.py
```

This performs a **live** Gemini call and checks `gh auth status`. It prints only a
short fingerprint of the key, never the key itself.

If GitHub is not logged in:

```powershell
gh auth login --web --git-protocol https
```

## 4. Run the app

```powershell
streamlit run app.py
```

In the browser:

1. Upload a PDF.
2. Pick a summary style.
3. Optionally enable structure analysis and key quotes.
4. Click **Summarize**.
5. Watch the tool-call progress, then read the final answer.
6. Download `summary.txt` and `chunk_stats.csv`.

## 5. What happens internally

1. The uploaded bytes are written to a temporary PDF file.
2. The agent receives a request containing that path and the chosen options.
3. `load_pdf` extracts text with pypdf, cleans whitespace, and splits it into
   token-limited overlapping chunks stored in an in-memory `DocumentStore`.
4. `summarize_document` summarizes each chunk with Gemini, then combines those
   summaries into one final answer (map→reduce).
5. Optional tools add structure analysis and quotes.
6. The UI streams LangGraph node updates so tool calls are visible, then offers
   downloads.

## 6. Tests and checks

```powershell
pytest
ruff check .
.venv\Scripts\python.exe scripts\check_secrets.py
```

All tests run offline: fake chat models stand in for Gemini, and tiny PDFs are
generated in memory.

## 7. Publishing

The final phase creates the remote repository, commits the work and pushes `main`.
No credentials or `.env` contents are committed.
