from django.urls import include, path
from rest_framework.routers import DefaultRouter
from clients.views import ClientViewSet, InteractionViewSet, LeadViewSet

router = DefaultRouter()
router.register(r"clients", ClientViewSet, basename="client")
router.register(r"leads", LeadViewSet, basename="lead")
router.register(r"interactions", InteractionViewSet, basename="interaction")

urlpatterns = [
    path("", include(router.urls)),
]