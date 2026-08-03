from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from accounts.models import Organization
from clients.mixins import OrganizationAndCreatorScopedCreateMixin, OrganizationScopedCreateMixin
from clients.models import Client, Interaction, Lead
from clients.serializers import ClientActivitySummarySerializer, ClientSerializer, InteractionSerializer, InteractionTimelineGroupSerializer, LeadSerializer
from clients.utils import ClientUtils
from core.utils import CoreUtils
from core.pagination import DefaultPagination
from core import constants as const
from core.responses import error_response, success_response

# Create your views here.
# Api test is not done
class ClientViewSet(OrganizationScopedCreateMixin,viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
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
            client_data = {
                "data": serializer.data,
                "pagination_data": pagination,
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
            return Response(success_response(data={}, message=const.CLIENT_UPDATED_SUCCESSFULLY),
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
class LeadViewSet(OrganizationScopedCreateMixin,viewsets.ModelViewSet):
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    ordering_fields = ["created_at", "updated_at", "name", "next_follow_up_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "membership") and user.membership and user.membership.organization:
            queryset = Lead.objects.filter(organization=user.membership.organization)
        else:
            queryset = Lead.objects.none()

        return ClientUtils.lead_filter(queryset, self.request.query_params)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            pagination = self.paginator.get_paginated_response()
            lead_data = {
                "data": serializer.data,
                "pagination_data": pagination,
            }
            return Response(success_response(data=lead_data,message=const.LEADS_RETRIVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.LEADS_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(success_response(data=serializer.data, message=const.LEAD_RETRIVED_SUCCESSFULLY))
        except Exception as e:
            return Response(error_response(message=const.LEAD_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                formatted_errors = CoreUtils.format_validation_errors(serializer.errors)
                return Response(error_response(message=const.VALIDATION_FAILURE,errors=formatted_errors),
                                status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            return Response(success_response(data={}, message=const.LEAD_CREATED_SUCCESSFULLY),
                            status=status.HTTP_201_CREATED)
        except Exception as e:
                return Response(error_response(message=const.LEAD_CREATION_FAILED,errors=str(e)),
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
            return Response(success_response(data={}, message=const.LEAD_UPDATED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.LEAD_UPDATION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_delete = True
            instance.save(update_fields=["is_deleted"])
            return Response(success_response(data={},message=const.LEAD_DELETED_SUCCESSFULLY), 
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.LEAD_DELETION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InteractionViewSet(OrganizationAndCreatorScopedCreateMixin,viewsets.ModelViewSet):
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    ordering_fields = ["created_at", "updated_at", "occurred_at"]
    ordering = ["-occurred_at", "-created_at"]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "membership") and user.membership and user.membership.organization:
            queryset = Interaction.objects.filter(organization=user.membership.organization)
        else:
            queryset = Interaction.objects.none()

        return ClientUtils.interaction_filter(queryset, self.request.query_params)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            pagination = self.paginator.get_paginated_response()
            Interaction_data = {
                "data": serializer.data,
                "pagination_data": pagination,
            }
            return Response(success_response(data=Interaction_data,message=const.INTERACTIONS_RETRIVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.INTERACTIONS_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                formatted_errors = CoreUtils.format_validation_errors(serializer.errors)
                return Response(error_response(message=const.VALIDATION_FAILURE,errors=formatted_errors),
                                status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            return Response(success_response(data={}, message=const.INTERACTION_CREATED_SUCCESSFULLY),
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(error_response(message=const.INTERACTION_CREATION_FAILED,errors=str(e)),
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
            return Response(success_response(data={}, message=const.INTERACTION_UPDATED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.INTERACTION_UPDATION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_delete = True
            instance.save(update_fields=["is_deleted"])
            return Response(success_response(data={},message=const.INTERACTION_DELETED_SUCCESSFULLY), 
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.INTERACTION_DELETION_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"])
    def timeline(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            data = ClientUtils.timeline_group(queryset, request.query_params)
            serializer = InteractionTimelineGroupSerializer(data, many=True)
            return Response(success_response(data=serializer.data,message=const.TIMELINE_RETRIEVED_SUCCESSFULLY), 
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.TIMELINE_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ClientActivitySummaryView(APIView):
    def get(self, request, client_id):
        try:
            summary = ClientUtils.get_client_activity_summary(client_id)
            if not summary:
                return Response(error_response(message="Client not found.",errors={}),
                                status=status.HTTP_404_NOT_FOUND)
            serializer = ClientActivitySummarySerializer(summary)
            return Response(success_response(data=serializer.data, messae=const.ACTIVITY_SUMMARY_RETRIEVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
                return Response(error_response(message=const.ACTIVITY_SUMMARY_RETRIEVAL_FAILED,errors=str(e)),
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClientTimelineView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, client_id):
        try:
            client = get_object_or_404(Client, id=client_id)
            timeline = ClientUtils.build_client_timeline(client)
            paginator = DefaultPagination()
            page = paginator.paginate_queryset(timeline, request)
            pagination = paginator.get_paginated_response()

            client_timeline_data = {
                "client_id": client.id,
                "client_name": client.name,
                "company_name": client.company_name,
                "timeline": page,
                "pagination_data": pagination,
            }

            return Response(success_response(data=client_timeline_data,message=const.CLIENT_TIMELINE_RETRIEVED_SUCCESSFULLY),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.CLIENT_TIMELINE_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LeadSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, lead_id):
        try:
            lead = get_object_or_404(
                Lead.objects.select_related("client"),
                id=lead_id,
                is_deleted=False,
            )
            data = ClientUtils.lead_summary_data(lead)
            return Response(
                success_response(
                    data=data,message=const.LEAD_SUMMARY_RETRIEVED_SUCCESSFULLY
                ),
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(error_response(message=const.LEAD_SUMMARY_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClientsAttentionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            organization_id = request.query_params.get("organization")
            queryset = Client.objects.all()

            if organization_id:
                organization = get_object_or_404(Organization, id=organization_id)
                queryset = queryset.filter(organization=organization)
            else:
                queryset = queryset.filter(organization_id=request.user.organization_id)

            data = ClientUtils.clients_needing_attention(queryset, request.query_params)
            return Response(success_response(data=data,message=const.CLIENT_ATTENTION_RETRIEVED_SUCCESSFULLY),
                            status= status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.CLIENT_ATTENTION_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

class DailySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            organization = request.user.organization
            data = ClientUtils.daily_summary_data(organization)
            return Response(success_response(data=data,message=const.DAILY_SUMMARY_RETRIEVED_SUCCESSFULL),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.DAILY_SUMMARY_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

class LeadPrioritizationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            queryset = Lead.objects.filter(
                organization=request.user.organization,
                is_deleted=False,
            ).select_related("client")

            data = ClientUtils.lead_prioritization_data(queryset, request.query_params)
            return Response(success_response(data=data,message=const.LEAD_PRIORITY_RETRIEVED_SUCCESSFULL),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.LEAD_PRIORITY_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FollowUpSuggestionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            queryset = Lead.objects.filter(
                organization=request.user.organization,
                is_deleted=False,
            ).select_related("client")

            data = ClientUtils.follow_up_suggestions_data(queryset, request.query_params)
            return Response(success_response(data=data,message=const.FOLLOW_UP_RETRIEVED_SUCCESSFULL),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.FOLLOW_UP_RETRIEVAL_FAILED,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NaturalLanguageQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            query = request.data.get("query", "")
            data = ClientUtils.natural_language_query_data(query, request.user.organization)
            return Response(success_response(data=data,message=const.NATURAL_LANGUAGE_PROCESSED_SUCCESSFULL),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(error_response(message=const.NATURAL_LANGUAGE_PROCESSED_UNSUCCESSFULL,errors=str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
