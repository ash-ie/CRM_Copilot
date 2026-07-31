from rest_framework.permissions import BasePermission


class IsOrganizationScoped(BasePermission):
    """
    Allows access only to users who belong to an organization,
    and only to objects in that organization.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return hasattr(user, "membership") and user.membership is not None

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if not hasattr(user, "membership") or not user.membership:
            return False

        user_org = user.membership.organization

        obj_org = getattr(obj, "organization", None)
        if obj_org is None:
            return False

        return obj_org == user_org