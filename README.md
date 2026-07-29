# django-docs-viewer

[![tests](https://github.com/JanMalte/django-docs-viewer/actions/workflows/run-tests.yml/badge.svg)](https://github.com/JanMalte/django-docs-viewer/actions/workflows/run-tests.yml)
[![PyPI version](https://img.shields.io/pypi/v/django-docs-viewer.svg)](https://pypi.org/project/django-docs-viewer/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/django-docs-viewer.svg)](https://pypi.org/project/django-docs-viewer/)
[![Supported Django versions](https://img.shields.io/badge/django-4.2%20%7C%205.0%20%7C%205.1%20%7C%205.2%20%7C%206.0-blue.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/github/license/JanMalte/django-docs-viewer.svg)](https://github.com/JanMalte/django-docs-viewer/blob/main/LICENSE)

A simple in-app Markdown documentation viewer for Django.

Point it at a directory of Markdown files and it serves them as browsable
documentation pages with an auto-generated sidebar. No build step, no database,
no models — pages are read from disk and rendered on request.

## Features

- Renders Markdown files (`fenced_code`, `tables`, `toc`, `sane_lists`).
- Auto-generated sidebar navigation grouped by folder — or hand-written via a `menu.md` file.
- Automatic per-page table of contents built from each page's headings.
- Case-insensitive, traversal-safe URL resolution.
- Serves images referenced from your Markdown.
- Login required by default; can be made public with one setting.
- Self-contained, overridable templates.

## How it compares

The niche is *zero-build, database-free, self-navigating docs*: Markdown
rendered at request time, with the sidebar and per-page table of contents built
from the folder tree and headings.
[django-markdown-view](https://github.com/rgs258/django-markdown-view) also
renders at request time but builds no navigation;
[Django Spellbook](https://django-spellbook.org/) builds navigation but via a
generation step and as part of a larger Markdown-components framework.

## Installation

```
pip install django-docs-viewer
```

## Usage

Add the app to `INSTALLED_APPS` and point `DOCS_VIEWER_ROOT` at your docs
directory:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "docs_viewer",
]

DOCS_VIEWER_ROOT = BASE_DIR / "docs"
```

Include the URLs:

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    # ...
    path("docs/", include("docs_viewer.urls")),
]
```

By default the docs require an authenticated user and redirect anonymous
visitors to `LOGIN_URL`, so make sure your project has a login view — or set
`DOCS_VIEWER_LOGIN_REQUIRED = False` to make the docs public.

Your docs directory can be flat:

```
docs/
├── README.md                     # landing page + site title
├── 01-getting-started.md
└── 02-configuration.md
```

or nested, with folders becoming sidebar groups:

```
docs/
├── README.md                     # landing page + site title
└── manual/
    ├── 01-getting-started.md
    ├── 02-configuration.md
    └── images/
        └── status-legend.png
```

Folders nest to any depth, and each level becomes a sidebar group, so a
subfolder per language keeps translated pages neatly separated instead of
listing every language in one flat group:

```
docs/
├── README.md                     # landing page + site title
└── manual/
    ├── deutsch/
    │   ├── 01-erste-schritte.md
    │   └── 02-konfiguration.md
    ├── english/
    │   ├── 01-getting-started.md
    │   └── 02-configuration.md
    └── francais/
        ├── 01-prise-en-main.md
        └── 02-configuration.md
```

Group labels come from the folder name, humanized (dashes and underscores
become spaces, and it is title-cased), so name folders in lowercase — `deutsch`
renders as **Deutsch** in the sidebar.

Pages sort by filename within their folder (the index/`README` first). Prefix
filenames with a zero-padded number (`01-`, `02-`) to control the order; the
prefix is stripped from the sidebar label, so `01-getting-started.md` shows as
**Getting started**. Zero-pad once you pass nine pages, otherwise `10-…` sorts
ahead of `2-…`.

## Settings

| Setting                      | Default                   | Description                                              |
| ---------------------------- | ------------------------- | -------------------------------------------------------- |
| `DOCS_VIEWER_ROOT`           | *(required)*              | Path to the directory containing your Markdown files.    |
| `DOCS_VIEWER_BASE_TEMPLATE`  | `"docs_viewer/base.html"` | Template the docs page extends. Point at your own layout. |
| `DOCS_VIEWER_LOGIN_REQUIRED` | `True`                    | Redirect anonymous users to `LOGIN_URL`. Set `False` to make docs public. |
| `DOCS_VIEWER_TITLE`          | `"Documentation"`         | Fallback page title when no index heading is available.  |
| `DOCS_VIEWER_TOC_DEPTH`      | `"2-3"`                   | Heading levels included in the per-page table of contents. |
| `DOCS_VIEWER_SKIP_DIRS`      | `["_*"]`                  | Glob patterns; directories matching any are hidden (excluded from navigation and not served). A custom value replaces the default, so include `"_*"` if you still want underscore-prefixed directories hidden. |

The page title is taken from the first level-1 heading of the index
(`index.md` or `README.md`) at the docs root, falling back to
`DOCS_VIEWER_TITLE`.

## Customizing the template

The docs page (`docs_viewer/detail.html`) extends whatever template
`DOCS_VIEWER_BASE_TEMPLATE` names, resolved dynamically at render time. By
default it extends the minimal `docs_viewer/base.html` bundled with the app, so
it works with no configuration.

To make docs pages inherit your site's chrome, point the setting at your own
base template:

```python
DOCS_VIEWER_BASE_TEMPLATE = "myproject/base.html"
```

Your base template only needs a `content` block (and, optionally, a `title`
block):

```html
{% block title %}{% endblock %}
...
{% block content %}{% endblock %}
```

To change the docs page itself rather than the surrounding layout, override
`docs_viewer/detail.html` in your own template directory.

## Custom navigation

By default the sidebar is generated from your folder tree. To control it by
hand instead, add a `menu.md` file at the root of your docs directory. When
present, its rendered Markdown replaces the auto-generated sidebar (and
`menu.md` itself is never served as a page).

Write it as a normal Markdown list of links:

```markdown
- [Introduction](/docs/)
- [Getting started](/docs/manual/01-getting-started)
- [Configuration](/docs/manual/02-configuration)
```

The links are rendered as-is, so point them at the paths where you mounted the
viewer — the `/docs/` prefix above matches `path("docs/", include(...))`.

## Translations

The interface strings ship translated into English, German and French. The
active language follows Django's usual i18n machinery, so enable
`django.middleware.locale.LocaleMiddleware` (and keep `USE_I18N = True`) if you
want the docs to follow the request's language.

## Development

```
poetry install
poetry run python manage.py test tests
```

Run the full support matrix with [tox](https://tox.wiki):

```
poetry run tox
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for coverage, translations, and the
pull-request checklist.

## License

MIT
