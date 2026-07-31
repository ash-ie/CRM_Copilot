from django.urls import path
from accounts.views import MembershipDetailView, MembershipListCreateView, OrganizationDetailView, OrganizationListCreateView, UserDetailView, UserListCreateView

urlpatterns = [
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("organizations/", OrganizationListCreateView.as_view(), name="organization-list-create"),
    path("organizations/<int:pk>/", OrganizationDetailView.as_view(), name="organization-detail"),
    path("memberships/", MembershipListCreateView.as_view(), name="membership-list-create"),
    path("memberships/<int:pk>/", MembershipDetailView.as_view(), name="membership-detail"),
]