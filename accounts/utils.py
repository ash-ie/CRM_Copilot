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
        
