from django.urls import include, path

urlpatterns = [
    path("docs/", include("docs_viewer.urls")),
]
