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
        
