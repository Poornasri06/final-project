import re
import os
from typing import List, Dict, Any
import PyPDF2

class RecursiveStructureChunker:
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 75):
        self.chunk_size = chunk_size  # Target words/tokens (~600)
        self.chunk_overlap = chunk_overlap  # Overlap (~75 words)

    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF page by page with section header detection."""
        pages_content = []
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for idx, page in enumerate(reader.pages):
                    try:
                        raw_text = page.extract_text() or ""
                    except Exception:
                        raw_text = ""
                    cleaned = self.clean_text(raw_text)
                    if cleaned:
                        pages_content.append({
                            "page_number": idx + 1,
                            "text": cleaned
                        })
        except Exception as e:
            raise ValueError(f"Failed to extract PDF content: {str(e)}")
        return pages_content

    def clean_text(self, text: str) -> str:
        """Clean extracted document text."""
        if not text:
            return ""
        # Normalize whitespace and strip weird control chars
        text = re.sub(r'[\r\t]', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()

    def detect_sections(self, page_text: str) -> List[Dict[str, str]]:
        """Detect heading titles within page text using regex heuristics."""
        lines = page_text.split('\n')
        sections = []
        current_section = "General"
        current_buffer = []

        heading_pattern = re.compile(
            r'^(?:[0-9]+\.|\b(?:ABSTRACT|INTRODUCTION|METHODS|RESULTS|DISCUSSION|CONCLUSION|RISK FACTORS|GUIDELINES|TREATMENT|COMPLICATIONS|PREVENTION|MANAGEMENT|EVIDENCE|SUMMARY)\b)',
            re.IGNORECASE
        )

        for line in lines:
            line_str = line.strip()
            if heading_pattern.match(line_str) and len(line_str) < 100:
                if current_buffer:
                    sections.append({
                        "section": current_section,
                        "content": "\n".join(current_buffer)
                    })
                    current_buffer = []
                current_section = line_str.upper()
            else:
                if line_str:
                    current_buffer.append(line_str)

        if current_buffer:
            sections.append({
                "section": current_section,
                "content": "\n".join(current_buffer)
            })

        return sections if sections else [{"section": "General", "content": page_text}]

    def chunk_document(self, document_id: str, document_title: str, pages_content: List[Dict[str, Any]], domain: str = "Healthcare", category: str = "General Healthcare") -> List[Dict[str, Any]]:
        """Chunk document text recursively preserving sections, pages, and token overlap."""
        chunks = []
        chunk_counter = 0

        for page_data in pages_content:
            page_num = page_data["page_number"]
            page_text = page_data["text"]
            sections = self.detect_sections(page_text)

            for sec in sections:
                sec_name = sec["section"]
                sec_content = sec["content"]
                words = sec_content.split()

                if not words:
                    continue

                if len(words) <= self.chunk_size:
                    chunk_counter += 1
                    chunks.append({
                        "document_id": document_id,
                        "document_name": document_title,
                        "chunk_index": chunk_counter,
                        "page_number": page_num,
                        "section": sec_name,
                        "text": sec_content,
                        "token_count": len(words),
                        "domain": domain,
                        "category": category
                    })
                else:
                    # Recursive sliding window over words with controlled overlap
                    start = 0
                    while start < len(words):
                        end = min(start + self.chunk_size, len(words))
                        chunk_words = words[start:end]
                        chunk_text = " ".join(chunk_words)

                        chunk_counter += 1
                        chunks.append({
                            "document_id": document_id,
                            "document_name": document_title,
                            "chunk_index": chunk_counter,
                            "page_number": page_num,
                            "section": sec_name,
                            "text": chunk_text,
                            "token_count": len(chunk_words),
                            "domain": domain,
                            "category": category
                        })

                        if end == len(words):
                            break
                        start += (self.chunk_size - self.chunk_overlap)

        return chunks
