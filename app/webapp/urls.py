from django.contrib import admin
from django.urls import path, include
from webapp.api import api
from webapp.views.terms_of_service import terms_of_service
from webapp.views.vessel_note import (
    vessel_note_create,
    vessel_note_message_add_form,
    vessel_note_message_add_save,
    vessel_note_message_update,
    vessel_note_message_reply_form,
    vessel_note_message_reply_save,
    vessel_note_share,
)
from webapp.views.vessel_access import (
    vessel_access_request,
    vessel_manage_roles,
    vessel_access_approve,
    vessel_access_deny,
    vessel_remove_user,
    vessel_add_user,
    vessel_change_user_role,
    vessel_toggle_privacy,
)
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
    # path("vessels/<int:pk>/note/", vessel_note_update, name="vessel_note_update"),
    path(
        "vessels/<int:pk>/note/create/", vessel_note_create, name="vessel_note_create"
    ),
    path(
        "vessels/note/<int:note_id>/add_message/",
        vessel_note_message_add_form,
        name="vessel_note_message_add_form",
    ),
    path(
        "vessels/note/<int:note_id>/add_message/save/",
        vessel_note_message_add_save,
        name="vessel_note_message_add_save",
    ),
    path(
        "vessels/note/message/<int:message_id>/update/",
        vessel_note_message_update,
        name="vessel_note_message_update",
    ),
    path(
        "vessels/note/message/<int:message_id>/reply/",
        vessel_note_message_reply_form,
        name="vessel_note_message_reply_form",
    ),
    path(
        "vessels/note/message/<int:message_id>/reply/save/",
        vessel_note_message_reply_save,
        name="vessel_note_message_reply_save",
    ),
    path(
        "vessels/note/<int:note_id>/share/", vessel_note_share, name="vessel_note_share"
    ),
    # Vessel access management
    path("vessels/<int:pk>/access/request/", vessel_access_request, name="vessel_access_request"),
    path("vessels/<int:pk>/manage-roles/", vessel_manage_roles, name="vessel_manage_roles"),
    path("vessels/<int:pk>/access/<int:request_id>/approve/", vessel_access_approve, name="vessel_access_approve"),
    path("vessels/<int:pk>/access/<int:request_id>/deny/", vessel_access_deny, name="vessel_access_deny"),
    path("vessels/<int:pk>/remove-user/<int:user_id>/", vessel_remove_user, name="vessel_remove_user"),
    path("vessels/<int:pk>/add-user/", vessel_add_user, name="vessel_add_user"),
    path("vessels/<int:pk>/change-role/<int:user_id>/", vessel_change_user_role, name="vessel_change_user_role"),
    path("vessels/<int:pk>/toggle-privacy/", vessel_toggle_privacy, name="vessel_toggle_privacy"),
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("accounts/", include("allauth.urls")),
    path("terms/", terms_of_service, name="terms_of_service"),
]
