from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from webapp.models.attribute import Attribute


class SailboatAttribute(models.Model):
    sailboat = models.ForeignKey(
        "Sailboat", on_delete=models.CASCADE, related_name="attribute_values"
    )
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="sailboat_values"
    )
    values = models.JSONField(help_text=_("List of values for this attribute"))

    class Meta:
        verbose_name = _("sailboat attribute")
        verbose_name_plural = _("sailboat attributes")
        unique_together = [["sailboat", "attribute"]]
        indexes = [
            models.Index(fields=["sailboat", "attribute"]),
        ]

    def __str__(self):
        return f"{self.sailboat} - {self.attribute.name}"

    def clean(self):
        super().clean()
        if not isinstance(self.values, list):
            raise ValidationError({"values": _("Values must be a list")})

        # Validate values based on attribute type
        if self.attribute.input_type == Attribute.InputType.FLOAT:
            if not all(isinstance(v, (int, float)) for v in self.values):
                raise ValidationError(
                    {
                        "values": _(
                            "All values must be numbers for FLOAT type attributes"
                        )
                    }
                )
        elif self.attribute.input_type == Attribute.InputType.OPTIONS:
            if not all(v in self.attribute.options for v in self.values):
                raise ValidationError(
                    {"values": _("All values must be in the allowed options list")}
                )
