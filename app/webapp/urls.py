from django.contrib import admin
from django.urls import path, include
from webapp.api import api
from app.webapp.views.views import (
    home,
    sailboats_index,
    sailboat_create,
    sailboat_detail,
    sailboat_update,
    sailboat_delete,
    vessels_index,
    vessel_create,
    vessel_detail,
    vessel_update,
    vessel_delete,
    vessel_note_update,
)


urlpatterns = [
    path("", home, name="home"),
    path("sailboats/", sailboats_index, name="sailboats_index"),
    path("sailboats/create/", sailboat_create, name="sailboat_create"),
    path("sailboats/<int:pk>/", sailboat_detail, name="sailboat_detail"),
    path("sailboats/<int:pk>/update/", sailboat_update, name="sailboat_update"),
    path("sailboats/<int:pk>/delete/", sailboat_delete, name="sailboat_delete"),
    path("vessels/", vessels_index, name="vessels_index"),
    path("vessels/create/", vessel_create, name="vessel_create"),
    path("vessels/<int:pk>/", vessel_detail, name="vessel_detail"),
    path("vessels/<int:pk>/update/", vessel_update, name="vessel_update"),
    path("vessels/<int:pk>/delete/", vessel_delete, name="vessel_delete"),
    path("vessels/<int:pk>/note/", vessel_note_update, name="vessel_note_update"),
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("accounts/", include("allauth.urls")),
]
