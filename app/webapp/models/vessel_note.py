from django.db import models
from django.utils.translation import gettext_lazy as _
from webapp.models.vessel import Vessel
from webapp.models.user import User


class VesselNote(models.Model):
    vessel = models.ForeignKey(
        Vessel,
        on_delete=models.CASCADE,
        related_name="notes",
        help_text=_("The vessel this note is associated with"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_vessel_notes",
        help_text=_("The user who owns this note"),
    )
    shared_with = models.ManyToManyField(
        User,
        related_name="shared_vessel_notes",
        blank=True,
        help_text=_("Users this note is shared with"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("vessel note")
        verbose_name_plural = _("vessel notes")
        unique_together = [["vessel", "user"]]
        indexes = [
            models.Index(fields=["vessel", "user"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Note for {self.vessel} by {self.user}"

    @property
    def owner(self):
        return self.user


class NoteMessage(models.Model):
    vessel_note = models.ForeignKey(
        VesselNote,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text=_("The vessel note this message belongs to"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="note_messages",
        help_text=_("The user who wrote this message"),
    )
    content = models.TextField(help_text=_("The content of the note message"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("note message")
        verbose_name_plural = _("note messages")
        ordering = ["created_at"]

    def __str__(self):
        return f"Message by {self.user} on {self.created_at}"
