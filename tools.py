"""LangChain tools exposed to the LangGraph agent."""

from __future__ import annotations

from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, tool

from config import Settings
from pdf_processor import DocumentStore, PDFProcessingError, process_pdf
from summarizer import analyze_structure, extract_quotes
from summarizer import summarize_document as run_summarize


def build_tools(store: DocumentStore, llm: BaseChatModel, settings: Settings) -> list[BaseTool]:
    """Build the tool set bound to a document store and language model."""

    @tool
    def load_pdf(file_path: str) -> str:
        """Load a local PDF file and chunk it. Returns the doc_id needed by other tools."""
        path = Path(file_path)
        try:
            document = process_pdf(
                path.name,
                path.read_bytes(),
                chunk_tokens=settings.chunk_tokens,
                overlap_tokens=settings.overlap_tokens,
            )
        except (OSError, PDFProcessingError) as exc:
            return f"Error loading PDF: {exc}"

        store.add(document)
        return (
            f"Loaded {document.name} as doc_id={document.doc_id} "
            f"({document.page_count} pages, {len(document.chunks)} chunks)."
        )

    @tool
    def summarize_document(doc_id: str, style: str) -> str:
        """Summarize a loaded document using one of: brief, detailed, bullet_points, executive."""
        try:
            document = store.get(doc_id)
            return run_summarize(llm, document.chunks, style)
        except (KeyError, ValueError) as exc:
            return f"Error summarizing: {exc}"

    @tool
    def analyze_document_structure(doc_id: str) -> str:
        """Analyze the structure and main themes of a loaded document."""
        try:
            document = store.get(doc_id)
            return analyze_structure(llm, document.text)
        except (KeyError, ValueError) as exc:
            return f"Error analyzing structure: {exc}"

    @tool
    def extract_key_quotes(doc_id: str) -> str:
        """Extract important verbatim quotes from a loaded document."""
        try:
            document = store.get(doc_id)
            return extract_quotes(llm, document.text)
        except (KeyError, ValueError) as exc:
            return f"Error extracting quotes: {exc}"

    @tool
    def list_loaded_documents() -> str:
        """List documents already loaded, with their doc_ids and chunk counts."""
        documents = store.list_documents()
        if not documents:
            return "No documents loaded yet. Call load_pdf first."
        return "\n".join(
            f"{doc.doc_id}: {doc.name} ({len(doc.chunks)} chunks)" for doc in documents
        )

    return [
        load_pdf,
        summarize_document,
        analyze_document_structure,
        extract_key_quotes,
        list_loaded_documents,
    ]
