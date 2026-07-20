import re
import hashlib

_HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)')


class Chunk:
    def __init__(
        self,
        text: str,
        heading_path: list[str] = None,
        source_url: str = "",
        tool: str = "",
        doc_type: str = ""
    ):
        self.text = text
        self.heading_path = heading_path if heading_path is not None else []
        self.source_url = source_url
        self.tool = tool
        self.doc_type = doc_type
        self.id = self._make_chunk_id()
        self.metadata = self._build_chunk_metadata()
        self.text_to_embed = self._text_with_context()
        self.embeddings = []
    
    def _make_chunk_id(self) -> str:
        raw = f"{self.source_url}::{self.text}"
        return hashlib.sha256(raw.encode()).hexdigest()

    # A makeshift contextual augmentation
    def _text_with_context(self) -> str:
        if not self.heading_path:
            return self.text
        breadcrumb = " > ".join(self.heading_path)
        return f"{breadcrumb}\n{self.text}"
    
    def _build_chunk_metadata(self) -> dict:
        return {
            "text": self.text,           # the CLEAN original, for display and for the LLM
            "heading_path": self.heading_path,
            "source_url": self.source_url,
            "tool": self.tool,
            "doc_type": self.doc_type
        }

def extract_strings_to_embed(chunks: list[Chunk]) -> list[str]:
    return [c.text_to_embed for c in chunks ]

class Document:
    def __init__(
        self,
        markdown_text: str,
        source_url: str,
        tool: str,
        doc_type: str
    ):
        self.markdown_text = markdown_text
        self.source_url = source_url
        self.tool = tool
        self.doc_type = doc_type
    
    def _pack_sentences(self, text: str, chunk_size: int = 1500) -> list[str]:
        text = text.replace('\n', ' ')
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)

        chunks = []
        current_chunk = []
        current_size = 0

        for s in sentences:
            s = s.strip()
            if not s:
                continue

            s_size = len(s)

            if current_size + s_size < chunk_size:
                current_chunk.append(s)
                current_size += s_size
            else:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [s]
                current_size = s_size

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks
    
    def _split_into_sections(self) -> list[dict]:
        lines = self.markdown_text.split('\n')
        sections = []
        heading_stack = []  # list of (level, title)
        current_lines = []

        def flush():
            body = '\n'.join(current_lines).strip()
            if body:
                sections.append({
                    "heading_path": [title for _, title in heading_stack],
                    "text": body,
                })

        for line in lines:
            match = _HEADING_RE.match(line)
            if match:
                flush()
                current_lines = []
                level = len(match.group(1))
                title = match.group(2).strip()

                # Pop headings at the same or deeper level; a new H2 replaces the old H2
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                heading_stack.append((level, title))
            else:
                current_lines.append(line)

        flush()
        return sections

    def chunk_document(
        self,
        chunk_size: int = 1500,
    ) -> list[Chunk]:
        sections = self._split_into_sections()
        chunks = []

        for section in sections:
            body = section["text"]
            pieces = [body] if len(body) <= chunk_size else self._pack_sentences(body, chunk_size=chunk_size)

            for piece in pieces:
                chunks.append(Chunk(
                    text=piece,
                    heading_path=section["heading_path"],
                    source_url=self.source_url,
                    tool=self.tool,
                    doc_type=self.doc_type,
                ))

        return chunks