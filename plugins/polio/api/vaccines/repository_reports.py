"""API endpoints and serializers for vaccine repository reports."""

from datetime import datetime, timedelta
from django.db.models import OuterRef, Subquery, Q, Value, Case, When, CharField, Exists
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, permissions, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from iaso.api.common import Paginator
from plugins.polio.models import VaccineStock, DestructionReport, IncidentReport


class VaccineReportingFilterBackend(filters.BaseFilterBackend):
    """Filter backend for vaccine reporting that handles country and file type filtering."""

    def filter_queryset(self, request, queryset, view):
        # Filter by vaccine name (single)
        vaccine_name = request.query_params.get("vaccine_name", None)
        if vaccine_name:
            queryset = queryset.filter(vaccine=vaccine_name)

        # Filter by country block
        country_block = request.query_params.get("country_block", None)
        if country_block:
            try:
                country_block_ids = [int(id) for id in country_block.split(",")]
                queryset = queryset.filter(country__groups__in=country_block_ids)
            except ValueError:
                raise ValidationError("country_block must be a comma-separated list of integers")

        # Filter by country (multi)
        countries = request.query_params.get("countries", None)
        if countries:
            try:
                country_ids = [int(id) for id in countries.split(",")]
                queryset = queryset.filter(country__id__in=country_ids)
            except ValueError:
                raise ValidationError("countries must be a comma-separated list of integers")

        # Filter by file type
        file_type = request.query_params.get("file_type", None)
        if file_type:
            file_type = file_type.upper()
            if file_type == "IR":
                queryset = queryset.filter(incidentreport__isnull=False)
            elif file_type == "DR":
                queryset = queryset.filter(destructionreport__isnull=False)

        return queryset.distinct()


class VaccineRepositoryReportSerializer(serializers.Serializer):
    country_name = serializers.CharField(source="country.name")
    country_id = serializers.IntegerField(source="country.id")
    vaccine = serializers.CharField()
    incident_report_data = serializers.SerializerMethodField()
    destruction_report_data = serializers.SerializerMethodField()

    def get_incident_report_data(self, obj):
        incident_reports = IncidentReport.objects.filter(vaccine_stock=obj)
        return [
            {
                "date": ir.date_of_incident_report,
                "file": ir.document.url if ir.document else None,
            }
            for ir in incident_reports
        ]

    def get_destruction_report_data(self, obj):
        destruction_reports = DestructionReport.objects.filter(vaccine_stock=obj)
        return [
            {
                "date": dr.destruction_report_date,
                "file": dr.document.url if dr.document else None,
            }
            for dr in destruction_reports
        ]


class VaccineRepositoryReportsViewSet(GenericViewSet, ListModelMixin):
    """ViewSet for retrieving vaccine repository reports data."""

    serializer_class = VaccineRepositoryReportSerializer
    pagination_class = Paginator
    filter_backends = [OrderingFilter, SearchFilter, VaccineReportingFilterBackend]
    ordering_fields = ["country__name", "vaccine"]
    ordering = ["country__name"]
    search_fields = ["country__name", "vaccine"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    default_page_size = 10

    def get_queryset(self):
        """Get the queryset for VaccineStock objects."""
        return (
            VaccineStock.objects.select_related("country")
            .prefetch_related("incidentreport_set", "destructionreport_set")
            .filter(Q(incidentreport__isnull=False) | Q(destructionreport__isnull=False))
            .distinct()
        )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "file_type",
                openapi.IN_QUERY,
                description="Filter by file type (IR, DR)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "country_block",
                openapi.IN_QUERY,
                description="Filter by country block (comma separated list of org unit group ids)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "countries",
                openapi.IN_QUERY,
                description="Filter by countries (comma separated list of country ids)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "vaccine_name",
                openapi.IN_QUERY,
                description="Filter by vaccine name",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Vaccine Reports Repository

        Return a paginated list of vaccine stocks with their associated incident and destruction reports.
        """
        return super().list(request, *args, **kwargs)
