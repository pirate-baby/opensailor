from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from .vessel import Vessel
from .media import Media

User = get_user_model()


class LogEntry(models.Model):
    vessel = models.ForeignKey(
        Vessel,
        on_delete=models.CASCADE,
        related_name="log_entries",
        help_text=_("The vessel this log entry belongs to"),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="log_entries",
        help_text=_("The user who created this log entry"),
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Optional short title for the log entry"),
    )
    content = models.TextField(help_text=_("Log entry content in markdown format"))
    log_timestamp = models.DateTimeField(
        help_text=_("When this log event occurred (not when it was recorded)")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Log Entry")
        verbose_name_plural = _("Log Entries")
        ordering = ["-log_timestamp"]
        indexes = [
            models.Index(fields=["vessel", "-log_timestamp"]),
            models.Index(fields=["author", "-log_timestamp"]),
        ]

    def __str__(self):
        if self.title:
            return f"{self.vessel.name} - {self.title}"
        return f"{self.vessel.name} - {self.log_timestamp.strftime('%Y-%m-%d %H:%M')}"

    def can_edit(self, user):
        """Check if user can edit this log entry"""
        if user == self.author:
            return True
        return user.has_perm("can_manage_vessel", self.vessel)

    def can_view(self, user):
        """Check if user can view this log entry"""
        return user.has_perm("can_view_vessel", self.vessel)


class LogEntryLocation(models.Model):
    LOCATION_TYPE_CHOICES = [
        ("waypoint", _("Waypoint")),
        ("start", _("Start Point")),
        ("end", _("End Point")),
        ("anchorage", _("Anchorage")),
        ("marina", _("Marina")),
        ("fuel", _("Fuel Stop")),
        ("emergency", _("Emergency")),
        ("other", _("Other")),
    ]

    log_entry = models.ForeignKey(
        LogEntry,
        on_delete=models.CASCADE,
        related_name="locations",
        help_text=_("The log entry this location belongs to"),
    )
    name = models.CharField(
        max_length=200, blank=True, help_text=_("Optional name for this location")
    )
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text=_("Latitude in decimal degrees"),
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=7,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text=_("Longitude in decimal degrees"),
    )
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPE_CHOICES,
        default="waypoint",
        help_text=_("Type of location"),
    )
    order = models.PositiveIntegerField(
        default=0, help_text=_("Order of this location in the route (0-based)")
    )

    # Additional location metadata
    speed_knots = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_("Speed in knots at this location"),
    )
    heading_degrees = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(359)],
        help_text=_("Compass heading in degrees (0-359)"),
    )
    depth_feet = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_("Water depth in feet"),
    )
    wind_speed_knots = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_("Wind speed in knots"),
    )
    wind_direction_degrees = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(359)],
        help_text=_("Wind direction in degrees (0-359)"),
    )
    temperature_f = models.IntegerField(
        null=True, blank=True, help_text=_("Temperature in Fahrenheit")
    )
    barometric_pressure = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(25), MaxValueValidator(35)],
        help_text=_("Barometric pressure in inches of mercury"),
    )
    sea_state = models.CharField(
        max_length=100, blank=True, help_text=_("Description of sea conditions")
    )
    visibility_miles = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_("Visibility in nautical miles"),
    )

    timestamp = models.DateTimeField(
        null=True, blank=True, help_text=_("Timestamp when location was recorded")
    )

    class Meta:
        verbose_name = _("Log Entry Location")
        verbose_name_plural = _("Log Entry Locations")
        ordering = ["order", "timestamp"]
        indexes = [
            models.Index(fields=["log_entry", "order"]),
            models.Index(fields=["latitude", "longitude"]),
        ]

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.latitude}, {self.longitude})"
        return f"{self.latitude}, {self.longitude}"


class LogEntryAttachment(models.Model):
    ATTACHMENT_TYPE_CHOICES = [
        ("image", _("Image")),
        ("receipt", _("Receipt")),
        ("manual", _("Manual")),
        ("document", _("Document")),
        ("video", _("Video")),
        ("audio", _("Audio")),
        ("other", _("Other")),
    ]

    log_entry = models.ForeignKey(
        LogEntry,
        on_delete=models.CASCADE,
        related_name="attachments",
        help_text=_("The log entry this attachment belongs to"),
    )
    media = models.ForeignKey(
        Media,
        on_delete=models.CASCADE,
        help_text=_("The media file for this attachment"),
    )
    attachment_type = models.CharField(
        max_length=20,
        choices=ATTACHMENT_TYPE_CHOICES,
        help_text=_("Type of attachment"),
    )
    description = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("Optional description of the attachment"),
    )
    order = models.PositiveIntegerField(
        default=0, help_text=_("Display order of attachments")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Log Entry Attachment")
        verbose_name_plural = _("Log Entry Attachments")
        ordering = ["order", "created_at"]
        indexes = [
            models.Index(fields=["log_entry", "order"]),
            models.Index(fields=["attachment_type"]),
        ]

    def __str__(self):
        return f"{self.log_entry} - {self.media.original_filename}"

    @property
    def is_image(self):
        """Returns True if this attachment is an image"""
        return self.attachment_type == "image" or self.media.media_type == "image"

    def can_view(self, user):
        """Check if user can view this attachment"""
        return self.log_entry.can_view(user)
