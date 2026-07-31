from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from clients.models import Client
from clients.serializers import ClientSerializer
from clients.utils import ClientUtils
from core.utils import CoreUtils
from core.pagination import DefaultPagination
from core import constants as const
from core.responses import error_response, success_response

# Create your views here.
class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "owner"]
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "membership") and user.membership and user.membership.organization:
            queryset = Client.objects.filter(organization=user.membership.organization)
        else:
            queryset = Client.objects.none()
        return ClientUtils.client_filter(queryset, self.request.query_params)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            pagination = self.paginator.get_paginated_response()
            client_data={
                **pagination,
                "data": serializer.data,
            }
            return Response(success_response(data=client_data,message=const.CLIENTS_RETRIVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.CLIENTS_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(success_response(data=serializer.data, message=const.CLIENT_RETRIVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.CLIENT_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                formatted_errors = CoreUtils.format_validation_errors(serializer.errors)
                return Response(error_response(message=const.VALIDATION_FAILURE,errors=formatted_errors),
                                status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            return Response(success_response(data={}, message=const.CLIENT_CREATED_SUCCESSFULLY),
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(error_response(message=const.CLIENT_CREATION_FAILED,errors=str(e)),
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
            return Response(success_response(data=serializer.data, message=const.CLIENT_UPDATED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.CLIENT_UPDATION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_deleted = True
            instance.save(update_fields=["is_deleted"])
            return Response(success_response(data={},message=const.CLIENT_DELETED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.CLIENT_DELETION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


                  