from collections import defaultdict

from django.db.models import Q, Count, Max
from django.db import models
from django.utils import timezone
from clients.models import Client, Interaction, Lead
from tasks.models import Note, Task


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

    @staticmethod
    def get_client_activity_summary(client_id):
        client = Client.objects.filter(id=client_id, is_deleted=False).\
            annotate(
                total_leads=Count("leads",filter=Q(leads__is_deleted=False),distinct=True),
                total_interactions=Count("interactions", distinct=True),
                last_interaction_at=Max("interactions__occurred_at"), 
                total_tasks=Count("tasks",filter=Q(tasks__is_deleted=False), distinct=True),
                open_tasks=Count("tasks",filter=Q(tasks__is_deleted=False) &\
                                  ~Q(tasks__status=Task.Status.COMPLETED),distinct=True),
                completed_tasks=Count("tasks",filter=Q(tasks__is_deleted=False,\
                                        tasks__status=Task.Status.COMPLETED),distinct=True),
                total_notes=Count("client_notes",filter=Q(client_notes__is_deleted=False), distinct=True),
                last_note_at=Max("client_notes__created_at"),
                last_task_at=Max("tasks__created_at")
            ).first()
        if not client:
            return None
        
        recent_interactions = list(Interaction.objects.filter(client_id=client_id,\
                                            organization_id=client.organization_id)\
                                        .order_by("-occurred_at")[:5]\
                                        .values(
                                            "id",
                                            "interaction_type",
                                            "subject",
                                            "summary",
                                            "occurred_at",
                                            "created_at",
                                        )
                                    )
        recent_tasks = list(Task.objects.filter(client_id=client_id,
                                organization_id=client.organization_id,
                                is_deleted=False)\
                                .order_by("-created_at")[:5]\
                                .values(
                                    "id",
                                    "title",
                                    "status",
                                    "priority",
                                    "due_date",
                                    "completed_at",
                                    "created_at",
                                )
                            )
        recent_notes = list(Note.objects.filter(client_id=client_id,
                                organization_id=client.organization_id,
                                is_deleted=False)\
                                .order_by("-created_at")[:5]\
                                .values(
                                    "id",
                                    "title",
                                    "content",
                                    "created_at",
                                )
                            )
        recent_leads = list(Lead.objects.filter(client_id=client_id,
                                organization_id=client.organization_id,
                                is_deleted=False)
                            )\
                            .order_by("-created_at")[:5]\
                            .values(
                                "id",
                                "name",
                                "status",
                                "priority",
                                "score",
                                "created_at",
                            )
        return {
            "client_id": client.id,
            "client_name": client.name,
            "company_name": client.company_name,
            "status": client.status,
            "total_leads": client.total_leads,
            "total_interactions": client.total_interactions,
            "last_interaction_at": client.last_interaction_at,
            "total_tasks": client.total_tasks,
            "open_tasks": client.open_tasks,
            "completed_tasks": client.completed_tasks,
            "last_task_at": client.last_task_at,
            "total_notes": client.total_notes,
            "last_note_at": client.last_note_at,
            "recent_interactions": recent_interactions,
            "recent_tasks": recent_tasks,
            "recent_notes": recent_notes,
            "recent_leads": recent_leads,
        }

    @staticmethod
    def timeline_group(queryset, params):
        client = params.get("client")
        lead = params.get("lead")
        interaction_type = params.get("interaction_type")
        search = params.get("search")

        if client:
            queryset = queryset.filter(client_id=client)

        if lead:
            queryset = queryset.filter(lead_id=lead)

        if interaction_type:
            queryset = queryset.filter(interaction_type=interaction_type)

        if search:
            queryset = queryset.filter(
                models.Q(subject__icontains=search) |
                models.Q(summary__icontains=search)
            )

        queryset = queryset.order_by("-occurred_at", "-created_at")
        grouped = defaultdict(list)

        for item in queryset:
            date_key = item.occurred_at.date()
            grouped[date_key].append({
                "id": item.id,
                "organization": item.organization_id,
                "client": item.client_id,
                "lead": item.lead_id,
                "interaction_type": item.interaction_type,
                "interaction_type_display": item.get_interaction_type_display(),
                "subject": item.subject,
                "summary": item.summary,
                "occurred_at": item.occurred_at,
                "created_at": item.created_at,
                "created_by": item.created_by_id
            })

        return [
            {
                "date": date,
                "interactions": grouped[date],
            }
            for date in sorted(grouped.keys(), reverse=True)
        ]

    @staticmethod
    def build_client_timeline(client):
        interaction_items = list(
            Interaction.objects.filter(client_id=client.id, organization_id=client.organization_id)
            .values(
                "id",
                "organization_id",
                "client_id",
                "lead_id",
                "interaction_type",
                "subject",
                "summary",
                "occurred_at",
                "created_at",
                "created_by_id",
            )
        )

        task_items = list(
            Task.objects.filter(client_id=client.id, organization_id=client.organization_id, is_deleted=False)
            .values(
                "id",
                "organization_id",
                "client_id",
                "lead_id",
                "title",
                "description",
                "created_at",
                "created_by_id",
                "due_date",
                "status",
                "priority",
            )
        )

        note_items = list(
            Note.objects.filter(client_id=client.id, organization_id=client.organization_id, is_deleted=False)
            .values(
                "id",
                "organization_id",
                "client_id",
                "lead_id",
                "title",
                "content",
                "created_at",
                "created_by_id",
            )
        )

        timeline = []

        for item in interaction_items:
            timeline.append({
                "id": item["id"],
                "organization": item["organization_id"],
                "client": item["client_id"],
                "lead": item["lead_id"],
                "type": "interaction",
                "title": item["subject"],
                "summary": item["summary"] or "",
                "occurred_at": item["occurred_at"],
                "created_at": item["created_at"],
                "created_by": item["created_by_id"],
                "metadata": {
                    "interaction_type": item["interaction_type"],
                },
            })

        for item in task_items:
            timeline.append({
                "id": item["id"],
                "organization": item["organization_id"],
                "client": item["client_id"],
                "lead": item["lead_id"],
                "type": "task",
                "title": item["title"],
                "summary": item["description"] or "",
                "occurred_at": item["created_at"],
                "created_at": item["created_at"],
                "created_by": item["created_by_id"],
                "metadata": {
                    "due_date": item["due_date"],
                    "status": item["status"],
                    "priority": item["priority"],
                },
            })

        for item in note_items:
            timeline.append({
                "id": item["id"],
                "organization": item["organization_id"],
                "client": item["client_id"],
                "lead": item["lead_id"],
                "type": "note",
                "title": item["title"],
                "summary": item["content"] or "",
                "occurred_at": item["created_at"],
                "created_at": item["created_at"],
                "created_by": item["created_by_id"],
                "metadata": {},
            })

        return sorted(
            timeline,
            key=lambda x: (x["occurred_at"] or x["created_at"]),
            reverse=True,
        )

    @staticmethod
    def lead_summary_data(lead):
        if not lead:
            return None

        total_interactions = Interaction.objects.filter(
            lead_id=lead.id,
            organization_id=lead.organization_id,
        ).count()

        total_tasks = Task.objects.filter(
            lead_id=lead.id,
            organization_id=lead.organization_id,
            is_deleted=False,
        ).count()

        open_tasks = Task.objects.filter(
            lead_id=lead.id,
            organization_id=lead.organization_id,
            is_deleted=False,
        ).exclude(
            status__in=[Task.Status.COMPLETED, Task.Status.CANCELLED]
        ).count()

        total_notes = Note.objects.filter(
            lead_id=lead.id,
            organization_id=lead.organization_id,
            is_deleted=False,
        ).count()

        last_interaction_at = Interaction.objects.filter(
            lead_id=lead.id,
            organization_id=lead.organization_id,
        ).aggregate(last=Max("occurred_at"))["last"]

        last_task_at = Task.objects.filter(
            lead_id=lead.id,
            organization_id=lead.organization_id,
            is_deleted=False,
        ).aggregate(last=Max("created_at"))["last"]

        last_note_at = Note.objects.filter(
            lead_id=lead.id,
            organization_id=lead.organization_id,
            is_deleted=False,
        ).aggregate(last=Max("created_at"))["last"]

        recent_interactions = list(
            Interaction.objects.filter(
                lead_id=lead.id,
                organization_id=lead.organization_id,
            )
            .order_by("-occurred_at", "-created_at")[:5]
            .values(
                "id",
                "subject",
                "summary",
                "interaction_type",
                "occurred_at",
                "created_at",
            )
        )

        recent_tasks = list(
            Task.objects.filter(
                lead_id=lead.id,
                organization_id=lead.organization_id,
                is_deleted=False,
            )
            .order_by("-created_at")[:5]
            .values(
                "id",
                "title",
                "description",
                "status",
                "priority",
                "due_date",
                "completed_at",
                "is_completed",
                "created_at",
            )
        )

        recent_notes = list(
            Note.objects.filter(
                lead_id=lead.id,
                organization_id=lead.organization_id,
                is_deleted=False,
            )
            .order_by("-created_at")[:5]
            .values(
                "id",
                "title",
                "content",
                "created_at",
            )
        )

        client_data = None
        if lead.client_id and lead.client:
            client_data = {
                "id": lead.client.id,
                "name": lead.client.name,
            }

        return {
            "lead_id": lead.id,
            "lead_name": lead.name,
            "company_name": lead.company_name,
            "status": lead.status,
            "status_display": lead.get_status_display(),
            "priority": lead.priority,
            "priority_display": lead.get_priority_display(),
            "score": getattr(lead, "score", None),
            "client": client_data,
            "metrics": {
                "total_interactions": total_interactions,
                "total_tasks": total_tasks,
                "open_tasks": open_tasks,
                "total_notes": total_notes,
                "last_interaction_at": last_interaction_at,
                "last_task_at": last_task_at,
                "last_note_at": last_note_at,
            },
            "recent_interactions": recent_interactions,
            "recent_tasks": recent_tasks,
            "recent_notes": recent_notes,
        }

    @staticmethod
    def clients_needing_attention(queryset, params):
        search = params.get("search")
        status = params.get("status")
        owner = params.get("owner")

        queryset = queryset.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(company_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
                | Q(source__icontains=search)
            )

        if status:
            queryset = queryset.filter(status=status)

        if owner:
            queryset = queryset.filter(owner_id=owner)

        results = []

        for client in queryset:
            open_tasks = Task.objects.filter(
                client_id=client.id,
                organization_id=client.organization_id,
                is_deleted=False,
            ).exclude(
                status__in=[Task.Status.COMPLETED, Task.Status.CANCELLED]
            )

            overdue_tasks = open_tasks.filter(due_date__lt=__import__("django.utils.timezone", fromlist=["now"]).now())

            last_interaction_at = Interaction.objects.filter(
                client_id=client.id,
                organization_id=client.organization_id,
            ).aggregate(last=Max("occurred_at"))["last"]

            recent_notes_count = Note.objects.filter(
                client_id=client.id,
                organization_id=client.organization_id,
                is_deleted=False,
            ).count()

            reason_parts = []
            if overdue_tasks.exists():
                reason_parts.append("Overdue tasks")
            if open_tasks.count() > 0 and not overdue_tasks.exists():
                reason_parts.append("Pending follow-up")
            if not last_interaction_at:
                reason_parts.append("No recent interaction")
            if recent_notes_count == 0:
                reason_parts.append("No notes")

            priority_score = 0
            priority_score += overdue_tasks.count() * 40
            priority_score += open_tasks.count() * 10
            if not last_interaction_at:
                priority_score += 20
            if recent_notes_count == 0:
                priority_score += 10

            if priority_score == 0:
                continue

            results.append({
                "id": client.id,
                "name": client.name,
                "company_name": client.company_name,
                "reason": ", ".join(reason_parts) if reason_parts else "Needs attention",
                "last_interaction_at": last_interaction_at,
                "open_tasks": open_tasks.count(),
                "overdue_tasks": overdue_tasks.count(),
                "priority_score": priority_score,
            })

        results = sorted(results, key=lambda x: x["priority_score"], reverse=True)
        return {"clients": results}

    @staticmethod
    def daily_summary_data(organization):
        today = timezone.localdate()
        now = timezone.now()

        total_clients = Client.objects.filter(
            organization=organization,
            is_deleted=False,
        ).count()

        total_leads = Lead.objects.filter(
            organization=organization,
            is_deleted=False,
        ).count()

        due_today_queryset = Task.objects.filter(
            organization=organization,
            is_deleted=False,
            due_date__date=today,
        ).exclude(
            status__in=[Task.Status.COMPLETED, Task.Status.CANCELLED]
        )

        overdue_queryset = Task.objects.filter(
            organization=organization,
            is_deleted=False,
            due_date__lt=now,
        ).exclude(
            status__in=[Task.Status.COMPLETED, Task.Status.CANCELLED]
        )

        pending_followups = Task.objects.filter(
            organization=organization,
            is_deleted=False,
        ).exclude(
            status__in=[Task.Status.COMPLETED, Task.Status.CANCELLED]
        ).count()

        clients_attention_data = ClientUtils.clients_needing_attention(
            Client.objects.filter(
                organization=organization,
                is_deleted=False,
            ),
            {},
        )["clients"]

        urgent_tasks = list(
            due_today_queryset.order_by("-priority", "due_date")[:5].values(
                "id",
                "title",
                "due_date",
                "status",
                "priority",
                "client_id",
                "lead_id",
            )
        )

        recent_interactions = list(
            Interaction.objects.filter(
                organization=organization,
            )
            .order_by("-occurred_at", "-created_at")[:5]
            .values(
                "id",
                "subject",
                "summary",
                "interaction_type",
                "client_id",
                "lead_id",
                "occurred_at",
                "created_at",
            )
        )

        def map_ref(obj_id, model):
            if not obj_id:
                return None
            return {
                "id": obj_id,
                "name": model.objects.filter(id=obj_id).values_list("name", flat=True).first() or "",
            }

        urgent_tasks_payload = []
        for task in urgent_tasks:
            urgent_tasks_payload.append({
                "id": task["id"],
                "title": task["title"],
                "due_date": task["due_date"],
                "status": task["status"],
                "status_display": Task.Status(task["status"]).label if task["status"] else "",
                "priority": task["priority"],
                "priority_display": Task.Priority(task["priority"]).label if task["priority"] else "",
                "client": map_ref(task["client_id"], Client),
                "lead": map_ref(task["lead_id"], Lead),
            })

        recent_interactions_payload = []
        for interaction in recent_interactions:
            recent_interactions_payload.append({
                "id": interaction["id"],
                "subject": interaction["subject"],
                "summary": interaction["summary"] or "",
                "interaction_type": interaction["interaction_type"],
                "interaction_type_display": Interaction.InteractionType(interaction["interaction_type"]).label \
                    if hasattr(Interaction, "InteractionType") and interaction["interaction_type"] else interaction["interaction_type"],
                "client": map_ref(interaction["client_id"], Client),
                "lead": map_ref(interaction["lead_id"], Lead),
                "occurred_at": interaction["occurred_at"],
                "created_at": interaction["created_at"],
            })

        return {
            "date": today,
            "summary": {
                "total_clients": total_clients,
                "total_leads": total_leads,
                "total_tasks_due_today": due_today_queryset.count(),
                "total_overdue_tasks": overdue_queryset.count(),
                "total_pending_followups": pending_followups,
            },
            "highlights": {
                "urgent_tasks": urgent_tasks_payload,
                "clients_needing_attention": clients_attention_data[:5],
                "recent_interactions": recent_interactions_payload,
            },
        }

    @staticmethod
    def lead_prioritization_data(queryset, params):
        search = params.get("search")
        status = params.get("status")
        priority = params.get("priority")
        min_score = params.get("min_score")

        queryset = queryset.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(
                name__icontains=search
            )

        if status:
            queryset = queryset.filter(status=status)

        if priority:
            queryset = queryset.filter(priority=priority)

        results = []

        for lead in queryset:
            open_tasks_queryset = Task.objects.filter(
                lead_id=lead.id,
                organization_id=lead.organization_id,
                is_deleted=False,
            ).exclude(
                status__in=[Task.Status.COMPLETED, Task.Status.CANCELLED]
            )

            overdue_tasks_queryset = open_tasks_queryset.filter(due_date__lt=timezone.now())

            last_interaction_at = Interaction.objects.filter(
                lead_id=lead.id,
                organization_id=lead.organization_id,
            ).aggregate(last=Max("occurred_at"))["last"]

            open_tasks = open_tasks_queryset.count()
            overdue_tasks = overdue_tasks_queryset.count()

            score = getattr(lead, "score", 0) or 0
            reason_parts = []

            if score >= 80:
                reason_parts.append("High lead score")
            elif score >= 50:
                reason_parts.append("Moderate lead score")
            else:
                reason_parts.append("Low lead score")

            if last_interaction_at:
                reason_parts.append("Recent interaction")
            else:
                reason_parts.append("No recent interaction")

            if overdue_tasks > 0:
                reason_parts.append("Overdue follow-up")
            elif open_tasks > 0:
                reason_parts.append("Open follow-up tasks")

            priority_score = score + (overdue_tasks * 20) + (open_tasks * 5)
            if not last_interaction_at:
                priority_score += 10

            if min_score:
                try:
                    if priority_score < int(min_score):
                        continue
                except (TypeError, ValueError):
                    pass

            results.append({
                "id": lead.id,
                "name": lead.name,
                "company_name": lead.company_name,
                "status": lead.status,
                "status_display": lead.get_status_display(),
                "priority": lead.priority,
                "priority_display": lead.get_priority_display(),
                "score": priority_score,
                "reason": ", ".join(reason_parts),
                "last_interaction_at": last_interaction_at,
                "open_tasks": open_tasks,
                "overdue_tasks": overdue_tasks,
                "client": {
                    "id": lead.client_id,
                    "name": lead.client.name if lead.client else "",
                } if lead.client_id else None,
            })

        results = sorted(results, key=lambda x: x["score"], reverse=True)
        return {"leads": results}

    @staticmethod
    def follow_up_suggestions_data(queryset, params):
        search = params.get("search")
        client_id = params.get("client")
        lead_id = params.get("lead")
        priority = params.get("priority")

        queryset = queryset.filter(is_deleted=False)

        if search:
            queryset = queryset.filter(name__icontains=search)

        if client_id:
            queryset = queryset.filter(client_id=client_id)

        if lead_id:
            queryset = queryset.filter(id=lead_id)

        suggestions = []
        now = timezone.now()

        for lead in queryset:
            open_tasks = Task.objects.filter(
                lead_id=lead.id,
                organization_id=lead.organization_id,
                is_deleted=False,
            ).exclude(
                status__in=[Task.Status.COMPLETED, Task.Status.CANCELLED]
            )

            overdue_tasks = open_tasks.filter(due_date__lt=now)

            last_interaction = Interaction.objects.filter(
                lead_id=lead.id,
                organization_id=lead.organization_id,
            ).order_by("-occurred_at", "-created_at").first()

            last_contact_at = last_interaction.occurred_at if last_interaction else None
            days_since_contact = None
            if last_contact_at:
                days_since_contact = (now - last_contact_at).days

            if overdue_tasks.exists():
                suggestion_type = "call"
                title = f"Follow up with {lead.name}"
                reason = f"{overdue_tasks.count()} overdue task(s) and pending follow-up"
                suggested_action = "Call the lead and clear overdue action items"
                priority_level = "high"
            elif not last_contact_at or (days_since_contact is not None and days_since_contact >= 7):
                suggestion_type = "message"
                title = f"Reconnect with {lead.name}"
                reason = "No recent interaction"
                suggested_action = "Send a follow-up message or email"
                priority_level = "medium"
            else:
                suggestion_type = "checkin"
                title = f"Check in with {lead.name}"
                reason = "Open tasks need review"
                suggested_action = "Review current task progress"
                priority_level = "low"

            if priority and priority_level != priority:
                continue

            suggestions.append({
                "type": suggestion_type,
                "title": title,
                "reason": reason,
                "priority": priority_level,
                "client": {
                    "id": lead.client_id,
                    "name": lead.client.name if lead.client else "",
                } if lead.client_id else None,
                "lead": {
                    "id": lead.id,
                    "name": lead.name,
                },
                "suggested_action": suggested_action,
                "due_at": last_contact_at,
            })

        return {"suggestions": suggestions}

    @staticmethod
    def natural_language_query_data(query, organization):
        q = (query or "").strip().lower()
        results = []
        intent = "unknown"
        summary = "No matching data found"
        confidence = 0.4
        suggested_action = "Refine your question"

        if any(keyword in q for keyword in ["overdue client", "clients needing attention", "attention clients"]):
            intent = "clients_needing_attention"
            confidence = 0.9
            clients = Client.objects.filter(
                organization=organization,
                is_deleted=False,
            )

            for client in clients:
                open_tasks = Task.objects.filter(
                    client_id=client.id,
                    organization_id=organization.id,
                    is_deleted=False,
                ).exclude(
                    status__in=[Task.Status.COMPLETED, Task.Status.CANCELLED]
                )

                overdue_tasks = open_tasks.filter(due_date__lt=timezone.now())

                if overdue_tasks.exists() or open_tasks.exists():
                    results.append({
                        "id": client.id,
                        "type": "client",
                        "title": client.name,
                        "description": client.company_name or "",
                        "client": {
                            "id": client.id,
                            "name": client.name,
                        },
                        "lead": None,
                        "status": client.status,
                        "priority": "high" if overdue_tasks.exists() else "medium",
                        "due_date": None,
                    })

            summary = f"{len(results)} client(s) need attention"
            suggested_action = "Review overdue tasks and follow up with clients"

        elif any(keyword in q for keyword in ["overdue task", "overdue tasks", "tasks overdue"]):
            intent = "overdue_tasks"
            confidence = 0.92
            tasks = Task.objects.filter(
                organization=organization,
                is_deleted=False,
            ).exclude(
                status__in=[Task.Status.COMPLETED, Task.Status.CANCELLED]
            ).filter(
                due_date__lt=timezone.now()
            )

            for task in tasks.select_related("client", "lead"):
                results.append({
                    "id": task.id,
                    "type": "task",
                    "title": task.title,
                    "description": task.description,
                    "client": {
                        "id": task.client_id,
                        "name": task.client.name if task.client else "",
                    } if task.client_id else None,
                    "lead": {
                        "id": task.lead_id,
                        "name": task.lead.name if task.lead else "",
                    } if task.lead_id else None,
                    "status": str(task.status),
                    "priority": str(task.priority),
                    "due_date": task.due_date,
                })

            summary = f"{len(results)} overdue task(s) found"
            suggested_action = "Work on overdue tasks first"

        elif any(keyword in q for keyword in ["follow up", "next action", "suggestion"]):
            intent = "follow_up_suggestions"
            confidence = 0.88
            leads = Lead.objects.filter(
                organization=organization,
                is_deleted=False,
            ).select_related("client")

            for lead in leads:
                last_interaction = Interaction.objects.filter(
                    lead_id=lead.id,
                    organization_id=organization.id,
                ).order_by("-occurred_at", "-created_at").first()

                if not last_interaction or (timezone.now() - last_interaction.occurred_at).days >= 7:
                    results.append({
                        "id": lead.id,
                        "type": "lead",
                        "title": lead.name,
                        "description": lead.company_name or "",
                        "client": {
                            "id": lead.client_id,
                            "name": lead.client.name if lead.client else "",
                        } if lead.client_id else None,
                        "lead": {
                            "id": lead.id,
                            "name": lead.name,
                        },
                        "status": str(lead.status),
                        "priority": str(lead.priority),
                        "due_date": None,
                    })

            summary = f"{len(results)} follow-up suggestion(s) found"
            suggested_action = "Reach out to inactive leads"

        else:
            # generic fallback: search across models
            intent = "search"
            confidence = 0.55

            client_results = Client.objects.filter(
                organization=organization,
                is_deleted=False,
                name__icontains=query,
            )[:5]
            lead_results = Lead.objects.filter(
                organization=organization,
                is_deleted=False,
                name__icontains=query,
            )[:5]
            task_results = Task.objects.filter(
                organization=organization,
                is_deleted=False,
                title__icontains=query,
            ).select_related("client", "lead")[:5]
            note_results = Note.objects.filter(
                organization=organization,
                is_deleted=False,
                title__icontains=query,
            )[:5]

            for obj in client_results:
                results.append({
                    "id": obj.id,
                    "type": "client",
                    "title": obj.name,
                    "description": obj.company_name or "",
                    "client": {"id": obj.id, "name": obj.name},
                    "lead": None,
                    "status": str(obj.status),
                    "priority": "",
                    "due_date": None,
                })

            for obj in lead_results:
                results.append({
                    "id": obj.id,
                    "type": "lead",
                    "title": obj.name,
                    "description": obj.company_name or "",
                    "client": {
                        "id": obj.client_id,
                        "name": obj.client.name if obj.client else "",
                    } if obj.client_id else None,
                    "lead": {"id": obj.id, "name": obj.name},
                    "status": str(obj.status),
                    "priority": str(obj.priority),
                    "due_date": None,
                })

            for obj in task_results:
                results.append({
                    "id": obj.id,
                    "type": "task",
                    "title": obj.title,
                    "description": obj.description,
                    "client": {
                        "id": obj.client_id,
                        "name": obj.client.name if obj.client else "",
                    } if obj.client_id else None,
                    "lead": {
                        "id": obj.lead_id,
                        "name": obj.lead.name if obj.lead else "",
                    } if obj.lead_id else None,
                    "status": str(obj.status),
                    "priority": str(obj.priority),
                    "due_date": obj.due_date,
                })

            for obj in note_results:
                results.append({
                    "id": obj.id,
                    "type": "note",
                    "title": obj.title,
                    "description": obj.content,
                    "client": {
                        "id": obj.client_id,
                        "name": obj.client.name if obj.client else "",
                    } if obj.client_id else None,
                    "lead": {
                        "id": obj.lead_id,
                        "name": obj.lead.name if obj.lead else "",
                    } if obj.lead_id else None,
                    "status": "",
                    "priority": "",
                    "due_date": None,
                })

            summary = f"Found {len(results)} matching item(s)"
            suggested_action = "Review the matching records"

        return {
            "query": query,
            "intent": intent,
            "confidence": confidence,
            "summary": summary,
            "suggested_action": suggested_action,
            "results": results,
        }


    
                                