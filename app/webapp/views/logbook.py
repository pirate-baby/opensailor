from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django import forms
from django.views.decorators.http import require_http_methods
from django.forms import inlineformset_factory
from django.utils import timezone

from webapp.models.vessel import Vessel
from webapp.models.logbook import LogEntry, LogEntryLocation, LogEntryAttachment
from webapp.models.media import Media
from webapp.decorators import vessel_crew_or_skipper_required


class LogEntryForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 6, "class": "form-textarea"}),
        label="Log Content",
        help_text="Write your log entry in markdown format. You can include links, lists, and formatting.",
    )

    log_timestamp = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-input",
                "step": "60",  # Allow minute precision, not seconds
            }
        ),
        label="Log Date & Time",
        help_text="When did this log event occur?",
    )

    class Meta:
        model = LogEntry
        fields = ["title", "content", "log_timestamp"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Optional: Brief title for this entry",
                }
            ),
        }
        help_texts = {
            "title": "Optional short title to summarize this log entry",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial datetime to current time if creating new entry
        if not self.instance.pk:
            # Format datetime for HTML5 datetime-local input
            now = timezone.now()
            self.fields["log_timestamp"].initial = now.strftime("%Y-%m-%dT%H:%M")


class LogEntryLocationForm(forms.ModelForm):
    class Meta:
        model = LogEntryLocation
        fields = [
            "name",
            "latitude",
            "longitude",
            "location_type",
            "order",
            "speed_knots",
            "heading_degrees",
            "depth_feet",
            "wind_speed_knots",
            "wind_direction_degrees",
            "temperature_f",
            "barometric_pressure",
            "sea_state",
            "visibility_miles",
            "timestamp",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Location name (optional)"}
            ),
            "latitude": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "step": "0.000001",
                    "placeholder": "e.g. 37.7749",
                }
            ),
            "longitude": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "step": "0.000001",
                    "placeholder": "e.g. -122.4194",
                }
            ),
            "location_type": forms.Select(attrs={"class": "form-select"}),
            "order": forms.NumberInput(attrs={"class": "form-input", "min": "0"}),
            "speed_knots": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.1", "min": "0"}
            ),
            "heading_degrees": forms.NumberInput(
                attrs={"class": "form-input", "min": "0", "max": "359"}
            ),
            "depth_feet": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.1", "min": "0"}
            ),
            "wind_speed_knots": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.1", "min": "0"}
            ),
            "wind_direction_degrees": forms.NumberInput(
                attrs={"class": "form-input", "min": "0", "max": "359"}
            ),
            "temperature_f": forms.NumberInput(attrs={"class": "form-input"}),
            "barometric_pressure": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.01", "min": "25", "max": "35"}
            ),
            "sea_state": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "e.g. Calm, Light chop, Moderate seas",
                }
            ),
            "visibility_miles": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.1", "min": "0"}
            ),
            "timestamp": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-input"}
            ),
        }


class LogEntryAttachmentForm(forms.ModelForm):
    file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={"class": "form-input", "multiple": False}
        ),
        help_text="Upload images, documents, receipts, or manuals",
    )

    class Meta:
        model = LogEntryAttachment
        fields = ["attachment_type", "description"]
        widgets = {
            "attachment_type": forms.Select(attrs={"class": "form-select"}),
            "description": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Optional description"}
            ),
        }

    def save(self, commit=True):
        attachment = super().save(commit=False)

        if self.cleaned_data.get("file"):
            # Create Media object for the uploaded file
            media = Media(
                uploaded_by=self.instance.log_entry.author,
                original_filename=self.cleaned_data["file"].name,
            )
            media.save()
            media.file.save(
                self.cleaned_data["file"].name, self.cleaned_data["file"], save=True
            )
            attachment.media = media

        if commit:
            attachment.save()
        return attachment


# Inline formsets for locations and attachments
LocationFormSet = inlineformset_factory(
    LogEntry,
    LogEntryLocation,
    form=LogEntryLocationForm,
    extra=0,
    can_delete=True,
    fields=[
        "name",
        "latitude",
        "longitude",
        "location_type",
        "order",
        "speed_knots",
        "heading_degrees",
        "depth_feet",
        "wind_speed_knots",
        "wind_direction_degrees",
        "temperature_f",
        "barometric_pressure",
        "sea_state",
        "visibility_miles",
        "timestamp",
    ],
)

AttachmentFormSet = inlineformset_factory(
    LogEntry,
    LogEntryAttachment,
    form=LogEntryAttachmentForm,
    extra=0,
    can_delete=True,
    fields=["attachment_type", "description"],
)


def _process_attachment_uploads(request, attachments, log_entry):
    """Helper to process attachment file uploads"""
    for i, attachment in enumerate(attachments):
        attachment.log_entry = log_entry
        
        file_field_name = f"attachments-{i}-file"
        if file_field_name in request.FILES:
            uploaded_file = request.FILES[file_field_name]
            
            media = Media(
                uploaded_by=request.user,
                original_filename=uploaded_file.name,
            )
            media.save()
            media.file.save(uploaded_file.name, uploaded_file, save=True)
            attachment.media = media
            
            if (
                media.media_type == "image"
                and attachment.attachment_type == "other"
            ):
                attachment.attachment_type = "image"
        
        attachment.save()


def _process_attachment_uploads_edit(request, attachments, log_entry):
    """Helper to process attachment file uploads for edit"""
    for i, attachment in enumerate(attachments):
        attachment.log_entry = log_entry
        
        file_field_name = f"attachments-{i}-file"
        if file_field_name in request.FILES:
            uploaded_file = request.FILES[file_field_name]
            
            if attachment.media:
                attachment.media.delete()
            
            media = Media(
                uploaded_by=request.user,
                original_filename=uploaded_file.name,
            )
            media.save()
            media.file.save(uploaded_file.name, uploaded_file, save=True)
            attachment.media = media
            
            if (
                media.media_type == "image"
                and attachment.attachment_type == "other"
            ):
                attachment.attachment_type = "image"
        
        attachment.save()


def _handle_formset_deletions(location_formset, attachment_formset):
    """Helper to handle formset deletions"""
    for location in location_formset.deleted_objects:
        location.delete()
    
    for attachment in attachment_formset.deleted_objects:
        if attachment.media:
            attachment.media.delete()
        attachment.delete()


@vessel_crew_or_skipper_required
def log_entry_create(request, pk):
    vessel = get_object_or_404(Vessel, pk=pk)

    if request.method == "POST":
        form = LogEntryForm(request.POST)
        location_formset = LocationFormSet(request.POST, prefix="locations")
        attachment_formset = AttachmentFormSet(
            request.POST, request.FILES, prefix="attachments"
        )

        if (
            form.is_valid()
            and location_formset.is_valid()
            and attachment_formset.is_valid()
        ):
            log_entry = form.save(commit=False)
            log_entry.vessel = vessel
            log_entry.author = request.user
            log_entry.save()

            locations = location_formset.save(commit=False)
            for location in locations:
                location.log_entry = log_entry
                location.save()

            attachments = attachment_formset.save(commit=False)
            _process_attachment_uploads(request, attachments, log_entry)
            _handle_formset_deletions(location_formset, attachment_formset)

            messages.success(request, "Log entry created successfully!")
            return redirect("vessel_detail", pk=vessel.pk)

        messages.error(request, "Please correct the errors below.")

    if request.method != "POST":
        form = LogEntryForm()
        location_formset = LocationFormSet(prefix="locations")
        attachment_formset = AttachmentFormSet(prefix="attachments")

    context = {
        "form": form,
        "location_formset": location_formset,
        "attachment_formset": attachment_formset,
        "vessel": vessel,
        "is_edit": False,
    }

    return render(request, "webapp/logbook/log_entry_form.html", context)


@vessel_crew_or_skipper_required
def log_entry_edit(request, pk, entry_pk):
    vessel = get_object_or_404(Vessel, pk=pk)
    log_entry = get_object_or_404(LogEntry, pk=entry_pk, vessel=vessel)

    # Check if user can edit this entry
    if not log_entry.can_edit(request.user):
        messages.error(request, "You do not have permission to edit this log entry.")
        return redirect("vessel_detail", pk=vessel.pk)

    if request.method == "POST":
        form = LogEntryForm(request.POST, instance=log_entry)
        location_formset = LocationFormSet(
            request.POST, instance=log_entry, prefix="locations"
        )
        attachment_formset = AttachmentFormSet(
            request.POST, request.FILES, instance=log_entry, prefix="attachments"
        )

        if (
            form.is_valid()
            and location_formset.is_valid()
            and attachment_formset.is_valid()
        ):
            log_entry = form.save()

            locations = location_formset.save(commit=False)
            for location in locations:
                location.log_entry = log_entry
                location.save()

            attachments = attachment_formset.save(commit=False)
            _process_attachment_uploads_edit(request, attachments, log_entry)
            _handle_formset_deletions(location_formset, attachment_formset)

            messages.success(request, "Log entry updated successfully!")
            return redirect("vessel_detail", pk=vessel.pk)

        messages.error(request, "Please correct the errors below.")

    if request.method != "POST":
        form = LogEntryForm(instance=log_entry)
        location_formset = LocationFormSet(instance=log_entry, prefix="locations")
        attachment_formset = AttachmentFormSet(instance=log_entry, prefix="attachments")

    context = {
        "form": form,
        "location_formset": location_formset,
        "attachment_formset": attachment_formset,
        "vessel": vessel,
        "log_entry": log_entry,
        "is_edit": True,
    }

    return render(request, "webapp/logbook/log_entry_form.html", context)


@vessel_crew_or_skipper_required
@require_http_methods(["POST"])
def log_entry_delete(request, pk, entry_pk):
    vessel = get_object_or_404(Vessel, pk=pk)
    log_entry = get_object_or_404(LogEntry, pk=entry_pk, vessel=vessel)

    # Check if user can delete this entry
    if not log_entry.can_edit(request.user):
        messages.error(request, "You do not have permission to delete this log entry.")
        return redirect("vessel_detail", pk=vessel.pk)

    # Delete associated media files
    for attachment in log_entry.attachments.all():
        if attachment.media:
            attachment.media.delete()  # This will also delete the file

    log_entry.delete()
    messages.success(request, "Log entry deleted successfully!")
    return redirect("vessel_detail", pk=vessel.pk)
