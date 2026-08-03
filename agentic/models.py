import uuid
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
# Create your models here.
class AgentRun(TimeStampedModel):
    class Status(models.IntegerChoices):
        PENDING = 1, "Pending"
        RUNNING = 2, "Running"
        COMPLETED = 3, "Completed"
        FAILED = 4, "Failed"
        CANCELLED = 5, "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="agent_runs",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_agent_runs",
    )
    agent_name = models.CharField(max_length=100)
    prompt = models.TextField()
    status = models.TextField(
        choices=Status.choices,
        default=Status.PENDING,
    )
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "created_at"]),
            models.Index(fields=["agent_name"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(agent_name=""),
                name="agentrun_agent_name_not_empty",
            ),
        ]

    def __str__(self):
        return f"{self.agent_name} - {self.status} - {self.created_at:%Y-%m-%d %H:%M}"

    @property
    def duration_seconds(self):
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None

class AgentActionLog(TimeStampedModel):
    class ActionType(models.IntegerChoices):
        TOOL_CALL = 1, "Tool Call"
        TOOL_RESULT = 2, "Tool Result"
        PROMPT = 3, "Prompt"
        DECISION = 4, "Decision"
        ERROR = 5, "Error"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="agent_action_logs",
    )
    agent_run = models.ForeignKey(
        AgentRun,
        on_delete=models.CASCADE,
        related_name="action_logs",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_agent_action_logs",
    )
    action_type = models.PositiveIntegerField(
        choices=ActionType.choices,
        db_index=True,
    )
    tool_name = models.CharField(max_length=120, blank=True)
    action_name = models.CharField(max_length=120, blank=True)
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    step_number = models.PositiveIntegerField(default=0)
    success = models.BooleanField(default=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["organization", "agent_run"]),
            models.Index(fields=["agent_run", "created_at"]),
            models.Index(fields=["action_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.action_type} - {self.tool_name or self.action_name}"