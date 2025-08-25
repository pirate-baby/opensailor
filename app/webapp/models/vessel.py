from typing import TYPE_CHECKING
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from guardian.models import UserObjectPermissionBase, GroupObjectPermissionBase
from guardian.shortcuts import assign_perm
from webapp.models.sailboat import Sailboat
from webapp.models.media import Media
from webapp.models.attribute import Attribute
from webapp.models.sailboat_attribute import SailboatAttribute
from webapp.models.moderation import Moderation
from webapp.schemas.attributes import AttributeAssignment


if TYPE_CHECKING:
    from webapp.models.user import User  # noqa: F401
    from django.core.files.uploadedfile import UploadedFile


class VesselAttribute(models.Model):
    vessel = models.ForeignKey("Vessel", on_delete=models.CASCADE)
    attribute = models.ForeignKey("Attribute", on_delete=models.CASCADE)
    value = models.CharField(max_length=255)

    class Meta:
        verbose_name = _("vessel attribute")
        verbose_name_plural = _("vessel attributes")
        unique_together = [["vessel", "attribute"]]
        indexes = [
            models.Index(fields=["vessel", "attribute"]),
        ]

    def __str__(self):
        return f"{self.vessel} - {self.attribute.name}"

    def clean(self):
        super().clean()
        match self.attribute.data_type:
            case Attribute.DataType.FLOAT:
                try:
                    self.value = float(self.value)
                except ValueError as exc:
                    raise ValidationError(
                        {"value": _("Value must be a number")}
                    ) from exc
            case Attribute.DataType.INTEGER:
                try:
                    self.value = int(self.value)
                except ValueError as exc:
                    raise ValidationError(
                        {"value": _("Value must be an integer")}
                    ) from exc
            case _:
                self.value = str(self.value)
        # if the attribute has options, make sure the value is in that list
        if self.attribute.options and self.value not in self.attribute.options:
            raise ValidationError(
                {"value": _("Value must be in the allowed options list")}
            )

        current_sailboat_attribute = SailboatAttribute.objects.filter(
            sailboat=self.sailboat,
            attribute=self.attribute,
        ).first()
        # if the sailboat already has this attribute
        # and the attribute does not accept contributions,
        # then we need to make sure the value is in the list of allowed value
        if not self.attribute.accepts_contributions:
            if (
                current_sailboat_attribute
                and self.value not in current_sailboat_attribute.values
            ):
                raise ValidationError(
                    {"value": _("Value is not allowed for this sailboat")}
                )
        # add the value to the sailboat attribute or create a new one
        if current_sailboat_attribute:
            current_sailboat_attribute.values.append(self.value)
            current_sailboat_attribute.save()
            verb = Moderation.Verb.UPDATE
        else:
            SailboatAttribute.objects.create(
                sailboat=self.sailboat,
                attribute=self.attribute,
                values=[self.value],
            )
            verb = Moderation.Verb.CREATE
        Moderation.objects.create(
            object_id=self.id,
            data={
                "attribute": self.attribute.id,
                "value": self.value,
            },
            verb=verb,
            triggered_by=self,
        )


class VesselImage(models.Model):
    vessel = models.ForeignKey("Vessel", on_delete=models.CASCADE)
    image = models.ForeignKey(Media, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
        unique_together = [["vessel", "order"]]

    def save(self, *args, **kwargs):
        if not self.order:
            # Get the highest order value for this vessel
            highest_order = (
                VesselImage.objects.filter(vessel=self.vessel).aggregate(
                    models.Max("order")
                )["order__max"]
                or 0
            )
            self.order = highest_order + 1
        super().save(*args, **kwargs)


class Vessel(models.Model):
    sailboat = models.ForeignKey(
        Sailboat,
        on_delete=models.CASCADE,
        related_name="vessels",
        help_text=_("The sailboat model this vessel is an instance of"),
    )
    hull_identification_number = models.CharField(
        max_length=14,
        help_text=_("Unique Hull Identification Number (HIN) for this vessel"),
        blank=True,
        null=True,
    )
    USCG_number = models.CharField(
        max_length=14,
        null=True,
        blank=True,
        help_text=_("Number issued by the USCG for this vessel"),
    )
    name = models.CharField(max_length=255, help_text=_("Name of this vessel"))
    year_built = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1800)],
        help_text=_("Year this vessel was built"),
    )
    images = models.ManyToManyField(
        Media,
        through=VesselImage,
        related_name="vessels",
        blank=True,
        limit_choices_to={"media_type": "image"},
        help_text=_("Images of this specific vessel"),
    )
    home_port = models.CharField(
        max_length=255, null=True, blank=True, help_text=_("Home port of this vessel")
    )
    is_public = models.BooleanField(
        default=True,
        help_text=_("Whether this vessel is publicly viewable or private")
    )
    created_by = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="created_vessels",
        help_text=_("User who created this vessel")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("vessel")
        verbose_name_plural = _("vessels")
        permissions = [
            ("can_manage_vessel", "Can manage vessel and assign roles"),
            ("can_crew_vessel", "Can add logs and view detailed vessel info"),
            ("can_view_vessel", "Can view private vessel details"),
        ]
        indexes = [
            models.Index(fields=["hull_identification_number"]),
            models.Index(fields=["year_built"]),
            models.Index(fields=["is_public"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self):
        return f"{self.sailboat} - {self.hull_identification_number}"

    @property
    def images_queryset(self):
        """Get the queryset of vessel images ordered by the 'order' field"""
        return (
            self.images.through.objects.filter(vessel=self)
            .order_by("order")
            .select_related("image")
        )

    @property
    def images_all(self):
        """Get all images ordered by the 'order' field"""
        return [vessel_image.image for vessel_image in self.images_queryset]

    @property
    def first_image(self):
        """Get the first image, if it exists"""
        image_relation = (
            self.images.through.objects.filter(vessel=self).order_by("order").first()
        )
        return image_relation.image if image_relation else None

    @property
    def has_images(self):
        """Check if the vessel has any images"""
        return self.images.exists()

    def add_image(self, image: "UploadedFile"):
        """add an image to the vessel"""
        media = Media.objects.create(file=image)
        VesselImage.objects.create(
            vessel=self, image=media, order=self.images.count() + 1
        )
        self.save()

    def create_or_update_attribute(
        self, attribute_assignment: AttributeAssignment
    ) -> VesselAttribute:
        """create or update an attribute for the vessel, and create a moderation request
        for the parent sailboat if the data is new"""
        attribute = Attribute.objects.get(name=attribute_assignment.name)
        if existing_attribute := VesselAttribute.objects.filter(
            vessel=self,
            attribute=attribute,
        ).first():
            existing_attribute.value = attribute_assignment.value
            existing_attribute.save()
            return existing_attribute
        return VesselAttribute.objects.create(
            vessel=self, attribute=attribute, value=attribute_assignment.value
        )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Assign permissions to creator for new vessels
        if is_new and self.created_by:
            assign_perm("can_manage_vessel", self.created_by, self)
            assign_perm("can_crew_vessel", self.created_by, self)
            assign_perm("can_view_vessel", self.created_by, self)


class VesselUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey("Vessel", on_delete=models.CASCADE)


class VesselGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey("Vessel", on_delete=models.CASCADE)
