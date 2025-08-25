from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone
from guardian.shortcuts import assign_perm


User = get_user_model()


class VesselAccessRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        APPROVED = "approved", _("Approved")
        DENIED = "denied", _("Denied")

    class Role(models.TextChoices):
        VIEWER = "viewer", _("Viewer")
        CREW = "crew", _("Crew")
        SKIPPER = "skipper", _("Skipper")

    vessel = models.ForeignKey(
        "Vessel",
        on_delete=models.CASCADE,
        related_name="access_requests",
        help_text=_("The vessel being requested access to")
    )
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vessel_access_requests",
        help_text=_("User requesting access")
    )
    requested_role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text=_("Role being requested")
    )
    message = models.TextField(
        blank=True,
        help_text=_("Optional message from requester explaining why they need access")
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        help_text=_("Current status of the request")
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_vessel_access_requests",
        help_text=_("User who reviewed this request")
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When this request was reviewed")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("vessel access request")
        verbose_name_plural = _("vessel access requests")
        unique_together = [["vessel", "requester"]]  # One active request per user per vessel
        indexes = [
            models.Index(fields=["vessel", "status"]),
            models.Index(fields=["requester", "status"]),
        ]

    def __str__(self):
        return f"{self.requester.username} -> {self.vessel.name} ({self.requested_role})"

    def approve(self, reviewer):
        """Approve the request and assign permissions"""
        self.status = self.Status.APPROVED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()
        
        # Assign the appropriate permissions
        if self.requested_role == self.Role.VIEWER:
            assign_perm("webapp.can_view_vessel", self.requester, self.vessel)
        elif self.requested_role == self.Role.CREW:
            assign_perm("webapp.can_view_vessel", self.requester, self.vessel)
            assign_perm("webapp.can_crew_vessel", self.requester, self.vessel)
        elif self.requested_role == self.Role.SKIPPER:
            assign_perm("webapp.can_view_vessel", self.requester, self.vessel)
            assign_perm("webapp.can_crew_vessel", self.requester, self.vessel)
            assign_perm("webapp.can_manage_vessel", self.requester, self.vessel)

    def deny(self, reviewer):
        """Deny the request"""
        self.status = self.Status.DENIED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()