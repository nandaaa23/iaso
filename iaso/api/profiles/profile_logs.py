from hat.audit.models import Modification
from iaso.api.common import (
    HasPermission,
    ModelViewSet,
    parse_comma_separated_numeric_values,
)
from hat.menupermissions import models as permission
from rest_framework import serializers, filters
import django_filters
from django.contrib.auth.models import User
from iaso.models.base import Profile
from django.utils.translation import gettext_lazy as _
from django.db.models.query import QuerySet
from django.db.models import Q
from django.conf import settings
from iaso.api.common import Paginator
from iaso.models.org_unit import OrgUnit

from django.db.models import F, Func, Value, CharField, JSONField, IntegerField
from django.db.models.functions import Cast


class ProfileLogsListPagination(Paginator):
    page_size = 20


class ProfileLogsListFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Modification
        fields = []

    # using CharFilter as NumberFilter errors for some reason
    user_ids = django_filters.CharFilter(method="filter_user_ids", label=_("User IDs"))
    modified_by = django_filters.CharFilter(method="filter_modified_by", label=_("Modified by"))
    org_unit_id = django_filters.CharFilter(method="filter_org_unit_id", label=_("Location"))
    created_at = django_filters.DateFromToRangeFilter()

    def filter_user_ids(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        # object_id is tored as string in Modification
        user_ids = [user_id for user_id in parse_comma_separated_numeric_values(value, name)]
        # There's always a new_value, even on delete
        return queryset.filter(new_value__0__fields__user__in=user_ids)

    def filter_modified_by(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        # object_id is stored as string in Modification
        user_ids = parse_comma_separated_numeric_values(value, name)
        return queryset.filter(user__id__in=user_ids)

    def filter_org_unit_id(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        return queryset.filter(
            Q(past_value__0__fields__org_units__contains=int(value))
            | Q(new_value__0__fields__org_units__contains=int(value))
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields["created_at"].fields[0].input_formats = settings.API_DATE_INPUT_FORMATS
        self.form.fields["created_at"].fields[-1].input_formats = settings.API_DATE_INPUT_FORMATS


class NestedOrgUnitForListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgUnit
        fields = ["id", "name"]


class NestedUserForListSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["user_id", "username", "first_name", "last_name"]

    def get_user_id(self, user):
        return user.id


class ProfileLogListSerializer(serializers.ModelSerializer):
    # The user who created the Log
    modified_by = serializers.SerializerMethodField(read_only=True)
    # The user in the content of the Log
    user = serializers.SerializerMethodField(read_only=True)
    past_location = serializers.SerializerMethodField(read_only=True)
    new_location = serializers.SerializerMethodField(read_only=True)
    fields_modified = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Modification
        fields = ["id", "user", "modified_by", "past_location", "new_location", "created_at", "fields_modified"]

    def get_modified_by(self, modification):
        return {"id": modification.user.iaso_profile.id, **NestedUserForListSerializer(modification.user).data}

    def get_user(self, modification):
        # Use .first() because profiles can be hard deleted
        profile = Profile.objects.select_related("user").filter(pk=int(modification.object_id)).first()
        if profile is not None:
            return {"id": profile.id, **NestedUserForListSerializer(profile.user).data}
        return {}

    def get_past_location(self, modification):
        past_value = modification.past_value
        if not past_value:
            return []
        org_unit_ids = past_value[0]["fields"].get("org_units", None)
        if not org_unit_ids:
            return []
        org_units = OrgUnit.objects.filter(pk__in=org_unit_ids)
        serializer = NestedOrgUnitForListSerializer(org_units, many=True)
        return serializer.data

    def get_new_location(self, modification):
        new_value = modification.new_value
        if not new_value:
            return []
        org_unit_ids = new_value[0]["fields"].get("org_units", None)
        if not org_unit_ids:
            return []
        org_units = OrgUnit.objects.filter(pk__in=org_unit_ids)
        serializer = NestedOrgUnitForListSerializer(org_units, many=True)

        return serializer.data

    def get_fields_modified(self, modification):
        diffs = modification.field_diffs()
        if not modification.past_value:
            return ["new_user_created"]
        # password updated will always be in the added dict because it's never present on past value
        password_updated = diffs["added"].get("password_updated", None)
        if password_updated:
            if password_updated.get("after", False):
                diffs["added"]["password"] = password_updated
            del diffs["added"]["password_updated"]

        added = list(diffs["added"].keys())
        removed = list(diffs["removed"].keys())
        modified = list(diffs["modified"].keys())
        result = list(set(removed + added + modified))
        result.sort()
        # filter user and account because these can't be modified
        return [key for key in result if key != "user" and key != "account"]


class ProfileLogRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modification
        fields = ["id", "created_at", "user", "source", "new_value", "past_value", "object_id", "content_type"]


class ProfileLogsViewset(ModelViewSet):
    permission_classes = [HasPermission(permission.USERS_ADMIN)]
    filter_backends = [
        filters.OrderingFilter,
        django_filters.rest_framework.DjangoFilterBackend,
    ]
    filterset_class = ProfileLogsListFilter
    pagination_class = ProfileLogsListPagination
    ordering_fields = ["created_at"]

    http_method_names = ["get"]

    def get_queryset(self):
        order = self.request.query_params.get("order", "-created_at")
        request_user = self.request.user

        queryset = (
            Modification.objects.select_related("user")
            .filter(content_type__app_label="iaso")
            .filter(content_type__model="profile")
            .filter(user__iaso_profile__account=request_user.iaso_profile.account)
        )

        if "created_at" in order:
            queryset = queryset.order_by(order)
        if order == "modified_by":
            queryset = queryset.order_by("user__username")
        if order == "-modified_by":
            queryset = queryset.order_by("-user__username")
        if order == "user":
            queryset = queryset.order_by("new_value__0__fields__user__username")
        if order == "-user":
            queryset = queryset.order_by("-new_value__0__fields__user__username")

        return queryset

    def get_serializer_class(self):
        if hasattr(self, "action") and self.action == "list":
            return ProfileLogListSerializer
        return super().get_serializer_class()
