from django.urls import include, path
from rest_framework.routers import DefaultRouter
from clients.views import ClientActivitySummaryView, ClientTimelineView, ClientViewSet, ClientsAttentionView, DailySummaryView, FollowUpSuggestionView, InteractionViewSet, LeadPrioritizationView, LeadSummaryView, LeadViewSet, NaturalLanguageQueryView

router = DefaultRouter()
router.register(r"clients", ClientViewSet, basename="client")
router.register(r"leads", LeadViewSet, basename="lead")
router.register(r"interactions", InteractionViewSet, basename="interaction")

urlpatterns = [
    path("", include(router.urls)),
    path("<int:client_id>/activity-summary/",ClientActivitySummaryView.as_view(),name="client-activity-summary"),
    path("<int:client_id>/timeline/",ClientTimelineView.as_view(),name="client-timeline"),
    path("leads/<int:lead_id>/summary/",LeadSummaryView.as_view(),name="lead-summary"),
    path("clients/attention/",ClientsAttentionView.as_view(),name="clients-attention"),
    path("dashboard/daily-summary/",DailySummaryView.as_view(),name="daily-summary"),
    path("leads/prioritization/",LeadPrioritizationView.as_view(),name="lead-prioritization"),
    path("suggestions/follow-up/", FollowUpSuggestionView.as_view(), name="follow-up-suggestions"),
    path("copilot/query/", NaturalLanguageQueryView.as_view(), name="natural-language-query"),
]