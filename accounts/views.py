from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from core import constants as const
from accounts.models import User
from accounts.serializers import UserSerializer
from accounts.utils import AccountUtils
from core.pagination import DefaultPagination
from core.responses import error_response, success_response

# Create your views here.
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.filter(is_active=True).order_by("email")
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            queryset = AccountUtils.user_filter(queryset, request.query_params)

            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)

            user_data = {
                "user_data": serializer.data,
                "pagination_data": self.paginator.get_paginated_response(),                                                                                           
            }

            return Response(
                success_response(
                    data=user_data,
                    message=const.USERS_RETRIEVED_SUCCESSFULLY
                ),
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                error_response(
                    message=const.USERS_RETRIEVAL_FAILED,
                    errors=str(e)
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(error_response(message=const.VALIDATION_FAILURE,errors=serializer.errors),
                                status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            return Response(success_response(data={},message=const.USERS_CREATED_SUCCESSFULLY),
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(error_response(message=const.USER_CREATION_FAILED,errors=str(e)),
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

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
                            return Response(error_response(message=const.VALIDATION_FAILURE,errors=serializer.errors),
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
            instance.is_active = False
            instance.save(update_fields=["is_active"])
            return Response(success_response(data={},message=const.USER_DELETED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
                    return Response(error_response(message=const.USER_DELETION_FAILED,errors=str(e)),
                                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)


