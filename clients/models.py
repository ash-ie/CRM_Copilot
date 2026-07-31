from django.db import models
from django.conf import settings
from accounts.models import Organization
from core.models import TimeStampedModel
from core import constants as const
# Create your models here.
class Client(TimeStampedModel):
    class Status(models.IntegerChoices):
        ACTIVE = 1, "Active"
        INACTIVE = 2, "Inactive"
        ARCHIVED = 3, "Archived"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="clients",
    )
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    status = models.PositiveSmallIntegerField(
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    source = models.CharField(max_length=100, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_clients",
    )
    notes = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "name"]),
            models.Index(fields=["organization", "email"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "email"],
                name="unique_client_email_per_organization",
            )
        ]

    def __str__(self):
        return self.name

class Lead(TimeStampedModel):
    class Status(models.IntegerChoices):
        NEW = 1, "New"
        CONTACTED = 2, "Contacted"
        QUALIFIED = 3, "Qualified"
        WON = 4, "Won"
        LOST = 5, "Lost"

    class Priority(models.IntegerChoices):
        LOW = 1, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 3, "High"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="leads",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=100, blank=True)
    status = models.PositiveIntegerField(
        choices=Status.choices,
        default=Status.NEW,
    )
    priority = models.PositiveIntegerField(
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_leads",
    )
    notes = models.TextField(blank=True)
    last_contacted_at = models.DateTimeField(null=True, blank=True)
    next_follow_up_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "priority"]),
            models.Index(fields=["organization", "name"]),
            models.Index(fields=["organization", "email"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "email"],
                name="unique_lead_email_per_organization",
            )
        ]

    def __str__(self):
        return self.name

class Interaction(TimeStampedModel):
    class Type(models.IntegerChoices):
        CALL = 1, "Call"
        EMAIL = 2, "Email"
        MEETING = 3, "Meeting"
        WHATSAPP = 4, "WhatsApp"
        NOTE = 5, "Note"
        OTHER = 6, "Other"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="interactions",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="interactions",
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="interactions",
    )
    interaction_type = models.PositiveIntegerField(
        choices=Type.choices,
        default=Type.OTHER,
    )
    subject = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)
    occurred_at = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_interactions",
    )

    class Meta:
        ordering = ["-occurred_at", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "interaction_type"]),
            models.Index(fields=["organization", "occurred_at"]),
            models.Index(fields=["organization", "client"]),
            models.Index(fields=["organization", "lead"]),
        ]

    def clean(self):
        if not self.client and not self.lead:
            raise ValueError(const.INTERACTION_EITHER_CLIENT_OR_LEAD)
        if self.client and self.lead:
            raise ValueError(const.INTERACTION_CANNOT_BE_LINKED)

    def __str__(self):
        return self.subject or f"{self.interaction_type} interaction"