from .parser import fetch_html, clean_html
from .chunker import Document, extract_text_to_embed
from shared.openai_client import OpenAIClient
from .indexer import upsert_chunks

seeds = [
    {
        'url': 'https://claude.com/pricing',
        'tool': 'Claude',
        'doc_type': 'pricing'
    },
    {
        'url': 'https://openai.com/api/pricing/',
        'tool': 'Codex',
        'doc_type': 'pricing'
    },
    {
        'url': 'https://github.com/features/copilot/plans',
        'tool': 'Copilot',
        'doc_type': 'pricing'
    },
    {
        'url': 'https://cursor.com/pricing',
        'tool': 'Cursor',
        'doc_type': 'pricing'
    },
    {
        'url': 'https://builtin.com/articles/claude-code-codex-cursor-github-copilot-comparison',
        'tool': 'comparison',
        'doc_type': 'comparison'
    },
    {
        'url': 'https://uvik.net/blog/claude-code-vs-cursor-vs-copilot-vs-codex-2026/',
        'tool': 'comparison',
        'doc_type': 'comparison'
    },
    {
        'url': 'https://www.nxcode.io/resources/news/cursor-vs-claude-code-vs-github-copilot-2026-ultimate-comparison',
        'tool': 'comparison',
        'doc_type': 'comparison'
    },
    {
        'url': 'https://aiviewer.ai/guides/best-ai-coding-tools-compared/',
        'tool': 'comparison',
        'doc_type': 'comparison'
    },
    {
        'url': 'https://www.sitepoint.com/claude-code-vs-cursor-vs-copilot-the-2026-developer-comparison',
        'tool': 'comparison',
        'doc_type': 'comparison'
    },
    {
        'url': 'http://clarista.io/blog/claude-code-vs-cursor-vs-codex',
        'tool': 'comparison',
        'doc_type': 'comparison'
    },
]


for s in seeds:
    url = s['url']
    tool = s['tool']
    doc_type = s['doc_type']

    html = fetch_html(url)
    md_text = clean_html(html)

    doc = Document(markdown_text=md_text, source_url=url, tool=tool, doc_type=doc_type)
    chunks = doc.chunk_document()

    strings = extract_text_to_embed(chunks)

    oc = OpenAIClient()
    embeddings = oc.embed(strings)
    upserted = upsert_chunks(chunks, embeddings)

