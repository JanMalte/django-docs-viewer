from django.conf import settings
from django.utils.translation import gettext_lazy as _

DEFAULT_TITLE = _("Documentation")
DEFAULT_BASE_TEMPLATE = "docs_viewer/base.html"
DEFAULT_TOC_DEPTH = "2-3"
DEFAULT_SKIP_DIRS = ["_*"]


def login_required():
    return getattr(settings, "DOCS_VIEWER_LOGIN_REQUIRED", True)


def default_title():
    return getattr(settings, "DOCS_VIEWER_TITLE", DEFAULT_TITLE)


def base_template():
    return getattr(settings, "DOCS_VIEWER_BASE_TEMPLATE", DEFAULT_BASE_TEMPLATE)


def toc_depth():
    return getattr(settings, "DOCS_VIEWER_TOC_DEPTH", DEFAULT_TOC_DEPTH)


def skip_dirs():
    """Glob patterns; a page is hidden when any directory in its path matches one."""
    return getattr(settings, "DOCS_VIEWER_SKIP_DIRS", DEFAULT_SKIP_DIRS)
