from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from core import constants as const
from accounts.models import Membership, Organization, User
from accounts.serializers import CustomTokenObtainPairSerializer, MembershipSerializer, OrganizationSerializer, RegisterSerializer, UserCreateSerializer, UserSerializer
from accounts.utils import AccountUtils
from core.permissions import IsAuthenticatedAndOrgMember
from core.utils import CoreUtils
from core.pagination import DefaultPagination
from core.responses import error_response, success_response

# Create your views here.
class OrganizationListCreateView(generics.ListCreateAPIView):
    queryset = Organization.objects.filter(is_deleted=False)
    serializer_class = OrganizationSerializer
    permission_classes = [IsAdminUser]
    pagination_class = DefaultPagination

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            queryset = AccountUtils.organization_filter(queryset, request.query_params)
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            data = {
                "organiZation_data": serializer.data,
                "pagination_data": self.paginator.get_paginated_response(),                                                                                           
            }    
            return Response(success_response(data=data,message=const.ORGANIZATIONS_RETRIEVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)    
        except Exception as e:
            return Response(error_response(message=const.ORGANIZATIONS_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(error_response(message=const.VALIDATION_FAILURE,errors=serializer.errors),
                                status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            return Response(success_response(data={},message=const.ORGANIZATIONS_CREATED_SUCCESSFULLY),
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(error_response(message=const.ORGANIZATIONS_CREATION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.filter(is_deleted=False)
    serializer_class = OrganizationSerializer
    permission_classes = [IsAdminUser]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(success_response(data=serializer.data,message=const.ORGANIZATION_RETRIEVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.ORGANIZATION_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", True)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if not serializer.is_valid():
                return Response(error_response(message=const.VALIDATION_FAILURE,errors=serializer.errors),
                                status=status.HTTP_400_BAD_REQUEST)
            self.perform_update(serializer)
            return Response(success_response(data={},message=const.ORGANIZATION_UPDATED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.ORGANIZATIONS_UPDATION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_deleted = True
            instance.save(update_fields=["is_deleted"])
            return Response(success_response(data={},message=const.ORGANIZATION_DELETED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.ORGANIZATIONS_DELETION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.filter(is_deleted=False,is_superuser=False)
    serializer_class = UserCreateSerializer
    permission_classes = [IsAuthenticated,IsAuthenticatedAndOrgMember]
    pagination_class = DefaultPagination

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            queryset = AccountUtils.user_filter(queryset, request.query_params)
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            data = {
                "user_data": serializer.data,
                "pagination_data": self.paginator.get_paginated_response(),                                                                                           
            }
            return Response(success_response(data=data,message=const.USERS_RETRIEVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.USERS_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                formatted_errors = CoreUtils.format_validation_errors(serializer.errors)
                return Response(error_response(message=const.VALIDATION_FAILURE,errors=formatted_errors),
                                status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            return Response(success_response(data={},message=const.USER_CREATED_SUCCESSFULLY),
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(error_response(message=const.USER_CREATION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,IsAuthenticatedAndOrgMember]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(success_response(data=serializer.data,message=const.USER_RETRIEVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.USER_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", True)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if not serializer.is_valid():
                formatted_errors = CoreUtils.format_validation_errors(serializer.errors)
                return Response(error_response(message=const.VALIDATION_FAILURE,errors=formatted_errors),
                                status=status.HTTP_400_BAD_REQUEST)
            self.perform_update(serializer)
            return Response(success_response(data={},message=const.USER_UPDATED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.USER_UPDATION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_deleted = True
            instance.save(update_fields=["is_deleted"])
            return Response(success_response(data={},message=const.USER_DELETED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
                    return Response(error_response(message=const.USER_DELETION_FAILED,errors=str(e)),
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)   

class MembershipListCreateView(generics.ListCreateAPIView):
    queryset = Membership.objects.select_related("user", "organization")\
        .filter(is_deleted=False)
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            queryset = AccountUtils.membership_filter(queryset, request.query_params)
        
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
        
            data = {
                "membership_data": serializer.data,
                "pagination_data": self.paginator.get_paginated_response(),                                                                                           
            }
        
            return Response(success_response(data=data,message=const.MEMBERSHIPS_RETRIEVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response(error_response(message=const.MEMBERSHIPS_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                formatted_errors = CoreUtils.format_validation_errors(serializer.errors)
                return Response(error_response(message=const.VALIDATION_FAILURE,errors=formatted_errors),
                                status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            return Response(success_response(data={},message=const.MEMBERSHIPS_CREATED_SUCCESSFULLY),
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(error_response(message=const.MEMBERSHIPS_CREATION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MembershipDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Membership.objects.select_related("user", "organization")\
        .filter(is_deleted=False)
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(success_response(data=serializer.data,message=const.MEMBERSHIP_RETRIEVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.MEMBERSHIP_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", True)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if not serializer.is_valid():
                formatted_errors = CoreUtils.format_validation_errors(serializer.errors)
                return Response(error_response(message=const.VALIDATION_FAILURE,errors=formatted_errors),
                                status=status.HTTP_400_BAD_REQUEST)
            self.perform_update(serializer)
            return Response(success_response(data={},message=const.MEMBERSHIPS_UPDATED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.MEMBERSHIPS_UPDATION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_deleted = True
            instance.save(update_fields=["is_deleted"])
            return Response(success_response(data={},message=const.MEMBERSHIPS_DELETED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.MEMBERSHIPS_DELETION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                formatted_errors = CoreUtils.format_validation_errors(serializer.errors)
                return Response(error_response(message=const.VALIDATION_FAILURE,errors=formatted_errors),
                                status=status.HTTP_400_BAD_REQUEST)
            user = serializer.save()
            return Response(success_response(data={},message=const.REGISTER_SUCCESSFULL))
        except Exception as e:
            return Response(error_response(message=const.REGISTER_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                formatted_errors = CoreUtils.format_validation_errors(serializer.errors)
                return Response(error_response(message=const.VALIDATION_FAILURE,errors=formatted_errors),
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(success_response(data=serializer.validated_data,message=const.LOGIN_SUCCESS),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.LOGIN_FAILURE,errors=str(e)),
                            status=status.HTTP_400_BAD_REQUEST)         