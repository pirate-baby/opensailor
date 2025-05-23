from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from webapp.models.vessel_note import VesselNote, NoteMessage
from webapp.models.vessel import Vessel


class VesselNoteCreateForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "class": "form-textarea"}),
        label="First message",
    )


@login_required
def vessel_note_create(request, pk):
    vessel = get_object_or_404(Vessel, pk=pk)
    if request.method == "POST":
        form = VesselNoteCreateForm(request.POST)
        if form.is_valid():
            note = VesselNote.objects.create(vessel=vessel, user=request.user)
            note.save()
            NoteMessage.objects.create(
                vessel_note=note,
                user=request.user,
                content=form.cleaned_data["content"],
            )
            messages.success(request, "Note created!")
            return redirect("vessel_detail", pk=vessel.pk)
    else:
        form = VesselNoteCreateForm()
    return render(
        request, "webapp/vessels/note_create.html", {"form": form, "vessel": vessel}
    )


class NoteMessageForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-textarea"}),
        label="Add message",
    )


@login_required
@require_http_methods(["GET"])
def vessel_note_message_add_form(request, note_id):
    note = get_object_or_404(VesselNote, pk=note_id)
    form = NoteMessageForm()
    return render(
        request,
        "webapp/components/note_message_form.html",
        {"form": form, "note": note, "action_url": request.path},
    )


@login_required
@require_http_methods(["POST"])
def vessel_note_message_add_save(request, note_id):
    note = get_object_or_404(VesselNote, pk=note_id)
    form = NoteMessageForm(request.POST)
    if form.is_valid():
        message = NoteMessage.objects.create(
            vessel_note=note,
            user=request.user,
            content=form.cleaned_data["content"],
        )
        return render(
            request,
            "webapp/components/note_message_item.html",
            {"message": message, "request": request},
        )
    return render(
        request,
        "webapp/components/note_message_form.html",
        {"form": form, "note": note, "action_url": request.path},
    )


@login_required
@require_http_methods(["GET"])
def vessel_note_message_edit_form(request, message_id):
    message = get_object_or_404(NoteMessage, pk=message_id)
    if message.user != request.user:
        return JsonResponse({"error": "Permission denied."}, status=403)
    form = NoteMessageForm(initial={"content": message.content})
    return render(
        request,
        "webapp/components/note_message_form.html",
        {
            "form": form,
            "note": message.vessel_note,
            "action_url": request.path,
            "edit_mode": True,
            "message_id": message.id,
        },
    )


@login_required
@require_http_methods(["POST"])
def vessel_note_message_update(request, message_id):
    message = get_object_or_404(NoteMessage, pk=message_id)
    if message.user != request.user:
        return JsonResponse({"error": "Permission denied."}, status=403)
    content = request.POST.get("content", "").strip()
    if not content:
        return JsonResponse({"error": "Content cannot be empty."}, status=400)
    message.content = content
    message.save()
    return render(
        request,
        "webapp/components/note_message_item.html",
        {"message": message, "request": request},
    )


@login_required
@require_http_methods(["GET"])
def vessel_note_message_reply_form(request, message_id):
    parent_message = get_object_or_404(NoteMessage, pk=message_id)
    note = parent_message.vessel_note
    form = NoteMessageForm()
    return render(
        request,
        "webapp/components/note_message_form.html",
        {
            "form": form,
            "note": note,
            "action_url": request.path,
            "reply_to": parent_message.id,
        },
    )


@login_required
@require_http_methods(["POST"])
def vessel_note_message_reply_save(request, message_id):
    parent_message = get_object_or_404(NoteMessage, pk=message_id)
    note = parent_message.vessel_note
    form = NoteMessageForm(request.POST)
    if form.is_valid():
        message = NoteMessage.objects.create(
            vessel_note=note,
            user=request.user,
            content=form.cleaned_data["content"],
        )
        # Optionally, you could add a parent/child relationship for threading
        return render(
            request,
            "webapp/components/note_message_item.html",
            {"message": message, "request": request},
        )
    return render(
        request,
        "webapp/components/note_message_form.html",
        {
            "form": form,
            "note": note,
            "action_url": request.path,
            "reply_to": parent_message.id,
        },
    )


@login_required
def vessel_note_share(request, note_id):
    note = get_object_or_404(VesselNote, pk=note_id)
    if note.owner != request.user:
        messages.error(request, "You do not have permission to share this note.")
        return redirect("vessel_detail", pk=note.vessel.pk)
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("vessel_detail", pk=note.vessel.pk)
    email = request.POST.get("email", "").strip().lower()
    if not email:
        messages.error(request, "Please provide an email address.")
        return redirect("vessel_detail", pk=note.vessel.pk)
    User = get_user_model()
    try:
        user_to_share = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, f"No user found with email {email}.")
        return redirect("vessel_detail", pk=note.vessel.pk)
    if user_to_share == request.user:
        messages.error(request, "You already own this note.")
        return redirect("vessel_detail", pk=note.vessel.pk)
    if note.shared_with.filter(pk=user_to_share.pk).exists():
        messages.info(
            request, f"{user_to_share.email} already has access to this note."
        )
        return redirect("vessel_detail", pk=note.vessel.pk)
    note.shared_with.add(user_to_share)
    note.save()
    # Send email with link to the note
    vessel_url = request.build_absolute_uri(
        reverse("vessel_detail", args=[note.vessel.pk])
    )
    subject = f"A note has been shared with you on {settings.APP_NAME}"
    message = f"You have been given access to a note for vessel '{note.vessel.name}'.\n\nView the vessel and note here: {vessel_url}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_to_share.email])
    messages.success(request, f"Shared note with {user_to_share.email}!")
    return redirect("vessel_detail", pk=note.vessel.pk)
