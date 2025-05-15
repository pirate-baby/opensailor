from typing import List
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from guardian.models import UserObjectPermissionBase
from guardian.models import GroupObjectPermissionBase
from webapp.models.make import Make
from webapp.models.designer import Designer
from webapp.models.sailboat_attribute import SailboatAttribute
from webapp.models.media import Media

class SailboatImage(models.Model):
    sailboat = models.ForeignKey('Sailboat', on_delete=models.CASCADE)
    image = models.ForeignKey(Media, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        unique_together = [['sailboat', 'order']]

    def save(self, *args, **kwargs):
        if not self.order:
            # Get the highest order value for this sailboat
            highest_order = SailboatImage.objects.filter(sailboat=self.sailboat).aggregate(
                models.Max('order'))['order__max'] or 0
            self.order = highest_order + 1
        super().save(*args, **kwargs)

class SailboatUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey('Sailboat', on_delete=models.CASCADE)

class SailboatGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey('Sailboat', on_delete=models.CASCADE)

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
    images = models.ManyToManyField(
        Media,
        through=SailboatImage,
        related_name='sailboats',
        blank=True,
        limit_choices_to={'media_type': 'image'},
        help_text=_('Images of the sailboat')
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
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sailboats',
        help_text=_('User who created this sailboat')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('sailboat')
        verbose_name_plural = _('sailboats')
        unique_together = [['make', 'name']]
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]
        permissions = [
            ('can_manage_sailboats', 'Can manage sailboats'),
            ('can_view_sailboats', 'Can view sailboats'),
        ]

    def __str__(self):
        return f"{self.make.name} {self.name}"

    def save(self, *args, **kwargs):
        # Convert name to lowercase for case-insensitive uniqueness
        self.name = self.name.lower()
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.created_by:
            # Assign object-level permissions to creator
            from guardian.shortcuts import assign_perm
            assign_perm('can_manage_sailboats', self.created_by, self)
            assign_perm('can_view_sailboats', self.created_by, self)

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
