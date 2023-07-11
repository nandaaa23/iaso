from datetime import date, datetime
from iaso.models.data_source import DataSource, SourceVersion
from iaso.models.data_store import JsonDataStore
from iaso.models.org_unit import OrgUnit, OrgUnitType
from iaso.models.project import Project
from iaso.test import APITestCase
import json
from iaso.models.base import Account, Group
from plugins.polio.api import (
    calculate_country_status,
    determine_status_for_district,
    get_data_for_round,
    get_latest_round_number,
    reduce_to_country_status,
)
from plugins.polio.models import Campaign, CampaignScope, Config, Round, RoundScope
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.contrib.gis.geos import Polygon, Point, MultiPolygon, GEOSGeometry


class PolioLqasAfroMapTestCase(APITestCase):
    authorized_user: User
    unauthorized_user: User
    account: Account
    projet: Project
    data_source: DataSource

    def setUp(cls) -> None:
        cls.account = Account.objects.create(name="Polio account")
        cls.authorized_user = cls.create_user_with_profile(username="authorized", account=cls.account)
        cls.unauthorized_user = cls.create_user_with_profile(username="unAuthorized", account=cls.account)
        cls.project = Project.objects.create(name="Polio", app_id="polio.rapid.outbreak.taskforce", account=cls.account)
        cls.data_source = DataSource.objects.create(name="Default source")
        cls.data_source.projects.add(cls.project)
        cls.data_source.save()
        cls.source_version = SourceVersion.objects.create(data_source=cls.data_source, number=1)
        cls.account.default_version = cls.source_version
        cls.account.save()
        cls.country = OrgUnitType.objects.create(name="Country", depth=1, category="COUNTRY")
        cls.country.projects.add(cls.project)
        cls.region = OrgUnitType.objects.create(name="Region", depth=2, category="REGION")
        cls.region.projects.add(cls.project)
        cls.district = OrgUnitType.objects.create(name="District", depth=3, category="DISTRICT")
        cls.district.projects.add(cls.project)
        cls.district.save()
        cls.region.sub_unit_types.add(cls.district)
        cls.region.save()
        cls.country.sub_unit_types.add(cls.region)
        cls.country.save()
        cls.country_1_geo_json = MultiPolygon(Polygon.from_bbox((1, 1, 5, 5)))
        cls.country_org_unit_1 = OrgUnit.objects.create(
            name="Country1",
            validation_status=OrgUnit.VALIDATION_VALID,
            source_ref="PvtAI4RUMkr",
            org_unit_type=cls.country,
            version=cls.source_version,
            simplified_geom=cls.country_1_geo_json,
        )
        cls.country_2_geo_json = MultiPolygon(Polygon.from_bbox((6, 6, 9, 9)))
        cls.country_org_unit_2 = OrgUnit.objects.create(
            name="Country2",
            validation_status=OrgUnit.VALIDATION_VALID,
            source_ref="PvtAI4RUMkr",
            org_unit_type=cls.country,
            version=cls.source_version,
            simplified_geom=cls.country_2_geo_json,
        )
        cls.region_org_unit_1 = OrgUnit.objects.create(
            name="Region1",
            validation_status=OrgUnit.VALIDATION_VALID,
            source_ref="PvtAI4RUMkr",
            org_unit_type=cls.region,
            version=cls.source_version,
            parent=cls.country_org_unit_1,
        )
        cls.region_org_unit_2 = OrgUnit.objects.create(
            name="Region2",
            validation_status=OrgUnit.VALIDATION_VALID,
            source_ref="PvtAI4RUMkr",
            org_unit_type=cls.region,
            version=cls.source_version,
            parent=cls.country_org_unit_2,
        )
        cls.district_1_geo_json = MultiPolygon(Polygon.from_bbox((2, 2, 3, 3)))
        cls.district_org_unit_1 = OrgUnit.objects.create(
            name="District1",
            validation_status=OrgUnit.VALIDATION_VALID,
            source_ref="PvtAI4RUMkr",
            org_unit_type=cls.district,
            version=cls.source_version,
            simplified_geom=cls.district_1_geo_json,
            parent=cls.region_org_unit_1,
        )
        cls.district_2_geo_json = MultiPolygon(Polygon.from_bbox((4, 4, 5, 5)))
        cls.district_org_unit_2 = OrgUnit.objects.create(
            name="District2",
            validation_status=OrgUnit.VALIDATION_VALID,
            source_ref="PvtAI4RUMkr",
            org_unit_type=cls.district,
            version=cls.source_version,
            simplified_geom=cls.district_2_geo_json,
            parent=cls.region_org_unit_1,
        )
        cls.district_3_geo_json = MultiPolygon(Polygon.from_bbox((6, 6, 7, 7)))
        cls.district_org_unit_3 = OrgUnit.objects.create(
            name="District3",
            validation_status=OrgUnit.VALIDATION_VALID,
            source_ref="PvtAI4RUMkr",
            org_unit_type=cls.district,
            version=cls.source_version,
            simplified_geom=cls.district_3_geo_json,
            parent=cls.region_org_unit_2,
        )
        cls.district_4_geo_json = MultiPolygon(Polygon.from_bbox((8, 8, 9, 9)))
        cls.district_org_unit_4 = OrgUnit.objects.create(
            name="District4",
            validation_status=OrgUnit.VALIDATION_VALID,
            source_ref="PvtAI4RUMkr",
            org_unit_type=cls.district,
            version=cls.source_version,
            simplified_geom=cls.district_4_geo_json,
            parent=cls.region_org_unit_2,
        )

        # country without campaign to test that api doesn't crash
        cls.country_3_geo_json = MultiPolygon(Polygon.from_bbox((11, 11, 15, 15)))
        cls.country_org_unit_3 = OrgUnit.objects.create(
            name="Country3",
            validation_status=OrgUnit.VALIDATION_VALID,
            source_ref="PvtAI4RUMkr",
            org_unit_type=cls.country,
            version=cls.source_version,
            simplified_geom=cls.country_3_geo_json,
        )

        # Campaign 1. Scope at campaign level
        cls.campaign_1 = Campaign.objects.create(
            obr_name="CAMPAIGN1",
            account=cls.account,
            separate_scopes_per_round=False,
            initial_org_unit=cls.country_org_unit_1,
        )
        cls.campaign1_scope_group = Group.objects.create(
            name="campaign1scope", domain="POLIO", source_version=cls.source_version
        )
        cls.campaign1_scope_group.org_units.add(cls.district_org_unit_1)
        cls.campaign1_scope_group.org_units.add(cls.district_org_unit_2)
        cls.campaign1_scope_group.save()
        cls.campaign_1_scope = CampaignScope.objects.create(
            campaign=cls.campaign_1, vaccine="bOPV", group=cls.campaign1_scope_group
        )
        cls.campaign1_round1 = Round.objects.create(
            number=1, started_at="2023-05-05", ended_at="2023-05-10", campaign=cls.campaign_1
        )
        cls.campaign1_round2 = Round.objects.create(
            number=2, started_at="2023-06-05", ended_at="2023-06-10", campaign=cls.campaign_1
        )

        # Campaign 2. Scope at round level
        cls.campaign_2 = Campaign.objects.create(
            obr_name="CAMPAIGN2",
            account=cls.account,
            separate_scopes_per_round=True,
            initial_org_unit=cls.country_org_unit_2,
        )

        cls.campaign2_round1 = Round.objects.create(
            number=1, started_at="2023-04-05", ended_at="2023-04-10", campaign=cls.campaign_2
        )
        cls.campaign2_round1_scope_org_units = Group.objects.create(
            name="campaign2round1scope", domain="POLIO", source_version=cls.source_version
        )
        cls.campaign2_round1_scope_org_units.org_units.add(cls.district_org_unit_3)
        cls.campaign2_round1_scope_org_units.save()
        cls.campaign2_round1_scope = RoundScope.objects.create(
            round=cls.campaign2_round1, vaccine="bOPV", group=cls.campaign2_round1_scope_org_units
        )

        cls.campaign2_round2 = Round.objects.create(
            number=2, started_at="2023-06-01", ended_at="2023-06-04", campaign=cls.campaign_2
        )
        cls.campaign2_round2_scope_org_units = Group.objects.create(
            name="campaign2round2scope", domain="POLIO", source_version=cls.source_version
        )
        cls.campaign2_round2_scope_org_units.org_units.add(cls.district_org_unit_4)
        cls.campaign2_round2_scope_org_units.save()
        cls.campaign2_round2_scope = RoundScope.objects.create(
            round=cls.campaign2_round2, vaccine="nOPV2", group=cls.campaign2_round2_scope_org_units
        )
        # Creating a campign with round ending at date.max to check if it is exluded from results
        cls.excluded_campaign = Campaign.objects.create(
            obr_name="EXCLUDEDCAMPAIGN",
            account=cls.account,
            separate_scopes_per_round=False,
            initial_org_unit=cls.country_org_unit_2,
        )
        cls.excluded_campaign_round1 = Round.objects.create(
            number=1, started_at="2100-04-05", ended_at=date.max, campaign=cls.excluded_campaign
        )
        cls.country1_data_store_content = {
            "stats": {
                cls.campaign_1.obr_name: {
                    "country_name": cls.country_org_unit_1.name,
                    "country_id": cls.country_org_unit_1.id,
                    "rounds": [
                        {
                            "number": 1,
                            "data": {
                                cls.district_org_unit_1.name: {
                                    "total_child_checked": 60,
                                    "total_child_fmd": 60,
                                    "district": cls.district_org_unit_1.id,
                                },
                                cls.district_org_unit_2.name: {
                                    "total_child_checked": 60,
                                    "total_child_fmd": 58,
                                    "district": cls.district_org_unit_2.id,
                                },
                            },
                        },
                        {
                            "number": 2,
                            "data": {
                                cls.district_org_unit_1.name: {
                                    "total_child_checked": 60,
                                    "total_child_fmd": 40,
                                    "district": cls.district_org_unit_1.id,
                                },
                                cls.district_org_unit_2.name: {
                                    "total_child_checked": 55,
                                    "total_child_fmd": 55,
                                    "district": cls.district_org_unit_2.id,
                                },
                            },
                        },
                    ],
                }
            }
        }
        cls.country2_data_store_content = {
            "stats": {
                cls.campaign_2.obr_name: {
                    "country_name": cls.country_org_unit_2.name,
                    "country_id": cls.country_org_unit_2.id,
                    "rounds": [
                        {
                            "number": 1,
                            "data": {
                                cls.district_org_unit_3.name: {
                                    "total_child_checked": 60,
                                    "total_child_fmd": 58,
                                    "district": cls.district_org_unit_3.id,
                                },
                                cls.district_org_unit_4.name: {
                                    "total_child_checked": 60,
                                    "total_child_fmd": 59,
                                    "district": cls.district_org_unit_4.id,
                                },
                            },
                        },
                        {
                            "number": 2,
                            "data": {
                                # TODO uncomment when code is able to filter out of scope districts
                                # cls.district_org_unit_3.name: {"total_child_checked": 60, "total_child_fmd": 60},
                                cls.district_org_unit_4.name: {
                                    "total_child_checked": 45,
                                    "total_child_fmd": 45,
                                    "district": cls.district_org_unit_4.id,
                                },
                            },
                        },
                    ],
                }
            }
        }
        cls.datastore_country1 = JsonDataStore.objects.create(
            content=cls.country1_data_store_content, slug=f"lqas_{cls.country_org_unit_1.id}", account=cls.account
        )
        cls.datastore_country2 = JsonDataStore.objects.create(
            content=cls.country2_data_store_content, slug=f"lqas_{cls.country_org_unit_2.id}", account=cls.account
        )
        cls.url_bounds = json.dumps({"_southWest": {"lat": 1, "lng": 1}, "_northEast": {"lat": 10, "lng": 10}})

    def test_authorized_user(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get("/api/polio/lqasmap/global/?category=lqas", accept="application/json")
        self.assertEqual(response.status_code, 200)

    def test_determine_status_for_district(self):
        district_data = self.country1_data_store_content["stats"][self.campaign_1.obr_name]["rounds"][0]["data"][
            self.district_org_unit_1.name
        ]
        self.assertEqual(determine_status_for_district(district_data), "1lqasOK")
        district_data = self.country2_data_store_content["stats"][self.campaign_2.obr_name]["rounds"][1]["data"][
            self.district_org_unit_4.name
        ]
        self.assertEqual(determine_status_for_district(district_data), "2lqasDisqualified")
        district_data = {"total_child_checked": 60, "total_child_fmd": 45}
        self.assertEqual(determine_status_for_district(district_data), "3lqasFail")

    def test_reduce_to_country_status(self):
        total = {}
        lqasPass = "1lqasOK"
        lqasDisqualified = "2lqasDisqualified"
        lqasFail = "3lqasFail"
        inScope = "inScope"
        total = reduce_to_country_status(total, lqasPass)
        self.assertEqual(total["total"], 1)
        self.assertEqual(total["passed"], 1)
        total = reduce_to_country_status(total, lqasPass)
        self.assertEqual(total["total"], 2)
        self.assertEqual(total["passed"], 2)
        total = reduce_to_country_status(total, lqasDisqualified)
        self.assertEqual(total["total"], 3)
        self.assertEqual(total["passed"], 2)
        total = reduce_to_country_status(total, lqasFail)
        self.assertEqual(total["total"], 4)
        self.assertEqual(total["passed"], 2)
        total = reduce_to_country_status(total, inScope)
        self.assertEqual(total["total"], 5)
        self.assertEqual(total["passed"], 2)

    def test_get_latest_round_number(self):
        country_data = self.country1_data_store_content["stats"][self.campaign_1.obr_name]
        number_found = get_latest_round_number(country_data)
        self.assertEqual(number_found, 2)
        country_data = {"rounds": []}
        number_found = get_latest_round_number(country_data)
        self.assertEqual(number_found, None)

    def test_get_data_for_round(self):
        country_data = self.country1_data_store_content["stats"][self.campaign_1.obr_name]
        data_for_round_1 = get_data_for_round(country_data, 1)
        self.assertEqual(data_for_round_1["number"], 1)
        self.assertEqual(
            data_for_round_1["data"][self.district_org_unit_1.name],
            {"total_child_checked": 60, "total_child_fmd": 60, "district": self.district_org_unit_1.id},
        )
        country_data = {"rounds": []}
        result = get_data_for_round(country_data, 1)
        self.assertEquals(result["data"], {})

    def test_calculate_country_status(self):
        country_data = self.country1_data_store_content["stats"][self.campaign_1.obr_name]
        scope = self.campaign_1.get_all_districts()
        round_number = 1
        result = calculate_country_status(country_data, scope, round_number)
        self.assertEquals(result, "1lqasOK")
        result = calculate_country_status({}, scope, round_number)
        self.assertEquals(result, "inScope")
        result = calculate_country_status({}, CampaignScope.objects.filter(campaign__obr_name="NOTHING"), round_number)
        self.assertEquals(result, "inScope")

    def test_is_round_over(self):
        # Accessing the round directly will cause the date to be of type str
        round = self.campaign_1.rounds.last()
        self.assertTrue(Round.is_round_over(round))
        round = self.excluded_campaign.rounds.last()
        self.assertFalse(Round.is_round_over(round))

    def test_lqas_global(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get("/api/polio/lqasmap/global/?category=lqas", accept="application/json")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        results = content["results"]
        # Test details of data for first country
        self.assertEquals(len(results), 3)
        results_for_first_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_1.id), None
        )
        self.assertTrue(results_for_first_country is not None)
        self.assertEquals(results_for_first_country["data"]["campaign"], self.campaign_1.obr_name)
        self.assertEquals(len(results_for_first_country["data"]["rounds"]), self.campaign_1.rounds.count())
        self.assertEquals(
            results_for_first_country["data"]["rounds"][0]["data"],
            self.country1_data_store_content["stats"][self.campaign_1.obr_name]["rounds"][0]["data"],
        )
        self.assertEquals(results_for_first_country["status"], "3lqasFail")

        # Test that second country is there as well
        results_for_second_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_2.id), None
        )
        self.assertTrue(results_for_second_country is not None)

        # Test third country. Without campaign data should be ull and status "inScope"
        results_for_third_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_3.id), None
        )
        self.assertTrue(results_for_third_country is not None)
        self.assertEquals(results_for_third_country["status"], "inScope")
        self.assertEquals(results_for_third_country["data"], {"country_name": self.country_org_unit_3.name})

    def test_lqas_global_round_filter(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get("/api/polio/lqasmap/global/?category=lqas&round=1", accept="application/json")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        results = content["results"]
        self.assertEquals(len(results), 3)
        results_for_first_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_1.id), None
        )
        self.assertTrue(results_for_first_country is not None)
        # Only status changes
        self.assertEquals(results_for_first_country["status"], "1lqasOK")
        results_for_second_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_2.id), None
        )
        self.assertTrue(results_for_second_country is not None)
        self.assertEquals(results_for_second_country["status"], "1lqasOK")

    def test_lqas_global_end_date_filter(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get("/api/polio/lqasmap/global/?category=lqas&endDate=04-06-2023", accept="application/json")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        results = content["results"]
        # Campaign 1 round 2 should fail, campaign2 round 2 should pass
        results_for_first_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_1.id), None
        )
        self.assertTrue(results_for_first_country is not None)
        self.assertEquals(results_for_first_country["status"], "inScope")

        results_for_second_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_2.id), None
        )
        self.assertTrue(results_for_second_country is not None)
        self.assertEquals(results_for_second_country["status"], "3lqasFail")

    def test_lqas_global_start_date_filter(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get("/api/polio/lqasmap/global/?category=lqas&startDate=07-06-2023", accept="application/json")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        results = content["results"]
        results_for_first_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_1.id), None
        )
        self.assertTrue(results_for_first_country is not None)
        self.assertEquals(results_for_first_country["status"], "inScope")

        results_for_second_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_2.id), None
        )
        self.assertTrue(results_for_second_country is not None)
        self.assertEquals(results_for_second_country["status"], "inScope")

    def test_lqas_global_round_with_start_date_filters(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get(
            "/api/polio/lqasmap/global/?category=lqas&startDate=04-05-2023&round=1", accept="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        results = content["results"]

        results_for_first_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_1.id), None
        )
        self.assertTrue(results_for_first_country is not None)
        self.assertEquals(results_for_first_country["status"], "1lqasOK")

        results_for_second_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_2.id), None
        )
        self.assertTrue(results_for_second_country is not None)
        self.assertEquals(results_for_second_country["status"], "inScope")

    def test_lqas_global_round_with_end_date_filters(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get(
            "/api/polio/lqasmap/global/?category=lqas&endDate=10-04-2023&round=1", accept="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        results = content["results"]

        results_for_first_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_1.id), None
        )
        self.assertTrue(results_for_first_country is not None)
        self.assertEquals(results_for_first_country["status"], "inScope")

        results_for_second_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_2.id), None
        )
        self.assertTrue(results_for_second_country is not None)
        self.assertEquals(results_for_second_country["status"], "1lqasOK")

    def lqas_global_start_and_end_date_filters(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get(
            "/api/polio/lqasmap/global/?category=lqas&endDate=10-04-2023&startDate=06-04-2023",
            accept="application/json",
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        results = content["results"]
        results_for_first_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_1.id), None
        )
        self.assertTrue(results_for_first_country is not None)
        self.assertEquals(results_for_first_country["status"], "inScope")

        results_for_second_country = next(
            (country_data for country_data in results if country_data["id"] == self.country_org_unit_2.id), None
        )
        self.assertTrue(results_for_second_country is not None)
        self.assertEquals(results_for_second_country["status"], "inScope")

    def test_lqas_zoomed_in(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get(
            f"/api/polio/lqasmap/zoomin/?category=lqas&bounds={self.url_bounds}", accept="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        results = content["results"]
        self.assertEquals(len(results), 3)
        results_for_first_district = next(
            (district_data for district_data in results if district_data["id"] == self.district_org_unit_1.id), None
        )
        self.assertTrue(results_for_first_district is not None)
        self.assertEquals(results_for_first_district["data"]["campaign"], self.campaign_1.obr_name)
        self.assertEquals(
            results_for_first_district["data"]["district_name"],
            self.district_org_unit_1.name,
        )
        self.assertEquals(results_for_first_district["status"], "3lqasFail")

        results_for_second_district = next(
            (district_data for district_data in results if district_data["id"] == self.district_org_unit_2.id), None
        )
        self.assertTrue(results_for_second_district is not None)
        self.assertEquals(results_for_second_district["data"]["campaign"], self.campaign_1.obr_name)
        self.assertEquals(
            results_for_second_district["data"]["district_name"],
            self.district_org_unit_2.name,
        )
        self.assertEquals(results_for_second_district["status"], "3lqasFail")

        # Third district has no data for latest round, ie round 2
        results_for_third_district = next(
            (district_data for district_data in results if district_data["id"] == self.district_org_unit_3.id), None
        )
        self.assertTrue(results_for_third_district is None)

        results_for_fourth_district = next(
            (district_data for district_data in results if district_data["id"] == self.district_org_unit_4.id), None
        )
        self.assertTrue(results_for_fourth_district is not None)
        self.assertEquals(results_for_fourth_district["data"]["campaign"], self.campaign_2.obr_name)
        self.assertEquals(
            results_for_fourth_district["data"]["district_name"],
            self.district_org_unit_4.name,
        )
        self.assertEquals(results_for_fourth_district["status"], "2lqasDisqualified")

    def test_lqas_zoomin_round_filter(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get(
            f"/api/polio/lqasmap/zoomin/?category=lqas&round=1&bounds={self.url_bounds}", accept="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        results = content["results"]
        self.assertEquals(len(results), 3)
        results_for_first_district = next(
            (district_data for district_data in results if district_data["id"] == self.district_org_unit_1.id), None
        )
        self.assertTrue(results_for_first_district is not None)
        self.assertEquals(results_for_first_district["data"]["campaign"], self.campaign_1.obr_name)
        self.assertEquals(
            results_for_first_district["data"]["district_name"],
            self.district_org_unit_1.name,
        )
        self.assertEquals(results_for_first_district["status"], "1lqasOK")

        results_for_second_district = next(
            (district_data for district_data in results if district_data["id"] == self.district_org_unit_2.id), None
        )
        self.assertTrue(results_for_second_district is not None)
        self.assertEquals(results_for_second_district["data"]["campaign"], self.campaign_1.obr_name)
        self.assertEquals(
            results_for_second_district["data"]["district_name"],
            self.district_org_unit_2.name,
        )
        self.assertEquals(results_for_second_district["status"], "1lqasOK")

        results_for_third_district = next(
            (district_data for district_data in results if district_data["id"] == self.district_org_unit_3.id), None
        )
        self.assertTrue(results_for_third_district is not None)
        self.assertEquals(results_for_third_district["data"]["campaign"], self.campaign_2.obr_name)
        self.assertEquals(
            results_for_third_district["data"]["district_name"],
            self.district_org_unit_3.name,
        )
        self.assertEquals(results_for_third_district["status"], "1lqasOK")

        # fourth district is out of scope for round 1
        results_for_fourth_district = next(
            (district_data for district_data in results if district_data["id"] == self.district_org_unit_4.id), None
        )
        self.assertTrue(results_for_fourth_district is None)

    def test_lqas_zoomedin_end_date_filter(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get(
            f"/api/polio/lqasmap/zoomin/?category=lqas&bounds={self.url_bounds}&endDate=04-06-2023",
            accept="application/json",
        )

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        results = content["results"]
        self.assertEquals(len(results), 1)
        self.assertEquals(results[0]["data"]["campaign"], self.campaign_2.obr_name)
        self.assertEquals(results[0]["data"]["district_name"], self.district_org_unit_4.name)
        self.assertEquals(results[0]["status"], "3lqasFail")

    def test_lqas_zoomedin_start_date_filter(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get(
            f"/api/polio/lqasmap/zoomin/?category=lqas&bounds={self.url_bounds}&startDate=07-06-2023",
            accept="application/json",
        )

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        results = content["results"]
        # There's no round date that starts after 07-06-2023
        self.assertEquals(len(results), 0)

    def test_lqas_zoomin_round_with_start_date_filters(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get(
            f"/api/polio/lqasmap/zoomin/?category=lqas&bounds={self.url_bounds}&startDate=04-05-2023&round=1",
            accept="application/json",
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        results = content["results"]
        self.assertEquals(len(results), 2)
        self.assertEquals(results[0]["data"]["campaign"], self.campaign_1.obr_name)
        self.assertEquals(results[0]["data"]["district_name"], self.district_org_unit_1.name)
        self.assertEquals(results[0]["status"], "1lqasOK")
        self.assertEquals(results[1]["data"]["campaign"], self.campaign_1.obr_name)
        self.assertEquals(results[1]["data"]["district_name"], self.district_org_unit_2.name)
        self.assertEquals(results[1]["status"], "1lqasOK")

    def test_lqas_zoomin_round_with_end_date_filters(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get(
            f"/api/polio/lqasmap/zoomin/?category=lqas&bounds={self.url_bounds}&endDate=10-04-2023&round=1",
            accept="application/json",
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        results = content["results"]
        self.assertEquals(len(results), 1)
        self.assertEquals(results[0]["data"]["campaign"], self.campaign_2.obr_name)
        self.assertEquals(results[0]["data"]["district_name"], self.district_org_unit_3.name)
        self.assertEquals(results[0]["status"], "1lqasOK")

    def test_lqas_zoomin_start_and_end_date_filters(self):
        c = APIClient()
        c.force_authenticate(user=self.authorized_user)
        response = c.get(
            f"/api/polio/lqasmap/zoomin/?category=lqas&bounds={self.url_bounds}&endDate=10-04-2023&startDate=06-04-2023",
            accept="application/json",
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        results = content["results"]
        self.assertEquals(len(results), 0)
