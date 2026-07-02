import re
import httpx
from bs4 import BeautifulSoup, Tag
from markdownify import markdownify as md

from mock_data import html_string


soup = BeautifulSoup(html_string, "html.parser")

_CONTAINER_SELECTORS = [
    "main",
    "article",
    '[role="main"]',
    ".docs-content",
    ".documentation",
    ".main-content",
    ".article-content",
    ".post-content",
    "#content",
    "#main-content",
]

_UNWANTED_TAGS = ["script", "style", "nav", "header", "footer", "aside", "head"]

#TODO: Make this an async function
def _fetch_html(url: str, timeout_in_secs: float = 20.0) -> BeautifulSoup:
    with httpx.Client() as client:
        response = client.get(
            url, follow_redirects=True, timeout=timeout_in_secs
        )

        return response.text

def _decompose_unwanted_tags(soup: BeautifulSoup) -> BeautifulSoup:
    for tag in soup(_UNWANTED_TAGS):
        tag.decompose()
    
    return soup

def _pick_main_container(soup: BeautifulSoup) -> Tag:
    for selector in _CONTAINER_SELECTORS:
        candidate = soup.select_one(selector)
        if candidate and candidate.get_text(strip=True):
            return candidate

    if soup.body:
        return soup.body
    return soup

def _normalize_text(text: str) -> str:
    norm_txt = re.sub(r'\n{3,}', '\n\n', text)
    return norm_txt.strip()

def _convert_to_markdown(soup: BeautifulSoup) -> str:
    md_text = md(str(soup), heading_style="ATX")
    return _normalize_text(md_text)

def clean_html(html: str = html_string) -> str:
    soup = BeautifulSoup(html_string, "html.parser")
    content = _decompose_unwanted_tags(soup)
    main_content = _pick_main_container(content)
    md_content = _convert_to_markdown(main_content)
    print(md_content)

html = _fetch_html("https://builtin.com/articles/claude-code-codex-cursor-github-copilot-comparison")
clean_html(html)

