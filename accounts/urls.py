from django.urls import path
from accounts.views import LoginAPIView, MembershipDetailView, MembershipListCreateView, OrganizationDetailView, OrganizationListCreateView, RegisterAPIView, UserDetailView, UserListCreateView

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("organizations/", OrganizationListCreateView.as_view(), name="organization-list-create"),
    path("organizations/<int:pk>/", OrganizationDetailView.as_view(), name="organization-detail"),
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("memberships/", MembershipListCreateView.as_view(), name="membership-list-create"),
    path("memberships/<int:pk>/", MembershipDetailView.as_view(), name="membership-detail"),
    path("register/", RegisterAPIView.as_view(), name="register"),
]