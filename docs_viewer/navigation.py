import re

from django.urls import reverse
from django.utils.html import escape

from .pages import (
    MENU_FILE,
    dedicated_index,
    discover_pages,
    is_index_filename,
    page_heading,
    render_markdown,
)
from .paths import docs_root, without_markdown_suffix

_NUMERIC_PREFIX_PATTERN = re.compile(r"^(\d+)[-_ ]")


def build_sidebar_html(current_path):
    menu_file = docs_root() / MENU_FILE
    if menu_file.is_file():
        return render_markdown(menu_file)

    tree = _build_tree(discover_pages())
    parts = ['<ul class="docs-nav">']

    if home_link := _home_link(current_path):
        parts.append(home_link)

    _render_tree(tree, current_path, parts)

    parts.append("</ul>")
    return "".join(parts)


def _build_tree(pages):
    """Arrange discovered pages into a nested tree mirroring their folder structure to any depth."""
    root = docs_root()
    tree = {"pages": [], "dirs": {}}
    for page in pages:
        node = tree
        for folder in page.relative_to(root).parts[:-1]:
            node = node["dirs"].setdefault(folder, {"pages": [], "dirs": {}})
        node["pages"].append(page)
    return tree


def _render_tree(node, current_path, parts):
    """Emit a folder's pages, then a nested group for each subfolder, recursing into each."""
    for page in sorted(node["pages"], key=_page_sort_key):
        parts.append(_page_link(page, current_path))
    for folder in sorted(node["dirs"], key=str.lower):
        parts.append(f'<li class="docs-nav-group"><span>{escape(_humanize(folder))}</span><ul>')
        _render_tree(node["dirs"][folder], current_path, parts)
        parts.append("</ul></li>")


def _home_link(current_path):
    """The top-level index/README, linked to the docs home. Skipped when the landing is just the
    first discovered page (no dedicated index) — that page is already listed in the nav."""
    index = dedicated_index()
    if index is None:
        return None
    return _nav_link(
        reverse("docs:home"),
        _page_label(docs_root() / index),
        is_active=current_path == without_markdown_suffix(index),
    )


def _page_link(page, current_path):
    doc_path = without_markdown_suffix(page.relative_to(docs_root()).as_posix())
    return _nav_link(
        reverse("docs:detail", kwargs={"doc_path": doc_path}),
        _page_label(page),
        is_active=doc_path == current_path,
    )


def _nav_link(href, label, is_active):
    active = " active" if is_active else ""
    return f'<li><a class="docs-nav-link{active}" href="{href}">{escape(label)}</a></li>'


def _page_label(page):
    """The page's first level-1 heading, or a humanized filename when it has none."""
    return page_heading(page) or _humanize(page.stem)


def _humanize(name):
    return _NUMERIC_PREFIX_PATTERN.sub("", name).replace("-", " ").replace("_", " ").title()


def _page_sort_key(page):
    return (0 if is_index_filename(page.name) else 1, page.name.lower())
