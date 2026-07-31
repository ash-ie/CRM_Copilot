from django.db.models import Q


class ClientUtils:
    @staticmethod
    def client_filter(queryset, params):
        search = params.get("search")
        status = params.get("status")
        owner = params.get("owner")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(company_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(source__icontains=search)
            )

        if status:
            queryset = queryset.filter(status=status)

        if owner:
            queryset = queryset.filter(owner_id=owner)

        return queryset