from rest_framework import serializers
from core import constants as const
from clients.models import Client


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
            