from django.db import models
from django.utils.translation import gettext_lazy as _

class Designer(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Name of the boat designer')
    )

    class Meta:
        verbose_name = _('designer')
        verbose_name_plural = _('designers')
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Convert name to lowercase for case-insensitive uniqueness
        self.name = self.name.lower()
        super().save(*args, **kwargs)