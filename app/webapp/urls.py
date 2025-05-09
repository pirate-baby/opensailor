from django.contrib import admin
from django.urls import path, include
from webapp.api import api
from webapp.views import home, sailboats_index


urlpatterns = [
    path("", home, name="home"),
    path("sailboats/", sailboats_index, name="sailboats_index"),
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("accounts/", include("allauth.urls")),
]
