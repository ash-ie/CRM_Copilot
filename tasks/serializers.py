from rest_framework import serializers
from core import constants as const
from tasks.models import Note, Task


class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.BooleanField(read_only=True)
    class Meta:
        model = Task
        fields = [
            "id",
            "organization",
            "assigned_to",
            "created_by",
            "client",
            "lead",
            "title",
            "description",
            "priority",
            "status",
            "due_date",
            "completed_at",
            "is_completed",
            "is_overdue",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id","created_by","is_overdue","created_at", "updated_at"]

    def validate(self, attrs):
        client = attrs.get("client", getattr(self.instance, "client", None))
        lead = attrs.get("lead", getattr(self.instance, "lead", None))
        assigned_to = attrs.get("assigned_to", getattr(self.instance, "assigned_to", None))
        status = attrs.get("status", getattr(self.instance, "status", None))
        completed_at = attrs.get("completed_at", getattr(self.instance, "completed_at", None))
        is_completed = attrs.get("is_completed", getattr(self.instance, "is_completed", False))
        if not client and not lead:
            raise serializers.ValidationError(
                const.TASK_EITHER_CLIENT_OR_LEAD
            )

        if client and lead:
            raise serializers.ValidationError(
                const.TASK_CANNOT_BE_LINKED
            )

        if status == Task.Status.COMPLETED and not completed_at:
            raise serializers.ValidationError(
                const.COMPLETED_AT_REQUIRED
            )

        if completed_at and status != Task.Status.COMPLETED:
            raise serializers.ValidationError(
                const.STATUS_MUST_COMPLETED
            )

        if is_completed and status != Task.Status.COMPLETED:
            raise serializers.ValidationError(
                const.IS_COMPLETED_TRUE
            )

        if assigned_to and self.context["request"].user.organization_id != assigned_to.organization_id:
            raise serializers.ValidationError(
                const.ASSIGNED_TO_ORGANIZATION
            )

        return attrs

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "id",
            "organization",
            "created_by",
            "client",
            "lead",
            "title",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]

    def validate(self, attrs):
        client = attrs.get("client", getattr(self.instance, "client", None))
        lead = attrs.get("lead", getattr(self.instance, "lead", None))

        if not client and not lead:
            raise serializers.ValidationError(
                const.NOTE_EITHER_CLIENT_OR_LEAD
            )

        if client and lead:
            raise serializers.ValidationError(
                const.NOTE_CANNOT_BE_LINKED
            )

        return attrs