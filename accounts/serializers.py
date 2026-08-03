from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import Membership, Organization, User
from rest_framework import serializers
from core import constants as const

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

class UserCreateSerializer(serializers.ModelSerializer):
    organization_id = serializers.IntegerField(write_only=True)
    role = serializers.ChoiceField(choices=Membership.Role.choices, write_only=True)
    password = serializers.CharField( write_only=True, required=True )
    confirm_password = serializers.CharField( write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "password", "confirm_password", "first_name", "last_name",
            "phone_number", "organization_id", "role", "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        current_user = request.user
        password = attrs["password"]
        confirm_password = attrs["confirm_password"]
        org_id = attrs["organization_id"]
        role = attrs["role"]

        if password != confirm_password: 
            raise serializers.ValidationError({"confirm_password": const.PASSWORD_MISMATCH})

        if not Organization.objects.filter(id=org_id, is_active=True, is_deleted=False).exists():
            raise serializers.ValidationError({ "organization_id":  const.ORGANIZATION_NOT_EXISTS})

        if current_user.is_superuser and role != Membership.Role.ADMIN:
            raise serializers.ValidationError({"role": const.SUPERUSER_CANNOT_CREATE})
        else:
            has_permission = Membership.objects.filter(user=current_user, organization_id=org_id,
                role__in=[ Membership.Role.ADMIN, Membership.Role.MANAGER ], is_active=True, 
                is_deleted=False).exists()
            if not has_permission: 
                raise serializers.ValidationError({ "organization_id": const.NO_PERMISSION})
        return attrs
class UserSerializer(serializers.ModelSerializer):
    organization_id = serializers.IntegerField(write_only=True, required=False)
    role = serializers.ChoiceField(choices=Membership.Role.choices, write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    organization = serializers.SerializerMethodField() 
    user_role = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "phone_number",
            "organization_id",
            "role",
            "organization",
            "user_role",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organization","created_at", "updated_at"]

    def _get_membership(self, obj):
        return obj.memberships.filter( is_active=True, is_deleted=False )\
            .select_related( "organization" ).first()
    
    def get_organization(self, obj): 
        membership = self._get_membership(obj)
        if not membership: 
            return None
        return { "id": membership.organization.id, "name": membership.organization.name, }

    def get_user_role(self, obj):
        membership = self._get_membership(obj)
        if not membership: 
            return None
        return membership.get_role_display()

    def validate(self, attrs):
        password = attrs.get("password") 
        confirm_password = attrs.get("confirm_password")

        if password or confirm_password: 
            if password != confirm_password: 
                raise serializers.ValidationError({ "confirm_password": "Passwords do not match." })   

        if "organization_id" in attrs:
            org_id = attrs["organization_id"]
            if not Organization.objects.filter(id=org_id, is_active=True, is_deleted=False).exists():
                raise serializers.ValidationError({ 
                    "organization_id": "Organization does not exist, is inactive or has been deleted."  
                })
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop("confirm_password", None)
        org_id = validated_data.pop("organization_id", None)
        role = validated_data.pop("role", None)
        password = validated_data.pop( "password", None )

        with transaction.atomic():
            if password:
                instance.set_password(password) 
                instance.save()
            instance = super().update(instance, validated_data)
            if org_id is not None or role is not None:
                membership = Membership.objects.filter( user=instance, is_active=True, is_deleted=False ).first()
                if membership:
                    if org_id is not None: 
                        membership.organization_id = org_id
                    if role is not None: 
                        membership.role = role
                    membership.save()
        return instance

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

class RegisterSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(write_only=True, max_length=255)
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
            "organization_name",
        ]
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        organization_name = validated_data.pop("organization_name")
        validated_data.pop("password2")

        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        organization = Organization.objects.create(name=organization_name)
        Membership.objects.create(
            user=user,
            organization=organization,
            role="owner",
        )

        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["first_name"] = getattr(user, "first_name", "")
        token["last_name"] = getattr(user, "last_name", "")
        return token

    def validate(self, attrs):

        data = super().validate(attrs)
        user = self.user

        membership = (
            Membership.objects.filter(
                user=user, 
                is_active=True, 
                is_deleted=False, 
                organization__is_active=True, 
                organization__is_deleted=False
            )
            .select_related("organization")
            .first()
        )

        data["user"] = {
            "id": user.id,
            "email": user.email,
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
        }

        data["membership"] = {
            "organization_id": membership.organization_id if membership else None,
            "organization_name": membership.organization.name if membership else None,
            "role": membership.role if membership else None,
        }

        return data