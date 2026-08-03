from rest_framework import serializers
from agentic.models import AgentActionLog, AgentRun
from core import constants as const

class AgentRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentRun
        fields = [
            "id",
            "organization",
            "created_by",
            "agent_name",
            "prompt",
            "status",
            "input_data",
            "output_data",
            "error_message",
            "started_at",
            "finished_at",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "organization",
            "created_by",
            "status",
            "output_data",
            "error_message",
            "started_at",
            "finished_at",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        if not hasattr(user, "membership"):
            raise serializers.ValidationError(const.USER_NOT_IN_ORGANIZATION)

        validated_data["organization"] = user.membership.organization
        validated_data["created_by"] = user
        return super().create(validated_data)
    
class AgentActionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentActionLog
        fields = [
            "id",
            "organization",
            "agent_run",
            "created_by",
            "action_type",
            "tool_name",
            "action_name",
            "input_data",
            "output_data",
            "error_message",
            "step_number",
            "success",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "organization",
            "created_by",
            "output_data",
            "error_message",
            "success",
            "created_at",
        ]

    def validate_agent_run(self, value):
        request = self.context["request"]
        user = request.user

        if not hasattr(user, "membership"):
            raise serializers.ValidationError(const.USER_NOT_IN_ORGANIZATION)

        if value.organization != user.membership.organization:
            raise serializers.ValidationError(const.CANNOT_ATTACH_LOG)

        return value