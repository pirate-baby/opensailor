from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from guardian.shortcuts import get_objects_for_user

class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', _('User')
        MODERATOR = 'moderator', _('Moderator')
        ADMIN = 'admin', _('Admin')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        help_text=_('User role that determines access level')
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        permissions = [
            ('can_manage_sailboats', 'Can manage sailboats'),
            ('can_view_sailboats', 'Can view sailboats'),
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
        from webapp.models.sailboat import Sailboat
        if self.is_admin:
            return Sailboat.objects.all()
        return get_objects_for_user(self, 'webapp.can_manage_sailboats', Sailboat)

    def get_viewable_sailboats(self):
        """Get all sailboats that the user can view"""
        from webapp.models.sailboat import Sailboat
        if self.is_admin or self.is_moderator:
            return Sailboat.objects.all()
        return get_objects_for_user(self, 'webapp.can_view_sailboats', Sailboat)

    def assign_role_permissions(self):
        """Assign appropriate permissions based on user role"""
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from webapp.models.sailboat import Sailboat

        # Get content type for Sailboat model
        sailboat_ct = ContentType.objects.get_for_model(Sailboat)

        # Get permissions
        manage_perm = Permission.objects.get(
            content_type=sailboat_ct,
            codename='can_manage_sailboats'
        )
        view_perm = Permission.objects.get(
            content_type=sailboat_ct,
            codename='can_view_sailboats'
        )

        # Clear existing permissions
        self.user_permissions.remove(manage_perm, view_perm)

        # Assign permissions based on role
        if self.is_admin:
            self.user_permissions.add(manage_perm, view_perm)
        elif self.is_moderator:
            self.user_permissions.add(manage_perm, view_perm)
        else:
            self.user_permissions.add(view_perm)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.assign_role_permissions()
