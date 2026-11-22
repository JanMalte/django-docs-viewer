from django.contrib.auth.views import redirect_to_login
from django.http import Http404
from django.shortcuts import render
from django.views import View
from django.views.static import serve

from .conf import back_url, base_template, login_required
from .navigation import build_sidebar_html
from .pages import directory_index, is_hidden, landing_relative_path, render_page, site_title
from .paths import (
    docs_root,
    is_image_request,
    resolve_within_docs,
    with_markdown_suffix,
    without_markdown_suffix,
)


class DocsView(View):
    def dispatch(self, request, *args, **kwargs):
        if login_required() and not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, doc_path=""):
        if is_image_request(doc_path):
            image = resolve_within_docs(doc_path)
            if image is None or not image.is_file() or is_hidden(image.relative_to(docs_root())):
                raise Http404("Documentation page not found")
            return serve(request, image.relative_to(docs_root()).as_posix(), document_root=str(docs_root()))

        if not doc_path:
            relative_path = landing_relative_path()
            if relative_path is None:
                raise Http404("No documentation available")
            markdown_path = resolve_within_docs(relative_path)
        else:
            markdown_path = resolve_within_docs(with_markdown_suffix(doc_path))
            if markdown_path is None or not markdown_path.is_file():
                directory = resolve_within_docs(without_markdown_suffix(doc_path))
                markdown_path = directory_index(directory)

        if markdown_path is None or not markdown_path.is_file():
            raise Http404("Documentation page not found")

        relative = markdown_path.relative_to(docs_root())
        if is_hidden(relative):
            raise Http404("Documentation page not found")

        canonical_path = without_markdown_suffix(relative.as_posix())
        content_html, toc_html = render_page(markdown_path)
        return render(
            request,
            "docs_viewer/detail.html",
            {
                "base_template": base_template(),
                "site_title": site_title(),
                "back_url": back_url(),
                "content_html": content_html,
                "toc_html": toc_html,
                "sidebar_html": build_sidebar_html(canonical_path),
            },
        )
