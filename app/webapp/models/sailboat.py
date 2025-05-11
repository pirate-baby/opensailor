from typing import List
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from webapp.models.make import Make
from webapp.models.designer import Designer
from webapp.models.sailboat_attribute import SailboatAttribute
from webapp.models.media import Media

class Sailboat(models.Model):
    name = models.CharField(
        max_length=100,
        help_text=_('Name of the sailboat model')
    )
    make = models.ForeignKey(
        Make,
        on_delete=models.CASCADE,
        related_name='sailboats',
        help_text=_('Manufacturer of the sailboat')
    )
    designers = models.ManyToManyField(
        Designer,
        related_name='sailboats',
        blank=True,
        help_text=_('Designers of the sailboat')
    )
    photos = models.ManyToManyField(
        Media,
        related_name='sailboats',
        blank=True,
        limit_choices_to={'media_type': 'image'},
        help_text=_('Photos of the sailboat')
    )
    manufactured_start_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1800)],
        help_text=_('Year when production of this model started')
    )
    manufactured_end_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1800)],
        help_text=_('Year when production of this model ended')
    )

    class Meta:
        verbose_name = _('sailboat')
        verbose_name_plural = _('sailboats')
        unique_together = [['make', 'name']]
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.make.name} {self.name}"

    def save(self, *args, **kwargs):
        # Convert name to lowercase for case-insensitive uniqueness
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        # Validate that end year is not before start year if both are provided
        if (self.manufactured_start_year and self.manufactured_end_year and
            self.manufactured_end_year < self.manufactured_start_year):
            raise ValidationError({
                'manufactured_end_year': _('End year cannot be before start year')
            })

    @property
    def attributes(self):

        class AttributeProxy:
                def __init__(self, attributes: List[SailboatAttribute]):
                    for attribute in attributes:
                        self.__dict__[attribute.name] = attribute

        return AttributeProxy(self.attribute_values.all())
