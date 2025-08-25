from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from guardian.shortcuts import get_objects_for_user

from webapp.models.sailboat import Sailboat


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "user", _("User")
        MODERATOR = "moderator", _("Moderator")
        ADMIN = "admin", _("Admin")

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        help_text=_("User role that determines access level"),
    )

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        permissions = [
            ("can_manage_sailboats", "Can manage sailboats"),
            ("can_view_sailboats", "Can view sailboats"),
            ("can_manage_vessels", "Can manage vessels"),
            ("can_crew_vessels", "Can crew vessels"), 
            ("can_view_vessels", "Can view vessels"),
        ]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_moderator(self):
        return self.role in [self.Role.MODERATOR, self.Role.ADMIN]

    @property
    def is_regular_user(self):
        return self.role == self.Role.USER

    def has_admin_access(self):
        """Check if user has admin access"""
        return self.is_admin

    def has_moderator_access(self):
        """Check if user has moderator access"""
        return self.is_moderator

    def has_user_access(self):
        """Check if user has basic user access"""
        return True  # All authenticated users have basic access

    def get_manageable_sailboats(self):
        """Get all sailboats that the user can manage"""
        if self.is_admin:
            return Sailboat.objects.all()
        return get_objects_for_user(self, "webapp.can_manage_sailboats", Sailboat)

    def get_viewable_sailboats(self):
        """Get all sailboats that the user can view"""
        if self.is_admin or self.is_moderator:
            return Sailboat.objects.all()
        return get_objects_for_user(self, "webapp.can_view_sailboats", Sailboat)

    def get_manageable_vessels(self):
        """Get all vessels that the user can manage (skipper role)"""
        from webapp.models.vessel import Vessel  # Import here to avoid circular imports
        if self.is_admin:
            return Vessel.objects.all()
        return get_objects_for_user(self, "webapp.can_manage_vessel", Vessel)

    def get_crewable_vessels(self):
        """Get all vessels that the user can crew (crew or skipper role)"""
        from webapp.models.vessel import Vessel
        if self.is_admin:
            return Vessel.objects.all()
        return get_objects_for_user(self, ["webapp.can_crew_vessel", "webapp.can_manage_vessel"], Vessel)

    def get_viewable_vessels(self):
        """Get all vessels that the user can view (any role + public vessels)"""
        from webapp.models.vessel import Vessel
        if self.is_admin or self.is_moderator:
            return Vessel.objects.all()
        
        # Get private vessels user has access to
        private_vessels = get_objects_for_user(
            self, ["webapp.can_view_vessel", "webapp.can_crew_vessel", "webapp.can_manage_vessel"], Vessel
        ).filter(is_public=False)
        
        # Combine with public vessels
        public_vessels = Vessel.objects.filter(is_public=True)
        
        return private_vessels.union(public_vessels)

    def can_manage_vessel(self, vessel):
        """Check if user can manage a specific vessel (skipper role)"""
        if self.is_admin:
            return True
        return self.has_perm("webapp.can_manage_vessel", vessel)

    def can_crew_vessel(self, vessel):
        """Check if user can crew a specific vessel (crew or skipper role)"""
        if self.is_admin:
            return True
        return (self.has_perm("webapp.can_crew_vessel", vessel) or 
                self.has_perm("webapp.can_manage_vessel", vessel))

    def can_view_vessel(self, vessel):
        """Check if user can view a specific vessel (any role or public)"""
        if self.is_admin or self.is_moderator:
            return True
        if vessel.is_public:
            return True
        return (self.has_perm("webapp.can_view_vessel", vessel) or
                self.has_perm("webapp.can_crew_vessel", vessel) or
                self.has_perm("webapp.can_manage_vessel", vessel))

    def assign_role_permissions(self):
        """Assign appropriate permissions based on user role"""
        from webapp.models.vessel import Vessel

        # Get content types
        sailboat_ct = ContentType.objects.get_for_model(Sailboat)
        vessel_ct = ContentType.objects.get_for_model(Vessel)

        # Get sailboat permissions
        manage_sailboat_perm = Permission.objects.get(
            content_type=sailboat_ct, codename="can_manage_sailboats"
        )
        view_sailboat_perm = Permission.objects.get(
            content_type=sailboat_ct, codename="can_view_sailboats"
        )

        # Get vessel permissions
        manage_vessel_perm = Permission.objects.get(
            content_type=vessel_ct, codename="can_manage_vessels"
        )
        crew_vessel_perm = Permission.objects.get(
            content_type=vessel_ct, codename="can_crew_vessels"
        )
        view_vessel_perm = Permission.objects.get(
            content_type=vessel_ct, codename="can_view_vessels"
        )

        # Remove all permissions first
        self.user_permissions.remove(
            manage_sailboat_perm, view_sailboat_perm,
            manage_vessel_perm, crew_vessel_perm, view_vessel_perm
        )

        # Assign permissions based on role
        if self.is_admin:
            self.user_permissions.add(
                manage_sailboat_perm, view_sailboat_perm,
                manage_vessel_perm, crew_vessel_perm, view_vessel_perm
            )
        elif self.is_moderator:
            self.user_permissions.add(
                manage_sailboat_perm, view_sailboat_perm,
                manage_vessel_perm, crew_vessel_perm, view_vessel_perm
            )
        else:
            self.user_permissions.add(view_sailboat_perm, view_vessel_perm)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.assign_role_permissions()
