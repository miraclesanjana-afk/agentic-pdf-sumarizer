# Agentic PDF Summarizer

A Streamlit app that summarizes PDF documents with **Google Gemini** through a
**LangGraph-backed LangChain agent**. The agent can load a PDF, summarize it,
analyze its structure and extract key quotes by choosing the right tools.

This project is based on the structure of
[niti007/pdfsummarizer-gemini](https://github.com/niti007/pdfsummarizer-gemini),
extended with an agentic tool-calling architecture and tests.

## Project status

- [x] **Phase 0** — validate Gemini API key and GitHub login
- [x] **Phase 1** — project foundation, config and Streamlit skeleton
- [x] **Phase 2** — PDF ingestion and chunking
- [ ] **Phase 3** — LangGraph agent with tools
- [ ] **Phase 4** — full Streamlit UI
- [ ] **Phase 5** — hardening and documentation
- [ ] **Phase 6** — publish to GitHub

## Setup

Requires Python 3.10+.

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Put your Gemini API key in `.env`:

```
GEMINI_API_KEY=your_real_key_here
```

Get a key at <https://aistudio.google.com/apikey>. Never commit `.env`.

## Run

```powershell
.venv\Scripts\python.exe scripts\validate_phase0.py
streamlit run app.py
```

## Development

```powershell
pip install -r requirements-dev.txt
pytest
ruff check .
```
