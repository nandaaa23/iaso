from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend  # type: ignore
from rest_framework import filters
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

from iaso.api.common import (
    ModelViewSet,
    DeletionFilterBackend,
    TimestampField,
)
from iaso.models import Entity, Instance, OrgUnit


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = "page_size"
    max_page_size = 1000


class MobileEntityAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instance
        fields = ["id", "form_id", "created_at", "updated_at", "org_unit", "json"]

    form_id = serializers.SerializerMethodField()
    id = serializers.CharField(read_only=True, source="uuid")

    created_at = TimestampField()
    updated_at = TimestampField()

    @staticmethod
    def get_form_id(instance):
        return instance.id


class MobileEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
            "defining_instance_id",
            "entity_type_id",
            "instances",
        ]

    created_at = TimestampField()
    updated_at = TimestampField()

    instances = serializers.SerializerMethodField()
    id = serializers.CharField(read_only=True, source="uuid")
    defining_instance_id = serializers.CharField(read_only=True, source="attributes.uuid")
    entity_type_id = serializers.CharField(read_only=True, source="entity_type.id")

    @staticmethod
    def get_instances(entity: Entity):
        res = []
        for instance in entity.non_deleted_instances:  # type: ignore
            res.append(MobileEntityAttributesSerializer(instance).data)

        return res

    @staticmethod
    def get_entity_type_name(obj: Entity):
        return obj.entity_type.name if obj.entity_type else None


class MobileEntityViewSet(ModelViewSet):
    """Entity API for mobile

    list: /api/mobile/entity

    pagination by default: 1000 entities

    It's possible to filter out entities with no activity before a certain date with the parameter limit_date

    details = /api/mobile/entity/id

    sample usage: /api/mobile/entity/?limit_date=2022-12-29&limit=1&page=1

    """

    results_key = "entities"
    remove_results_key_if_paginated = True
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend, DeletionFilterBackend]
    pagination_class = LargeResultsSetPagination

    def get_serializer_class(self):
        return MobileEntitySerializer

    def get_queryset(self):
        profile = self.request.user.iaso_profile
        orgunits = OrgUnit.objects.hierarchy(profile.org_units.all())
        # we give all entities having an instance linked to the one of the org units allowed for the current user
        queryset = Entity.objects.filter(account=profile.account).filter(instances__org_unit__in=orgunits)
        # we filter by last instance on the entity
        limit_date = self.request.query_params.get("limit_date", None)
        if limit_date:
            queryset = queryset.filter(instances__updated_at__gte=limit_date)
        p = Prefetch(
            "instances",
            queryset=Instance.objects.filter(deleted=False).exclude(file=""),
            to_attr="non_deleted_instances",
        )
        queryset = queryset.prefetch_related(p).prefetch_related("non_deleted_instances__form")
        return queryset
