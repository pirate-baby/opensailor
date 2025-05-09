from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class Attribute(models.Model):
    class InputType(models.TextChoices):
        STRING = 'string', _('String')
        FLOAT = 'float', _('Float')
        OPTIONS = 'options', _('Options')

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Name of the attribute')
    )
    description = models.TextField(
        help_text=_('Description of what this attribute represents')
    )
    input_type = models.CharField(
        max_length=20,
        choices=InputType.choices,
        help_text=_('Type of input for this attribute')
    )
    options = models.JSONField(
        null=True,
        blank=True,
        help_text=_('List of allowed options for OPTIONS type attributes')
    )

    class Meta:
        verbose_name = _('attribute')
        verbose_name_plural = _('attributes')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['input_type']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Convert name to lowercase for case-insensitive uniqueness
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.input_type == self.InputType.OPTIONS and not self.options:
            raise ValidationError({
                'options': _('Options are required for OPTIONS type attributes')
            })