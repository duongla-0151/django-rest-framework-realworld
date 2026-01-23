"""
Profile model for user profiles and following functionality.

Note: Profile functionality will be implemented in a future phase,
but the model is defined here for relationship completeness.
"""
from django.conf import settings
from django.db import models


class Profile(models.Model):
    """
    Profile model for extended user information and following.

    This model will be used for:
    - User profile pages (/api/profiles/:username)
    - Following/unfollowing users
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Following relationship (self-referential many-to-many)
    follows = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followed_by',
        blank=True
    )

    class Meta:
        db_table = 'profiles'

    def __str__(self):
        return f"Profile of {self.user.username}"

    def follow(self, profile):
        """Follow another profile."""
        self.follows.add(profile)

    def unfollow(self, profile):
        """Unfollow another profile."""
        self.follows.remove(profile)

    def is_following(self, profile):
        """Check if this profile follows another profile."""
        return self.follows.filter(pk=profile.pk).exists()
