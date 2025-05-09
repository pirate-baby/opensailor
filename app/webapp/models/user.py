from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

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
