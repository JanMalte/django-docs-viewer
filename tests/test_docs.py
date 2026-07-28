from pathlib import Path

from django.http import Http404
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from django.utils import translation

from docs_viewer.paths import (
    is_image_request,
    resolve_within_docs,
    with_markdown_suffix,
    without_markdown_suffix,
)


class DocsPathHelperTests(SimpleTestCase):
    def test_with_markdown_suffix_normalizes_suffix(self):
        self.assertEqual(with_markdown_suffix("manual/01-getting-started"), "manual/01-getting-started.md")
        self.assertEqual(with_markdown_suffix("manual/01-getting-started.md"), "manual/01-getting-started.md")

    def test_without_markdown_suffix_strips_md_suffix(self):
        self.assertEqual(without_markdown_suffix("manual/01-getting-started.md"), "manual/01-getting-started")
        self.assertEqual(without_markdown_suffix("manual/01-getting-started.MD"), "manual/01-getting-started")

    def test_image_request_detection_uses_suffix_only(self):
        self.assertTrue(is_image_request("manual/images/status-legend.png"))
        self.assertFalse(is_image_request("manual/01-getting-started"))

    def test_resolve_within_docs_blocks_traversal(self):
        with self.assertRaisesMessage(Http404, "Path outside documentation directory"):
            resolve_within_docs("../secret")


@override_settings(DOCS_VIEWER_LOGIN_REQUIRED=False)
class DocsViewTests(SimpleTestCase):
    def test_landing_page_renders(self):
        response = self.client.get(reverse("docs:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "docs_viewer/detail.html")

    def test_nested_page_renders_content(self):
        response = self.client.get(reverse("docs:detail", kwargs={"doc_path": "manual/01-getting-started"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This page explains how to get started")

    def test_auto_discovery_sidebar_lists_folders(self):
        response = self.client.get(reverse("docs:home"))
        self.assertContains(response, "docs-nav")
        self.assertContains(response, reverse("docs:detail", kwargs={"doc_path": "manual/01-getting-started"}))

    def test_index_appears_as_home_nav_item(self):
        response = self.client.get(reverse("docs:home"))
        self.assertContains(response, f'docs-nav-link active" href="{reverse("docs:home")}"')

    def test_md_suffix_is_stripped(self):
        response = self.client.get(reverse("docs:detail", kwargs={"doc_path": "manual/01-getting-started.md"}))
        self.assertEqual(response.status_code, 200)

    def test_embedded_image_is_served(self):
        response = self.client.get(reverse("docs:detail", kwargs={"doc_path": "manual/images/status-legend.png"}))
        self.assertEqual(response.status_code, 200)

    def test_page_url_is_case_insensitive(self):
        response = self.client.get(reverse("docs:detail", kwargs={"doc_path": "Manual/01-Getting-Started"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This page explains how to get started")

    def test_image_url_is_case_insensitive(self):
        response = self.client.get(reverse("docs:detail", kwargs={"doc_path": "Manual/Images/Status-Legend.png"}))
        self.assertEqual(response.status_code, 200)

    def test_path_traversal_is_blocked(self):
        response = self.client.get("/docs/../secret")
        self.assertEqual(response.status_code, 404)

    def test_missing_page_returns_404(self):
        response = self.client.get(reverse("docs:detail", kwargs={"doc_path": "manual/does-not-exist"}))
        self.assertEqual(response.status_code, 404)

    def test_title_uses_index_heading(self):
        response = self.client.get(reverse("docs:home"))
        self.assertContains(response, "<title>Django Docs Viewer</title>")

    def test_bundled_base_template_is_used_by_default(self):
        response = self.client.get(reverse("docs:home"))
        self.assertTemplateUsed(response, "docs_viewer/base.html")

    def test_header_shows_title_and_back_link(self):
        response = self.client.get(reverse("docs:home"))
        self.assertContains(response, '<h1 class="docs-title">Django Docs Viewer</h1>')
        self.assertContains(response, '<a class="docs-back" href="/">')

    def test_back_link_is_translated(self):
        with translation.override("de"):
            response = self.client.get(reverse("docs:home"))
            self.assertContains(response, "Zurück")
        with translation.override("fr"):
            response = self.client.get(reverse("docs:home"))
            self.assertContains(response, "Retour")

    def test_default_title_is_translated(self):
        with translation.override("de"), override_settings(DOCS_VIEWER_ROOT=flat_root()):
            response = self.client.get(reverse("docs:home"))
            self.assertContains(response, "<title>Dokumentation</title>")

    def test_page_with_subheadings_renders_toc(self):
        response = self.client.get(reverse("docs:detail", kwargs={"doc_path": "manual/02-configuration"}))
        self.assertContains(response, 'class="docs-toc"')
        self.assertContains(response, 'class="toc"')
        self.assertContains(response, 'href="#settings"')
        self.assertContains(response, 'href="#templates"')

    def test_toc_excludes_page_h1_by_default(self):
        response = self.client.get(reverse("docs:detail", kwargs={"doc_path": "manual/02-configuration"}))
        self.assertNotContains(response, 'href="#configuration"')

    def test_page_without_subheadings_has_no_toc(self):
        response = self.client.get(reverse("docs:detail", kwargs={"doc_path": "manual/01-getting-started"}))
        self.assertNotContains(response, 'class="docs-toc"')

    def test_toc_depth_setting_can_include_h1(self):
        with override_settings(DOCS_VIEWER_TOC_DEPTH="1-3"):
            response = self.client.get(reverse("docs:detail", kwargs={"doc_path": "manual/02-configuration"}))
            self.assertContains(response, 'href="#configuration"')

    def test_underscore_dirs_are_hidden_by_default(self):
        response = self.client.get(reverse("docs:home"))
        self.assertNotContains(response, reverse("docs:detail", kwargs={"doc_path": "_drafts/wip"}))

    def test_hidden_page_is_not_served(self):
        response = self.client.get(reverse("docs:detail", kwargs={"doc_path": "_drafts/wip"}))
        self.assertEqual(response.status_code, 404)

    def test_skip_dirs_setting_accepts_glob_patterns(self):
        with override_settings(DOCS_VIEWER_SKIP_DIRS=["man*"]):
            home = self.client.get(reverse("docs:home"))
            self.assertNotContains(home, reverse("docs:detail", kwargs={"doc_path": "manual/01-getting-started"}))
            page = self.client.get(reverse("docs:detail", kwargs={"doc_path": "manual/01-getting-started"}))
            self.assertEqual(page.status_code, 404)
            # A custom pattern replaces the default, so underscore dirs are no longer hidden.
            draft = self.client.get(reverse("docs:detail", kwargs={"doc_path": "_drafts/wip"}))
            self.assertEqual(draft.status_code, 200)

    def test_missing_image_returns_404(self):
        response = self.client.get(reverse("docs:detail", kwargs={"doc_path": "manual/images/nope.png"}))
        self.assertEqual(response.status_code, 404)

    def test_missing_docs_root_returns_404(self):
        with override_settings(DOCS_VIEWER_ROOT="/nonexistent/docs/root"):
            response = self.client.get(reverse("docs:home"))
            self.assertEqual(response.status_code, 404)


_PROJECT_TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [Path(__file__).resolve().parent / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]


@override_settings(
    TEMPLATES=_PROJECT_TEMPLATES,
    DOCS_VIEWER_BASE_TEMPLATE="layout.html",
    DOCS_VIEWER_LOGIN_REQUIRED=False,
)
class DocsProjectLayoutTests(SimpleTestCase):
    def test_base_template_setting_selects_project_layout(self):
        response = self.client.get(reverse("docs:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "layout.html")
        self.assertContains(response, "PROJECT LAYOUT")


class DocsLoginRequiredTests(SimpleTestCase):
    def test_anonymous_is_redirected_by_default(self):
        response = self.client.get(reverse("docs:home"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].startswith("/login/"))

    @override_settings(DOCS_VIEWER_LOGIN_REQUIRED=False)
    def test_anonymous_allowed_when_login_not_required(self):
        response = self.client.get(reverse("docs:home"))
        self.assertEqual(response.status_code, 200)


def flat_root():
    from django.conf import settings

    return settings.BASE_DIR / "docs" / "manual"


@override_settings(DOCS_VIEWER_LOGIN_REQUIRED=False)
class DocsTitleSettingTests(SimpleTestCase):
    def test_default_title_setting_used_without_index(self):
        with override_settings(DOCS_VIEWER_ROOT=flat_root(), DOCS_VIEWER_TITLE="Handbook"):
            response = self.client.get(reverse("docs:home"))
            self.assertContains(response, "<title>Handbook</title>")


@override_settings(DOCS_VIEWER_LOGIN_REQUIRED=False)
class DocsFlatDocsTests(SimpleTestCase):
    """A DOCS_VIEWER_ROOT whose pages live directly at its root, with no subfolders."""

    def test_flat_pages_appear_in_nav(self):
        with override_settings(DOCS_VIEWER_ROOT=flat_root()):
            response = self.client.get(reverse("docs:home"))
            self.assertContains(response, reverse("docs:detail", kwargs={"doc_path": "01-getting-started"}))

    def test_flat_page_renders(self):
        with override_settings(DOCS_VIEWER_ROOT=flat_root()):
            response = self.client.get(reverse("docs:detail", kwargs={"doc_path": "01-getting-started"}))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "This page explains how to get started")
