from rest_framework.exceptions import PermissionDenied


class OrganizationAndCreatorScopedCreateMixin:
    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, "membership") or not user.membership:
            raise PermissionDenied("User does not belong to an organization.")

        serializer.save(
            organization=user.membership.organization,
            created_by=user
        )