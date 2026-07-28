import fnmatch
import re
from pathlib import Path

import markdown

from .conf import default_title, skip_dirs, toc_depth
from .paths import docs_root

MARKDOWN_EXTENSIONS = ["fenced_code", "tables", "toc", "sane_lists"]

MENU_FILE = "menu.md"
# Matched case-insensitively for the docs-root landing page; also lead each folder's navigation
# group, ahead of the ordered pages. Kept lowercase and ordered by preference.
INDEX_FILENAMES = ["index.md", "readme.md"]

_HEADING_PATTERN = re.compile(r"^\s*#\s+(.+?)\s*$", re.MULTILINE)


def is_hidden(relative_path):
    """True when any directory in the path matches a configured skip pattern (see DOCS_VIEWER_SKIP_DIRS)."""
    directories = Path(relative_path).parts[:-1]
    return any(fnmatch.fnmatch(part, pattern) for part in directories for pattern in skip_dirs())


def _converter():
    return markdown.Markdown(
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs={"toc": {"toc_depth": toc_depth()}},
    )


def render_markdown(page):
    # Rendered from repo-authored, trusted markdown; templates inject the result with |safe.
    return _converter().convert(page.read_text(encoding="utf-8"))


def render_page(page):
    """Render a page to (content_html, toc_html); toc_html is empty when the page has no sub-headings."""
    converter = _converter()
    content_html = converter.convert(page.read_text(encoding="utf-8"))
    toc_html = converter.toc if converter.toc_tokens else ""
    return content_html, toc_html


def page_heading(page):
    """The page's first level-1 heading, or None when it has none."""
    match = _HEADING_PATTERN.search(page.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def is_index_filename(name):
    return name.lower() in INDEX_FILENAMES


def is_top_level_index(relative_path):
    """True for a landing-page file (index/README) sitting directly at the docs root."""
    relative = Path(relative_path)
    return relative.parent == Path() and is_index_filename(relative.name)


def discover_pages():
    root = docs_root()
    pages = []
    for page in root.rglob("*.md"):
        relative = page.relative_to(root)
        if is_hidden(relative) or page.name == MENU_FILE:
            continue
        # The top-level index/README is the landing page, not a nav entry.
        if is_top_level_index(relative):
            continue
        pages.append(page)
    return pages


def dedicated_index():
    """The docs-root index/README landing file, matched case-insensitively; None when absent."""
    root = docs_root()
    if not root.is_dir():
        return None
    by_name = {child.name.lower(): child.name for child in root.iterdir() if child.is_file()}
    for candidate in INDEX_FILENAMES:
        if candidate in by_name:
            return by_name[candidate]
    return None


def landing_relative_path():
    index = dedicated_index()
    if index is not None:
        return index
    pages = discover_pages()
    return pages[0].relative_to(docs_root()).as_posix() if pages else None


def site_title():
    """The docs title, taken from the index page's heading; a default when there is no index."""
    default = default_title()
    index = dedicated_index()
    if index is None:
        return default
    return page_heading(docs_root() / index) or default
