import re
from parser import fetch_html, clean_html


_HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)')

def split_into_sections(markdown_text: str) -> list[dict]:
    lines = markdown_text.split('\n')
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


def _pack_sentences(text: str, chunk_size: int = 1500) -> list[str]:
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

from dataclasses import dataclass, field


@dataclass
class Chunk:
    text: str
    heading_path: list[str] = field(default_factory=list)


def chunk_document(markdown_text: str, chunk_size: int = 1500) -> list[Chunk]:
    sections = split_into_sections(markdown_text)
    chunks = []

    for section in sections:
        body = section["text"]

        if len(body) <= chunk_size:
            chunks.append(Chunk(text=body, heading_path=section["heading_path"]))
        else:
            for piece in _pack_sentences(body, chunk_size=chunk_size):
                chunks.append(Chunk(text=piece, heading_path=section["heading_path"]))

    return chunks


html = fetch_html("https://builtin.com/articles/claude-code-codex-cursor-github-copilot-comparison")
md_txt = clean_html(html)

chunks = chunk_document(md_txt)


for c in chunks:
    # if c.heading_path:
    #     print(c.heading_path)
    # else:
    #     print('no heading')
    # print(c.text)
    print(c)
    print("\n")