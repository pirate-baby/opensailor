from typing import TYPE_CHECKING, Type
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

if TYPE_CHECKING:
    from webapp.models.user import User  # noqa: F401


class Moderation(models.Model):
    class State(models.TextChoices):
        UNMODERATED = "unmoderated", _("Unmoderated")
        APPROVED = "approved", _("Approved")
        DECLINED = "declined", _("Declined")
        MODIFIED = "modified", _("Modified")

    class Verb(models.TextChoices):
        CREATE = "create", _("Create")
        UPDATE = "update", _("Update")
        DELETE = "delete", _("Delete")

    # Content type and object id for the generic foreign key
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text=_("The type of model being moderated"),
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_(
            "The primary key of the existing object being moderated (if updating)"
        ),
    )
    content_object = GenericForeignKey("content_type", "object_id")

    # Data to be applied
    data = models.JSONField(
        help_text=_("The JSON data of the proposed changes or new object")
    )

    # User who requested the change
    requested_by = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="requested_moderations",
        help_text=_("The user who requested this moderation"),
    )

    # Object that triggered this moderation as a side effect (generic)
    triggered_by_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_moderations",
        help_text=_(
            "The type of object that triggered this moderation as a side effect"
        ),
    )
    triggered_by_object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("The primary key of the object that triggered this moderation"),
    )
    triggered_by = GenericForeignKey(
        "triggered_by_content_type", "triggered_by_object_id"
    )

    # Optional note from the requester
    request_note = models.TextField(
        blank=True,
        null=True,
        help_text=_("Optional note explaining the suggested change"),
    )

    # Moderator who handled this moderation (if any)
    moderator = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        related_name="handled_moderations",
        null=True,
        blank=True,
        help_text=_("The moderator who handled this moderation (if assigned)"),
    )

    # State of the moderation
    state = models.CharField(
        max_length=20,
        choices=State.choices,
        default=State.UNMODERATED,
        help_text=_("The current state of this moderation"),
    )

    # Verb of the moderation
    verb = models.CharField(
        max_length=20,
        choices=Verb.choices,
        default=Verb.CREATE,
        help_text=_("What type of action is being moderation"),
    )
    # Optional response note from the moderator
    response_note = models.TextField(
        blank=True,
        null=True,
        help_text=_("Optional response note from the moderator"),
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("moderation")
        verbose_name_plural = _("moderations")
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["state"]),
            models.Index(fields=["requested_by"]),
            models.Index(fields=["moderator"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        model_name = self.content_type.model
        if self.object_id:
            return f"Moderation for {model_name} #{self.object_id} - {self.state}"
        return f"Moderation for new {model_name} - {self.state}"

    @property
    def is_pending(self):
        return self.state == self.State.UNMODERATED

    @property
    def is_approved(self):
        return self.state == self.State.APPROVED

    @property
    def is_declined(self):
        return self.state == self.State.DECLINED

    @property
    def is_modified(self):
        return self.state == self.State.MODIFIED

    @classmethod
    def moderation_for(cls, class_: Type[models.Model], **kwargs):
        content_type = ContentType.objects.get_for_model(class_)
        return Moderation.objects.create(content_type=content_type, **kwargs)
