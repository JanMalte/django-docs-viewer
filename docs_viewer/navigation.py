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

    root_pages, groups = _group_pages(discover_pages())
    parts = ['<ul class="docs-nav">']

    if home_link := _home_link(current_path):
        parts.append(home_link)

    for page in sorted(root_pages, key=_page_sort_key):
        parts.append(_page_link(page, current_path))

    for group in sorted(groups, key=str.lower):
        parts.append(f'<li class="docs-nav-group"><span>{escape(_humanize(group))}</span><ul>')
        for page in sorted(groups[group], key=_page_sort_key):
            parts.append(_page_link(page, current_path))
        parts.append("</ul></li>")

    parts.append("</ul>")
    return "".join(parts)


def _group_pages(pages):
    """Partition discovered pages into top-level pages and folder groups keyed by folder name."""
    root = docs_root()
    root_pages = []
    groups = {}
    for page in pages:
        relative = page.relative_to(root)
        if len(relative.parts) == 1:
            root_pages.append(page)  # flat docs: pages live directly under the docs directory
        else:
            groups.setdefault(relative.parts[0], []).append(page)
    return root_pages, groups


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
