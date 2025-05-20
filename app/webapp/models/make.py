from typing import TYPE_CHECKING
from django.db import models
from django.utils.translation import gettext_lazy as _

from webapp.models.moderation import Moderation

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class Make(models.Model):
    name = models.CharField(
        max_length=100, unique=True, help_text=_("Name of the boat manufacturer")
    )

    class Meta:
        verbose_name = _("make")
        verbose_name_plural = _("makes")
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Convert name to lowercase for case-insensitive uniqueness
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create_moderated(cls, name: str, user: "User"):
        """get or create a make, moderating it if it's new"""
        make, created = cls.objects.get_or_create(name=name)
        make.save()
        if created:
            Moderation.moderation_for(
                cls,
                object_id=make.id,
                request_note="This make was created to support a new vessel",
                requested_by=user,
                verb=Moderation.Verb.CREATE,
                data={
                    "name": name,
                },
            )
        return make
