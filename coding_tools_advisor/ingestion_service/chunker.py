import re
from parser import fetch_html, clean_html


def split_text(text: str, chunk_size: int = 500) -> list:
    chunks = []
    current_chunk = []
    current_chunk_size = 0

    text = text.replace('\n', ' ')
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)

    for s in sentences:
        if not s.endswith('.'):
            s += '.'

        s_size = len(s)

        if s_size+current_chunk_size < chunk_size:
            current_chunk.append(s)
            current_chunk_size += s_size
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [s]
            current_chunk_size = s_size
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


html = fetch_html("https://builtin.com/articles/claude-code-codex-cursor-github-copilot-comparison")
md_txt = clean_html(html)

print(split_text(md_txt))