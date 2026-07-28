from django.urls import path

from .views import DocsView

app_name = "docs"

urlpatterns = [
    path("", DocsView.as_view(), name="home"),
    path("<path:doc_path>", DocsView.as_view(), name="detail"),
]
