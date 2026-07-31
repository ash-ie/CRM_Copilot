from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.pagination import DefaultPagination
from core.permissions import IsOrganizationScoped
from core.responses import error_response, success_response
from core import constants as const
from core.utils import CoreUtils
from tasks.mixins import OrganizationAndCreatorScopedCreateMixin
from tasks.models import Note, Task
from tasks.serializers import NoteSerializer, TaskSerializer
from tasks.utils import TaskUtils

# Create your views here.
class TaskViewSet(OrganizationAndCreatorScopedCreateMixin,viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated,IsOrganizationScoped]
    pagination_class = DefaultPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(organization=user.organization).select_related(
            "organization",
            "assigned_to",
            "created_by",
            "client",
            "lead",
        )
        return TaskUtils.task_filter(queryset, self.request.query_params)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(success_response(data=serializer.data,message=const.TASKS_LISTS_RETRIEVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.TASKS_LISTS_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(success_response(data=serializer.data,message=const.TASKS_RETRIEVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.TASKS_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                formatted_errors = CoreUtils.format_validation_errors(serializer.errors)
                return Response(error_response(message=const.VALIDATION_FAILURE,errors=formatted_errors),
                                status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            return Response(success_response(data={}, message=const.TASKS_CREATED_SUCCESSFULLY),
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(error_response(message=const.TASKS_CREATION_FAILED,errors=str(e)),
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
            return Response(success_response(data={}, message=const.TASKS_UPDATED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.TASKS_UPDATION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_deleted = True
            instance.save(update_fields=["is_deleted"])
            return Response(success_response(data={},message=const.TASKS_DELETED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.TASKS_DELETION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NoteViewSet(OrganizationAndCreatorScopedCreateMixin, viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, IsOrganizationScoped]
    pagination_class = DefaultPagination

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "membership") and user.membership and user.membership.organization:
            queryset = Note.objects.filter(organization=user.membership.organization).select_related(
                "organization",
                "created_by",
                "client",
                "lead",
            )
        else:
            queryset = Note.objects.none()

        return TaskUtils.note_filter(queryset, self.request.query_params)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(success_response(data=serializer.data,message=const.NOTES_RETRIEVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.NOTES_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(success_response(data=serializer.data,message=const.NOTE_RETRIEVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.NOTE_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                formatted_errors = CoreUtils.format_validation_errors(serializer.errors)
                return Response(error_response(message=const.VALIDATION_FAILURE,errors=formatted_errors),
                                status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            return Response(success_response(data={}, message=const.NOTE_CREATED_SUCCESSFULLY),
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(error_response(message=const.NOTE_CREATION_FAILED,errors=str(e)),
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
            return Response(success_response(data={}, message=const.NOTE_UPDATED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.NOTE_UPDATION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_deleted = True
            instance.save(update_fields=["is_deleted"])
            return Response(success_response(data={},message=const.NOTE_DELETED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.NOTE_DELETION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)    