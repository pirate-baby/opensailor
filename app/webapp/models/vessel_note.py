from django.db import models
from django.utils.translation import gettext_lazy as _
from webapp.models.vessel import Vessel
from webapp.models.user import User

class VesselNote(models.Model):
    vessel = models.ForeignKey(
        Vessel,
        on_delete=models.CASCADE,
        related_name='notes',
        help_text=_('The vessel this note is associated with')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vessel_notes',
        help_text=_('The user who created this note')
    )
    content = models.TextField(
        help_text=_('The markdown content of the note')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('vessel note')
        verbose_name_plural = _('vessel notes')
        unique_together = [['vessel', 'user']]
        indexes = [
            models.Index(fields=['vessel', 'user']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Note for {self.vessel} by {self.user}"