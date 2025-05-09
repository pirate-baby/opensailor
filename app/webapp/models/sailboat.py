from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from webapp.models.make import Make
from webapp.models.designer import Designer
from webapp.models.attribute import Attribute

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

    def __getattr__(self, name):
        """Handle dynamic attribute access"""
        try:
            attr = Attribute.objects.get(name=name.lower())
        except Attribute.DoesNotExist:
            raise AttributeError(f"Sailboat has no attribute '{name}'")

        # Get all values for this attribute
        values = self.attribute_values.filter(attribute=attr).values_list('values', flat=True)
        if not values:
            return None
        # Flatten the list of lists into a single list
        return [v for sublist in values for v in sublist]

    def __setattr__(self, name, value):
        """Handle dynamic attribute assignment"""
        if name in self._meta.get_fields():
            super().__setattr__(name, value)
            return

        if not self.pk:
            super().__setattr__(name, value)
            return

        try:
            attr = Attribute.objects.get(name=name.lower())
        except Attribute.DoesNotExist:
            raise AttributeError(f"Cannot set attribute '{name}' - it does not exist")

        # Delete existing values
        self.attribute_values.filter(attribute=attr).delete()

        # Create new values
        if value is not None:
            self.attribute_values.create(attribute=attr, values=value)

    @classmethod
    def get_filtered_queryset(cls, filters=None, order_by=None):
        """
        Get a filtered and ordered queryset of sailboats.

        Args:
            filters (dict): Dictionary of filter parameters
            order_by (str): Field to order by, prefixed with '-' for descending order

        Returns:
            QuerySet: Filtered and ordered queryset of sailboats
        """
        queryset = cls.objects.all()

        if filters:
            # Handle basic model fields
            if 'name' in filters:
                queryset = queryset.filter(name__icontains=filters['name'].lower())
            if 'make' in filters:
                queryset = queryset.filter(make__name__icontains=filters['make'].lower())
            if 'designer' in filters:
                queryset = queryset.filter(designers__name__icontains=filters['designer'].lower())
            if 'year_start' in filters:
                queryset = queryset.filter(manufactured_start_year__gte=filters['year_start'])
            if 'year_end' in filters:
                queryset = queryset.filter(manufactured_end_year__lte=filters['year_end'])

            # Handle dynamic attributes
            for key, value in filters.items():
                if key.startswith('attr_'):
                    attr_name = key[5:]  # Remove 'attr_' prefix
                    try:
                        attr = Attribute.objects.get(name=attr_name.lower())
                        if isinstance(value, list):
                            # For multiple values, we want boats that have ANY of the selected values
                            queryset = queryset.filter(
                                attribute_values__attribute=attr,
                                attribute_values__values__overlap=value
                            )
                        else:
                            queryset = queryset.filter(
                                attribute_values__attribute=attr,
                                attribute_values__values__contains=[value]
                            )
                    except Attribute.DoesNotExist:
                        continue

        # Apply ordering
        if order_by:
            if order_by.startswith('-'):
                field = order_by[1:]
                if field.startswith('attr_'):
                    attr_name = field[5:]
                    try:
                        attr = Attribute.objects.get(name=attr_name.lower())
                        queryset = queryset.order_by(f'-attribute_values__values__0')
                    except Attribute.DoesNotExist:
                        pass
                else:
                    queryset = queryset.order_by(order_by)
            else:
                if order_by.startswith('attr_'):
                    attr_name = order_by[5:]
                    try:
                        attr = Attribute.objects.get(name=attr_name.lower())
                        queryset = queryset.order_by('attribute_values__values__0')
                    except Attribute.DoesNotExist:
                        pass
                else:
                    queryset = queryset.order_by(order_by)

        return queryset.distinct()