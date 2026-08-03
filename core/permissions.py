from typing import Any
from rest_framework.permissions import BasePermission, SAFE_METHODS

ROLE_OWNER = "owner"
ROLE_ADMIN = "admin"
ROLE_MEMBER = "member"
ROLE_VIEWER = "viewer"

class BaseOrgPermission(BasePermission):
    message = "Permission denied."

    def is_superuser(self, request) -> bool:
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and getattr(user, "is_superuser", False))

    def is_authenticated(self, request) -> bool:
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated)

    def has_permission(self, request, view) -> bool:
        return self.is_authenticated(request)

    def get_organization(self, obj: Any):
        return getattr(obj, "organization", None)

    def get_membership(self, request, obj: Any):
        organization = self.get_organization(obj)
        if organization is None:
            return None

        memberships = getattr(organization, "memberships", None)
        if memberships is None:
            return None

        return memberships.filter(user=request.user).select_related("organization", "user").first()

    def is_org_member(self, request, obj: Any) -> bool:
        organization = self.get_organization(obj)
        if organization is None:
            return False

        memberships = getattr(organization, "memberships", None)
        if memberships is None:
            return False

        return memberships.filter(user=request.user).exists()

    def has_object_permission(self, request, view, obj: Any) -> bool:
        if self.is_superuser(request):
            return True
        return False

    def is_owner_or_admin(self, request, obj: Any) -> bool:
        membership = self.get_membership(request, obj)
        return bool(membership and membership.role in {ROLE_OWNER, ROLE_ADMIN})

    def is_owner(self, request, obj: Any) -> bool:
        membership = self.get_membership(request, obj)
        return bool(membership and membership.role == ROLE_OWNER)

    def is_viewer(self, request, obj: Any) -> bool:
        membership = self.get_membership(request, obj)
        return bool(membership and membership.role == ROLE_VIEWER)

    def is_creator(self, request, obj: Any) -> bool:
        return getattr(obj, "created_by", None) == request.user

    def is_assignee(self, request, obj: Any) -> bool:
        return getattr(obj, "assigned_to", None) == request.user

class IsAuthenticatedAndOrgMember(BaseOrgPermission):
    message = "You must be a member of this organization."

    def has_object_permission(self, request, view, obj: Any) -> bool:
        if self.is_superuser(request):
            return True
        return self.is_org_member(request, obj)

class IsOrganizationAdminOrOwner(BaseOrgPermission):
    message = "You must be an organization admin or owner."

    def has_object_permission(self, request, view, obj: Any) -> bool:
        if self.is_superuser(request):
            return True
        return self.is_owner_or_admin(request, obj)

class IsOrganizationOwner(BaseOrgPermission):
    message = "You must be the organization owner."

    def has_object_permission(self, request, view, obj: Any) -> bool:
        if self.is_superuser(request):
            return True
        return self.is_owner(request, obj)

class IsOrgMemberReadOnly(BaseOrgPermission):
    message = "You must be a member of this organization to view this resource."

    def has_object_permission(self, request, view, obj: Any) -> bool:
        if self.is_superuser(request):
            return True

        if request.method not in SAFE_METHODS:
            return False

        return self.is_org_member(request, obj)

class IsAssignedOrCreatorOrAdmin(BaseOrgPermission):
    message = "You can only access objects assigned to you, created by you, or managed by an admin/owner."

    def has_object_permission(self, request, view, obj: Any) -> bool:
        if self.is_superuser(request):
            return True

        if request.method in SAFE_METHODS:
            return True

        if self.is_owner_or_admin(request, obj):
            return True

        return self.is_creator(request, obj) or self.is_assignee(request, obj)

class IsAssignedOrCreator(BaseOrgPermission):
    message = "You can only modify objects you created or were assigned."

    def has_object_permission(self, request, view, obj: Any) -> bool:
        if self.is_superuser(request):
            return True

        if request.method in SAFE_METHODS:
            return True

        return self.is_creator(request, obj) or self.is_assignee(request, obj)

class IsTaskAssigneeOrCreatorOrAdmin(BaseOrgPermission):
    message = "You can only access tasks assigned to you, created by you, or managed by an admin/owner."

    def has_object_permission(self, request, view, obj: Any) -> bool:
        if self.is_superuser(request):
            return True

        if request.method in SAFE_METHODS:
            return True

        if self.is_owner_or_admin(request, obj):
            return True

        return self.is_creator(request, obj) or self.is_assignee(request, obj)

class IsNoteOwnerOrAdmin(BaseOrgPermission):
    message = "You can only access notes you created or notes managed by an admin/owner."

    def has_object_permission(self, request, view, obj: Any) -> bool:
        if self.is_superuser(request):
            return True

        if request.method in SAFE_METHODS:
            return True

        if self.is_owner_or_admin(request, obj):
            return True

        return self.is_creator(request, obj)

class CanManageMembership(BaseOrgPermission):
    message = "Only organization owners and admins can manage memberships."

    def has_object_permission(self, request, view, obj: Any) -> bool:
        if self.is_superuser(request):
            return True
        return self.is_owner_or_admin(request, obj)

class CanViewOrganizationData(BaseOrgPermission):
    message = "You must belong to this organization."

    def has_object_permission(self, request, view, obj: Any) -> bool:
        if self.is_superuser(request):
            return True
        return self.is_org_member(request, obj)

class ReadOnlyForViewers(BaseOrgPermission):
    message = "This action is restricted to read-only users."

    def has_object_permission(self, request, view, obj: Any) -> bool:
        if self.is_superuser(request):
            return True

        if request.method in SAFE_METHODS:
            return True

        return not self.is_viewer(request, obj)

class IsAgentSystemActor(BasePermission):
    message = "Only the agent system actor can perform this action."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and getattr(user, "is_agent", False))

    def has_object_permission(self, request, view, obj: Any) -> bool:
        return self.has_permission(request, view)