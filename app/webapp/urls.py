from django.contrib import admin
from django.urls import path, include
from webapp.api import api
from webapp.views import (
    home, sailboats_index, sailboat_create, sailboat_detail,
    sailboat_update, sailboat_delete
)


urlpatterns = [
    path("", home, name="home"),
    path("sailboats/", sailboats_index, name="sailboats_index"),
    path("sailboats/create/", sailboat_create, name="sailboat_create"),
    path("sailboats/<int:pk>/", sailboat_detail, name="sailboat_detail"),
    path("sailboats/<int:pk>/update/", sailboat_update, name="sailboat_update"),
    path("sailboats/<int:pk>/delete/", sailboat_delete, name="sailboat_delete"),
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("accounts/", include("allauth.urls")),
]
