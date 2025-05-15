from django.db import models
import re
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class Attribute(models.Model):
    class InputType(models.TextChoices):
        STRING = 'string', _('String')
        FLOAT = 'float', _('Float')
        OPTIONS = 'options', _('Options')
        INTEGER = 'integer', _('Integer')
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

    @property
    def snake_case_name(self):
        return re.sub(r'(?<!^\s)(?=[A-Z])', '_', self.name).lower()

    def get_form_field_name(self, prefix="attr_"):
        """
        Returns the name of the form field for this attribute,
        with the given prefix (default: 'attr_')
        """
        return f"{prefix}{self.snake_case_name}"

    def is_in_form_data(self, form_data, prefix="attr_"):
        """
        Checks if this attribute exists in the form data.
        Handles both regular input names and array-style input names (with []).

        Args:
            form_data: The request POST or GET data
            prefix: Prefix used for the attribute name in the form (default: 'attr_')

        Returns:
            bool: True if the attribute is in the form data, False otherwise
        """
        field_name = self.get_form_field_name(prefix)
        array_field_name = f"{field_name}[]"

        # Check for direct match
        if field_name in form_data:
            return True

        # Check for array-style fields
        for key in form_data.keys():
            if key.startswith(array_field_name.replace('[]', '[')):
                return True

        return False

    def get_values_from_form_data(self, form_data, prefix="attr_"):
        """
        Extracts all values for this attribute from the form data.
        Handles both regular input names and array-style input names.

        Args:
            form_data: The request POST or GET data
            prefix: Prefix used for the attribute name in the form (default: 'attr_')

        Returns:
            list: List of values for this attribute
        """
        field_name = self.get_form_field_name(prefix)
        array_field_name = f"{field_name}[]"

        if field_name in form_data:
            values = form_data.getlist(field_name)
        else:
            # For array-style inputs, collect all values with matching prefix
            values = []
            for key in form_data.keys():
                if key.startswith(array_field_name.replace('[]', '[')):
                    values.extend(form_data.getlist(key))

        # Filter out empty values
        return [v for v in values if v]

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
