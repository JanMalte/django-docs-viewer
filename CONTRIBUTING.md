# Contributing

Thanks for your interest in improving django-docs-viewer.

## Prerequisites

- **Python** — supported versions are 3.10–3.14. `.python-version` lists all of
  them (3.12 first, so it is the default interpreter); the rest let `tox` run
  the full matrix locally.
- **[Poetry](https://python-poetry.org/)** — manages the virtualenv,
  dependencies, and builds.
- **[pyenv](https://github.com/pyenv/pyenv)** (recommended) — the easiest way to
  install the several Python versions that `tox` runs against. Without it, a
  single system Python is enough to test against one version.
- **GNU gettext** (`msgfmt`) — required only for translation work (compiling
  catalogs). Install it with your OS package manager, e.g. `brew install
  gettext` (macOS) or `apt install gettext` (Debian/Ubuntu).
- **Git**.

Everything else (`tox`, `pre-commit`, `coverage`, `ruff`) is installed by
`poetry install`.

## Getting started

Optional, but recommended: use [pyenv](https://github.com/pyenv/pyenv) to
install the supported Python versions. The committed `.python-version` is a
pyenv file listing all of them; pyenv makes the first (3.12) the default
`python` and exposes the rest as `python3.x` so `tox` can find them (Poetry
itself does not read this file).

```
pyenv install --skip-existing         # installs the versions in .python-version that are missing
```

Poetry 2.0+ then uses the default interpreter automatically. To make the choice
explicit — or on older Poetry, which otherwise uses its own interpreter — bind
the environment to it:

```
poetry env use "$(pyenv which python)"
```

Then install the dependencies and Git hooks:

```
poetry install
poetry run pre-commit install
```

The commands below assume this Poetry environment. Prefix them with
`poetry run` (as shown) or activate the virtualenv first.

## Running the tests

Against your current interpreter:

```
poetry run python manage.py test tests
```

Across the full supported Python/Django matrix:

```
poetry run tox
```

## Coverage

Check that your changes are covered by tests (configuration lives in
`pyproject.toml`):

```
poetry run coverage run manage.py test tests
poetry run coverage report
```

Generate a browsable HTML report in `htmlcov/`:

```
poetry run coverage html
```

## Translations

User-facing strings are marked for translation and catalogs live in
`docs_viewer/locale/` (English, German, French). After changing or adding a
translatable string, update and compile the catalogs:

```
cd docs_viewer
poetry run django-admin makemessages -l de -l en -l fr
poetry run django-admin compilemessages
```

Compiling requires the GNU `gettext` tools (`msgfmt`). The compiled `.mo` files
are committed so they ship in the released package.

## Before opening a pull request

- Make sure the tests pass.
- Check that new code is covered by tests (`poetry run coverage report`).
- Run `poetry run pre-commit run --all-files` to apply formatting and linting.
- Keep changes small and focused.

## Releasing

Publishing is automated: pushing a `v*` tag triggers the `publish` workflow
(`.github/workflows/publish.yml`), which runs the full test matrix and, only if
it passes, builds the package and uploads it to PyPI via Trusted Publishing
(OIDC — no API tokens). The version lives only in `pyproject.toml`.

### Cutting a release

1. Bump the version and push the commit:

   ```
   poetry version patch      # or: minor / major / prerelease
   git commit -am "Release v$(poetry version -s)"
   git push
   ```

2. Tag the release and push the tag — this triggers the gated publish:

   ```
   git tag "v$(poetry version -s)"
   git push origin "v$(poetry version -s)"
   ```

   The `publish` workflow runs the test matrix and, if it passes, builds and
   uploads to PyPI.

### Manual fallback

To publish without CI, build and upload with a PyPI API token:

```
poetry build --clean
poetry config pypi-token.pypi <your-pypi-token>
poetry publish
```
