from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import TimeStampedModel
from django.conf import settings

# Create your models here.
class User(AbstractUser, TimeStampedModel):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email or self.username

class Organization(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Membership(TimeStampedModel):
    class Role(models.IntegerChoices):
        ADMIN = 1, "Admin"
        MANAGER = 2, "Manager"
        STAFF = 3, "Staff"
        VIEWER = 4, "Viewer"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.PositiveSmallIntegerField(
    choices=Role.choices,
    default=Role.STAFF,
    )
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "organization")
        ordering = ["organization__name", "user__email"]

    def __str__(self):
        return f"{self.user} - {self.organization} ({self.role})"