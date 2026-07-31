from django.db.models import Q


class AccountUtils:
    @staticmethod
    def user_filter(queryset, params):
        search = params.get("search")

        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(username__icontains=search) 
            )
        return queryset

    @staticmethod
    def organization_filter(queryset, params):
        search = params.get("search")
        is_active = params.get("is_active")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(slug__icontains=search)
            )

        if is_active in ["true", "false"]:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        return queryset

    @staticmethod
    def membership_filter(queryset, params):
        search = params.get("search")
        role = params.get("role")
        is_active = params.get("is_active")
        organization = params.get("organization")

        if search:
            queryset = queryset.filter(
                Q(user__email__icontains=search) |
                Q(user__username__icontains=search) |
                Q(organization__name__icontains=search)
            )

        if role:
            queryset = queryset.filter(role=role)

        if is_active in ["true", "false"]:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        if organization:
            queryset = queryset.filter(organization_id=organization)

        return queryset
        
