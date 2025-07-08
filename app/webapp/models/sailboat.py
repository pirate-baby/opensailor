from typing import List, TYPE_CHECKING
from guardian.shortcuts import assign_perm
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from guardian.models import UserObjectPermissionBase
from guardian.models import GroupObjectPermissionBase
from webapp.models.make import Make
from webapp.models.designer import Designer
from webapp.models.sailboat_attribute import SailboatAttribute
from webapp.models.media import Media
from webapp.models.moderation import Moderation

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class SailboatImage(models.Model):
    sailboat = models.ForeignKey("Sailboat", on_delete=models.CASCADE)
    image = models.ForeignKey(Media, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
        unique_together = [["sailboat", "order"]]

    def save(self, *args, **kwargs):
        if not self.order:
            # Get the highest order value for this sailboat
            highest_order = (
                SailboatImage.objects.filter(sailboat=self.sailboat).aggregate(
                    models.Max("order")
                )["order__max"]
                or 0
            )
            self.order = highest_order + 1
        super().save(*args, **kwargs)


class SailboatUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey("Sailboat", on_delete=models.CASCADE)


class SailboatGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey("Sailboat", on_delete=models.CASCADE)


class Sailboat(models.Model):
    name = models.CharField(max_length=100, help_text=_("Name of the sailboat model"))
    make = models.ForeignKey(
        Make,
        on_delete=models.CASCADE,
        related_name="sailboats",
        help_text=_("Manufacturer of the sailboat"),
    )
    designers = models.ManyToManyField(
        Designer,
        related_name="sailboats",
        blank=True,
        help_text=_("Designers of the sailboat"),
    )
    images = models.ManyToManyField(
        Media,
        through=SailboatImage,
        related_name="sailboats",
        blank=True,
        limit_choices_to={"media_type": "image"},
        help_text=_("Images of the sailboat"),
    )
    manufactured_start_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1800)],
        help_text=_("Year when production of this model started"),
    )
    manufactured_end_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1800)],
        help_text=_("Year when production of this model ended"),
    )
    created_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_sailboats",
        help_text=_("User who created this sailboat"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("sailboat")
        verbose_name_plural = _("sailboats")
        unique_together = [["make", "name"]]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]
        permissions = [
            ("can_manage_sailboats", "Can manage sailboats"),
            ("can_view_sailboats", "Can view sailboats"),
        ]

    def __str__(self):
        return f"{self.make.name} {self.name}"

    def add_year_built(self, year_built: int) -> bool:
        """add/adjust based on a new year built, returns True if changes we made"""
        if (
            not self.manufactured_start_year
            or year_built < self.manufactured_start_year
        ):
            self.manufactured_start_year = year_built
            self.save()
            return True
        if not self.manufactured_end_year or year_built > self.manufactured_end_year:
            self.manufactured_end_year = year_built
            self.save()
            return True
        return False

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.created_by:
            assign_perm("can_manage_sailboats", self.created_by, self)
            assign_perm("can_view_sailboats", self.created_by, self)

    @property
    def attributes(self):
        class AttributeProxy:
            def __init__(self, attributes: List[SailboatAttribute]):
                for attribute in attributes:
                    self.__dict__[attribute.name] = attribute

        return AttributeProxy(self.attribute_values.all())

    @classmethod
    def get_or_create_moderated(
        cls, make: Make, name: str, year_built: int, user: "User"
    ):
        """get or create a sailboat, moderating it if it's new"""
        sailboat, created = cls.objects.get_or_create(make=make, name=name)
        if created:
            Moderation.moderation_for(
                cls,
                object_id=sailboat.id,
                requested_by=user,
                request_note="This sailboat was created to support a new vessel",
                verb=Moderation.Verb.CREATE,
                data={
                    "name": name,
                },
            )
        if sailboat.add_year_built(year_built):
            Moderation.moderation_for(
                cls,
                object_id=sailboat.id,
                requested_by=user,
                request_note=f"{year_built} was added as the year built range for this model",
                verb=Moderation.Verb.UPDATE,
                data={
                    "year_built": year_built,
                },
            )

        return sailboat
