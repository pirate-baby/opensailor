from django.contrib import admin
from django.urls import path
from webapp.api import api
from webapp.views import home


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
