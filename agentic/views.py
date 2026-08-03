from django.shortcuts import render
from rest_framework import serializers, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from agentic.models import AgentActionLog, AgentRun
from agentic.serializers import AgentActionLogSerializer, AgentRunSerializer

# Create your views here.
class AgentRunViewSet(viewsets.ModelViewSet):
    serializer_class = AgentRunSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not hasattr(user, "membership"):
            return AgentRun.objects.none()

        return AgentRun.objects.filter(
            organization=user.membership.organization
        ).select_related("organization", "created_by")

class AgentActionLogViewSet(viewsets.ModelViewSet):
    serializer_class = AgentActionLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not hasattr(user, "membership"):
            return AgentActionLog.objects.none()

        return AgentActionLog.objects.filter(
            organization=user.membership.organization
        ).select_related("organization", "agent_run", "created_by")

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            organization=user.membership.organization,
            created_by=user,
        )