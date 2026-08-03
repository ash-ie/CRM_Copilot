from django.urls import include, path
from rest_framework.routers import DefaultRouter

from agentic.views import AgentActionLogViewSet, AgentRunViewSet

router = DefaultRouter()
router.register(r"agent-runs", AgentRunViewSet, basename="agent-run")
router.register(r"agent-action-logs", AgentActionLogViewSet, basename="agent-action-log")

urlpatterns = [
    path("", include(router.urls)),

]