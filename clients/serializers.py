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