from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from webapp.models.sailboat import Sailboat
from webapp.models.media import Media

class VesselImage(models.Model):
    vessel = models.ForeignKey('Vessel', on_delete=models.CASCADE)
    image = models.ForeignKey(Media, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        unique_together = [['vessel', 'order']]

    def save(self, *args, **kwargs):
        if not self.order:
            # Get the highest order value for this vessel
            highest_order = VesselImage.objects.filter(vessel=self.vessel).aggregate(
                models.Max('order'))['order__max'] or 0
            self.order = highest_order + 1
        super().save(*args, **kwargs)

class Vessel(models.Model):
    sailboat = models.ForeignKey(
        Sailboat,
        on_delete=models.CASCADE,
        related_name='vessels',
        help_text=_('The sailboat model this vessel is an instance of')
    )
    hull_identification_number = models.CharField(
        max_length=14,
        unique=True,
        help_text=_('Unique Hull Identification Number (HIN) for this vessel')
    )
    name = models.CharField(
        max_length=255,
        help_text=_('Name of this vessel')
    )
    year_built = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1800)],
        help_text=_('Year this vessel was built')
    )
    images = models.ManyToManyField(
        Media,
        through=VesselImage,
        related_name='vessels',
        blank=True,
        limit_choices_to={'media_type': 'image'},
        help_text=_('Images of this specific vessel')
    )
    home_port = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_('Home port of this vessel')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('vessel')
        verbose_name_plural = _('vessels')
        indexes = [
            models.Index(fields=['hull_identification_number']),
            models.Index(fields=['year_built']),
        ]

    def __str__(self):
        return f"{self.sailboat} - {self.hull_identification_number}"

    def clean(self):
        super().clean()
        # Validate that year_built is within the sailboat's manufacturing years
        if (self.sailboat.manufactured_start_year and
            self.year_built < self.sailboat.manufactured_start_year):
            raise ValidationError({
                'year_built': _('Year built cannot be before the sailboat model\'s manufacturing start year')
            })
        if (self.sailboat.manufactured_end_year and
            self.year_built > self.sailboat.manufactured_end_year):
            raise ValidationError({
                'year_built': _('Year built cannot be after the sailboat model\'s manufacturing end year')
            })

    @property
    def images_queryset(self):
        """Get the queryset of vessel images ordered by the 'order' field"""
        return self.images.through.objects.filter(vessel=self).order_by('order').select_related('image')

    @property
    def images_all(self):
        """Get all images ordered by the 'order' field"""
        return [vessel_image.image for vessel_image in self.images_queryset]

    @property
    def first_image(self):
        """Get the first image, if it exists"""
        image_relation = self.images.through.objects.filter(vessel=self).order_by('order').first()
        return image_relation.image if image_relation else None

    @property
    def has_images(self):
        """Check if the vessel has any images"""
        return self.images.exists()