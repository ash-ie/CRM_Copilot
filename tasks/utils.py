from django.db.models import Q
from django.utils import timezone

from tasks.models import Task


class TaskUtils:
    @staticmethod
    def task_filter(queryset, params):
        search = params.get("search")
        status = params.get("status")
        priority = params.get("priority")
        assigned_to = params.get("assigned_to")
        client = params.get("client")
        lead = params.get("lead")
        due_date = params.get("due_date")
        overdue = params.get("overdue")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        if status:
            queryset = queryset.filter(status=status)

        if priority:
            queryset = queryset.filter(priority=priority)

        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)

        if client:
            queryset = queryset.filter(client_id=client)

        if lead:
            queryset = queryset.filter(lead_id=lead)

        if due_date:
            queryset = queryset.filter(due_date__date=due_date)

        if overdue:
            queryset = queryset.overdue()

        return queryset

    @staticmethod
    def note_filter(queryset, params):
        search = params.get("search")
        client = params.get("client")
        lead = params.get("lead")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )

        if client:
            queryset = queryset.filter(client_id=client)

        if lead:
            queryset = queryset.filter(lead_id=lead)

        return queryset