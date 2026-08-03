from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import TimeStampedModel

# Create your models here.
class TaskQuerySet(models.QuerySet):
    def overdue(self):
        return self.filter(
            due_date__lt=timezone.now(),
            is_deleted=False,
        ).exclude(
            is_completed=True
        ).exclude(
            status__in=[Task.Status.COMPLETED, Task.Status.CANCELLED]
        )
class Task(TimeStampedModel):
    class Priority(models.IntegerChoices):
        LOW = 1, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 3, "High"
        URGENT = 4, "Urgent"

    class Status(models.IntegerChoices):
        PENDING = 1, "Pending"
        IN_PROGRESS = 2, "In Progress"
        COMPLETED = 3, "Completed"
        CANCELLED = 4, "Cancelled"

    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_tasks",
        null=True,
        blank=True,
    )
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
        blank=True,
    )
    lead = models.ForeignKey(
        "clients.Lead",
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.PositiveIntegerField(
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.PositiveIntegerField(
        choices=Status.choices,
        default=Status.PENDING,
    )
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "due_date"]),
            models.Index(fields=["assigned_to", "status"]),
        ]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if not self.due_date:
            return False
        if self.is_deleted:
            return False
        if self.is_completed:
            return False
        if self.status in [self.Status.COMPLETED, self.Status.CANCELLED]:
            return False
        return self.due_date < timezone.now()

class Note(TimeStampedModel):
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="notes",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_notes",
        null=True,
        blank=True,
    )

    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="client_notes",
        null=True,
        blank=True,
    )

    lead = models.ForeignKey(
        "clients.Lead",
        on_delete=models.CASCADE,
        related_name="lead_notes",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "created_at"]),
            models.Index(fields=["client", "created_at"]),
            models.Index(fields=["lead", "created_at"]),
        ]

    def __str__(self):
        return self.title
    