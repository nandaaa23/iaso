from decimal import Decimal

from django.contrib.gis.geos import Point

from iaso import models as m
from iaso.test import TestCase


class OrgUnitChangeRequestModelTestCase(TestCase):
    """
    Test OrgUnitChangeRequest.
    """

    @classmethod
    def setUpTestData(cls):
        cls.org_unit_type = m.OrgUnitType.objects.create(name="Org unit type")
        cls.org_unit = m.OrgUnit.objects.create(org_unit_type=cls.org_unit_type)

        cls.form = m.Form.objects.create(name="Vaccine form")
        cls.instance = m.Instance.objects.create(form=cls.form, org_unit=cls.org_unit)

        cls.account = m.Account.objects.create(name="Account")
        cls.user = cls.create_user_with_profile(username="user", account=cls.account)

    def test_create(self):
        new_org_unit_type = m.OrgUnitType.objects.create(name="New org unit type")
        new_parent = m.OrgUnit.objects.create(org_unit_type=new_org_unit_type)

        kwargs = {
            "org_unit": self.org_unit,
            "created_by": self.user,
            "parent": new_parent,
            "name": "New name",
            "org_unit_type": new_org_unit_type,
            "location": Point(-2.4747713, 47.3358576, 1.3358576),
            "accuracy": "0.11",
            "approved_fields": ["parent", "name", "org_unit_type", "groups", "location", "instances"],
        }
        org_unit_change_request = m.OrgUnitChangeRequest(**kwargs)

        # TODO:
        # "groups": [],
        # "instances": [],

        org_unit_change_request.full_clean()
        org_unit_change_request.save()
        org_unit_change_request.refresh_from_db()

        self.assertEqual(org_unit_change_request.org_unit, self.org_unit)
        self.assertEqual(org_unit_change_request.created_by, self.user)
        self.assertEqual(org_unit_change_request.parent, new_parent)
        self.assertEqual(org_unit_change_request.name, "New name")
        self.assertEqual(org_unit_change_request.org_unit_type, new_org_unit_type)
        self.assertCountEqual(org_unit_change_request.location, kwargs["location"])
        self.assertEqual(org_unit_change_request.accuracy, Decimal("0.11"))
        self.assertCountEqual(org_unit_change_request.approved_fields, kwargs["approved_fields"])
