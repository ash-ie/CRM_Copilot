from rest_framework import serializers
from core import constants as const
from clients.models import Client, Interaction, Lead


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "id",
            "organization",
            "name",
            "company_name",
            "email",
            "phone",
            "website",
            "status",
            "source",
            "owner",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_email(self, value):
        if value:
            value = value.strip().lower()
        return value

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(const.CLIENT_NAME_CANNOT_EMPTY)
        return value

    def validate(self, attrs):
        organization = attrs.get("organization", getattr(self.instance, "organization", None))
        email = attrs.get("email", getattr(self.instance, "email", None))
        if organization and email:
            qs = Client.objects.filter(organization=organization, email=email)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"email": const.CLIENT_EMAIL_EXISTS_IN_ORANZATION}
                )
        return attrs

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            "id",
            "organization",
            "client",
            "name",
            "email",
            "phone",
            "company_name",
            "source",
            "status",
            "priority",
            "value",
            "owner",
            "notes",
            "last_contacted_at",
            "next_follow_up_at",
            "score",
            "score_updated_at",
            "score_breakdown",
            "score_label",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "organization",
            "score",
            "score_updated_at",
            "score_breakdown",
            "score_label",
            "created_at",
            "updated_at",
        ]

    def get_score_label(self, obj):
        if obj.score >= 70:
            return "hot"
        if obj.score >= 40:
            return "warm"
        return "cold"

    def validate_email(self, value):
        if value:
            value = value.strip().lower()
        return value

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(const.LEAD_NAME_CANNOT_EMPTY)
        return value

    def validate(self, attrs):
        organization = attrs.get("organization", getattr(self.instance, "organization", None))
        email = attrs.get("email", getattr(self.instance, "email", None))
        if organization and email:
            qs = Lead.objects.filter(organization=organization, email=email)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"email": const.LEAD_EMAIL_EXISTS_IN_ORGANIZATION}
                ) 
        return attrs

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = [
            "id",
            "organization",
            "client",
            "lead",
            "interaction_type",
            "subject",
            "summary",
            "occurred_at",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]

    def validate(self, attrs):
        client = attrs.get("client", getattr(self.instance, "client", None))
        lead = attrs.get("lead", getattr(self.instance, "lead", None))

        if not client and not lead:
            raise serializers.ValidationError(const.INTERACTION_EITHER_CLIENT_OR_LEAD)
        if client and lead:
            raise serializers.ValidationError(const.INTERACTION_CANNOT_BE_LINKED)

        return attrs

class ClientActivitySummarySerializer(serializers.Serializer):
    client_id = serializers.IntegerField()
    client_name = serializers.CharField()
    company_name = serializers.CharField(allow_blank=True, required=False)
    status = serializers.IntegerField()
    total_leads = serializers.IntegerField()
    total_interactions = serializers.IntegerField()
    last_interaction_at = serializers.DateTimeField(allow_null=True)
    total_tasks = serializers.IntegerField()
    open_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    last_task_at = serializers.DateTimeField(allow_null=True)
    total_notes = serializers.IntegerField()
    last_note_at = serializers.DateTimeField(allow_null=True)
    recent_interactions = serializers.ListField()
    recent_tasks = serializers.ListField()
    recent_notes = serializers.ListField()
    recent_leads = serializers.ListField()

class InteractionTimelineItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    organization = serializers.IntegerField()
    client = serializers.IntegerField(allow_null=True)
    lead = serializers.IntegerField(allow_null=True)
    interaction_type = serializers.IntegerField()
    interaction_type_display = serializers.CharField()
    subject = serializers.CharField(allow_blank=True)
    summary = serializers.CharField(allow_blank=True)
    occurred_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    created_by = serializers.IntegerField(allow_null=True)

class InteractionTimelineGroupSerializer(serializers.Serializer):
    date = serializers.DateField()
    interactions = InteractionTimelineItemSerializer(many=True)

class ClientTimelineItemSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    title = serializers.CharField()
    summary = serializers.CharField(allow_blank=True, required=False)
    metadata = serializers.DictField(required=False)

class ClientTimelineResponseSerializer(serializers.Serializer):
    client_id = serializers.IntegerField()
    client_name = serializers.CharField()
    timeline = ClientTimelineItemSerializer(many=True)

class LeadSummaryClientSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class LeadSummaryInteractionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    subject = serializers.CharField()
    summary = serializers.CharField(allow_blank=True, required=False)
    interaction_type = serializers.IntegerField()
    interaction_type_display = serializers.CharField()
    occurred_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()

class LeadSummaryTaskSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    status = serializers.IntegerField()
    status_display = serializers.CharField()
    priority = serializers.IntegerField()
    priority_display = serializers.CharField()
    due_date = serializers.DateTimeField(allow_null=True, required=False)
    completed_at = serializers.DateTimeField(allow_null=True, required=False)
    is_completed = serializers.BooleanField()
    created_at = serializers.DateTimeField()

class LeadSummaryNoteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    created_at = serializers.DateTimeField()

class LeadSummaryMetricsSerializer(serializers.Serializer):
    total_interactions = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    open_tasks = serializers.IntegerField()
    total_notes = serializers.IntegerField()
    last_interaction_at = serializers.DateTimeField(allow_null=True, required=False)
    last_task_at = serializers.DateTimeField(allow_null=True, required=False)
    last_note_at = serializers.DateTimeField(allow_null=True, required=False)

class LeadSummaryResponseSerializer(serializers.Serializer):
    lead_id = serializers.IntegerField()
    lead_name = serializers.CharField()
    company_name = serializers.CharField(allow_blank=True, required=False)
    status = serializers.IntegerField()
    status_display = serializers.CharField()
    priority = serializers.IntegerField()
    priority_display = serializers.CharField()
    score = serializers.IntegerField(allow_null=True, required=False)
    client = LeadSummaryClientSerializer(allow_null=True, required=False)
    metrics = LeadSummaryMetricsSerializer()
    recent_interactions = LeadSummaryInteractionSerializer(many=True)
    recent_tasks = LeadSummaryTaskSerializer(many=True)
    recent_notes = LeadSummaryNoteSerializer(many=True)

class ClientAttentionItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    company_name = serializers.CharField(allow_blank=True, required=False)
    reason = serializers.CharField()
    last_interaction_at = serializers.DateTimeField(allow_null=True, required=False)
    open_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    priority_score = serializers.IntegerField()

class ClientsAttentionResponseSerializer(serializers.Serializer):
    clients = ClientAttentionItemSerializer(many=True)

class DailySummaryTaskSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    due_date = serializers.DateTimeField(allow_null=True, required=False)
    status = serializers.IntegerField()
    status_display = serializers.CharField()
    priority = serializers.IntegerField()
    priority_display = serializers.CharField()
    client = serializers.DictField(allow_null=True, required=False)
    lead = serializers.DictField(allow_null=True, required=False)

class DailySummaryClientSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    company_name = serializers.CharField(allow_blank=True, required=False)
    reason = serializers.CharField()
    last_interaction_at = serializers.DateTimeField(allow_null=True, required=False)
    open_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    priority_score = serializers.IntegerField()

class DailySummaryInteractionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    subject = serializers.CharField()
    summary = serializers.CharField(allow_blank=True, required=False)
    interaction_type = serializers.IntegerField()
    interaction_type_display = serializers.CharField()
    client = serializers.DictField(allow_null=True, required=False)
    lead = serializers.DictField(allow_null=True, required=False)
    occurred_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()

class DailySummaryMetricsSerializer(serializers.Serializer):
    total_clients = serializers.IntegerField()
    total_leads = serializers.IntegerField()
    total_tasks_due_today = serializers.IntegerField()
    total_overdue_tasks = serializers.IntegerField()
    total_pending_followups = serializers.IntegerField()

class DailySummaryHighlightsSerializer(serializers.Serializer):
    urgent_tasks = DailySummaryTaskSerializer(many=True)
    clients_needing_attention = DailySummaryClientSerializer(many=True)
    recent_interactions = DailySummaryInteractionSerializer(many=True)

class DailySummaryResponseSerializer(serializers.Serializer):
    date = serializers.DateField()
    summary = DailySummaryMetricsSerializer()
    highlights = DailySummaryHighlightsSerializer()

class LeadPriorityClientSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class LeadPriorityItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    company_name = serializers.CharField(allow_blank=True, required=False)
    status = serializers.IntegerField()
    status_display = serializers.CharField()
    priority = serializers.IntegerField()
    priority_display = serializers.CharField()
    score = serializers.IntegerField()
    reason = serializers.CharField()
    last_interaction_at = serializers.DateTimeField(allow_null=True, required=False)
    open_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    client = LeadPriorityClientSerializer(allow_null=True, required=False)

class LeadPrioritizationResponseSerializer(serializers.Serializer):
    leads = LeadPriorityItemSerializer(many=True)

class FollowUpSuggestionClientSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class FollowUpSuggestionLeadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class FollowUpSuggestionItemSerializer(serializers.Serializer):
    type = serializers.CharField()
    title = serializers.CharField()
    reason = serializers.CharField()
    priority = serializers.CharField()
    client = FollowUpSuggestionClientSerializer(allow_null=True, required=False)
    lead = FollowUpSuggestionLeadSerializer(allow_null=True, required=False)
    suggested_action = serializers.CharField(allow_blank=True, required=False)
    due_at = serializers.DateTimeField(allow_null=True, required=False)

class FollowUpSuggestionResponseSerializer(serializers.Serializer):
    suggestions = FollowUpSuggestionItemSerializer(many=True)

class NLQResultItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    client = serializers.DictField(allow_null=True, required=False)
    lead = serializers.DictField(allow_null=True, required=False)
    status = serializers.CharField(allow_blank=True, required=False)
    priority = serializers.CharField(allow_blank=True, required=False)
    due_date = serializers.DateTimeField(allow_null=True, required=False)

class NLQQueryResponseSerializer(serializers.Serializer):
    query = serializers.CharField()
    intent = serializers.CharField()
    confidence = serializers.FloatField(allow_null=True, required=False)
    summary = serializers.CharField()
    suggested_action = serializers.CharField(allow_blank=True, required=False)
    results = NLQResultItemSerializer(many=True)