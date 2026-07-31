class OrganizationScopedCreateMixin:
    def perform_create(self, serializer):
        user = self.request.user
        organization = None

        if hasattr(user, "membership") and user.membership:
            organization = user.membership.organization

        serializer.save(organization=organization)

class OrganizationAndCreatorScopedCreateMixin:
    def perform_create(self, serializer):
        user = self.request.user
        organization = None

        if hasattr(user, "membership") and user.membership:
            organization = user.membership.organization

        serializer.save(
            organization=organization,
            created_by=user
        )