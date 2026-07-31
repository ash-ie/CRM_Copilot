from accounts.models import Membership, Organization, User
from rest_framework import serializers
from core import constants as const
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
    )

    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source="organization",
        write_only=True,
    )

    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = Membership
        fields = [
            "id",
            "user",
            "user_id",
            "organization",
            "organization_id",
            "role",
            "role_display",
            "is_active",
            "joined_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "joined_at", "created_at", "updated_at"]

    def validate_user_id(self, user):
        if getattr(user, "is_deleted", False):
            raise serializers.ValidationError(
                const.SELECTED_USER_DELETED
            )

        if not user.is_active:
            raise serializers.ValidationError(
                const.SELECTED_USER_INACTIVE
            )

        return user


    def validate_organization_id(self, organization):
        if getattr(organization, "is_deleted", False):
            raise serializers.ValidationError(
                const.SELECTED_ORGANIZATION_DELETED
            )

        if not organization.is_active:
            raise serializers.ValidationError(
                const.SELECTED_ORGANIZATION_INACTIVE
            )

        return organization