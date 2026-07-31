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

    @staticmethod
    def lead_filter(queryset, params):
        search = params.get("search")
        status = params.get("status")
        priority = params.get("priority")
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

        if priority:
            queryset = queryset.filter(priority=priority)

        if owner:
            queryset = queryset.filter(owner_id=owner)

        return queryset

    @staticmethod
    def interaction_filter(queryset, params):
        search = params.get("search")
        interaction_type = params.get("interaction_type")
        client = params.get("client")
        lead = params.get("lead")

        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search) |
                Q(summary__icontains=search)
            )

        if interaction_type:
            queryset = queryset.filter(interaction_type=interaction_type)

        if client:
            queryset = queryset.filter(client_id=client)

        if lead:
            queryset = queryset.filter(lead_id=lead)

        return queryset