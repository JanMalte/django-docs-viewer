from pathlib import Path

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.http import Http404
from django.utils._os import safe_join

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".svg", ".gif"}
MARKDOWN_SUFFIX = ".md"


def docs_root():
    return Path(settings.DOCS_VIEWER_ROOT)


def resolve_within_docs(relative_path):
    """Resolve a URL path against the docs directory case-insensitively, guarding against traversal.

    Returns the matching on-disk path with its real casing, or None when nothing matches.
    """
    root = docs_root()
    try:
        requested = Path(safe_join(str(root), relative_path))
    except (ValueError, SuspiciousFileOperation):
        raise Http404("Path outside documentation directory")

    resolved = root
    for part in requested.relative_to(root).parts:
        resolved = _matching_child(resolved, part)
        if resolved is None:
            return None
    return resolved


def _matching_child(directory, name):
    """The entry of directory whose name matches name case-insensitively, or None."""
    if not directory.is_dir():
        return None
    lowered = name.lower()
    for child in directory.iterdir():
        if child.name.lower() == lowered:
            return child
    return None


def is_image_request(doc_path):
    return Path(doc_path).suffix.lower() in IMAGE_SUFFIXES


def with_markdown_suffix(doc_path):
    return f"{without_markdown_suffix(doc_path)}{MARKDOWN_SUFFIX}"


def without_markdown_suffix(doc_path):
    if doc_path.lower().endswith(MARKDOWN_SUFFIX):
        return doc_path[: -len(MARKDOWN_SUFFIX)]
    return doc_path
