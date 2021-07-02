from typing import Optional, Dict, Any, List

from iaso.models import (
    OrgUnit,
    OrgUnitType,
    DataSource,
    SourceVersion,
    Group,
    GroupSet,
    Task,
)
from beanstalk_worker import task_decorator
from django.contrib.gis.geos import Point, MultiPolygon, Polygon

import logging
import json
import time

try:  # only in 3.8
    from typing import TypedDict
except ImportError:
    TypedDict = type

logger = logging.getLogger(__name__)


def get_api(options):
    from dhis2 import Api

    api = Api(options.get("dhis2_url"), options.get("dhis2_user"), options.get("dhis2_password"))

    return api


def fetch_orgunits(options):
    api = get_api(options)
    orgunits = []

    for page in api.get_paged(
        "organisationUnits",
        page_size=options.get("page_size", 500),
        params={"fields": "id,name,path,coordinates,geometry,parent,organisationUnitGroups[id,name]"},
    ):
        orgunits.extend(page["organisationUnits"])
        logger.info(
            f'fetched {page["pager"]["page"]}/{page["pager"]["pageCount"]} '
            f'({len(orgunits)}/{page["pager"]["total"]} records)'
        )

    # sorting orgunit according to their path ensure the parent are before the children
    orgunits_sorted = sorted(orgunits, key=lambda ou: ou["path"])
    return orgunits_sorted


def map_parent(row, org_unit, unit_dict):
    if "parent" in row:
        parent_id = row["parent"]["id"]

        if parent_id not in unit_dict:
            raise Exception(f"Parent nof found for {org_unit.source_ref} {parent_id}. details : {org_unit} {row}")
        org_unit.parent = unit_dict[parent_id]


def row_without_coordinates(row):
    """for debug print"""
    return {i: row[i] for i in row if i != "coordinates" and i != "geometry"}


def find_org_unit_type(groups, type_dict):
    for group in groups:
        if group["name"] in type_dict:
            return type_dict[group["name"]]


class DhisGroup(TypedDict):
    id: str


class DhisGeom(TypedDict):
    """Seems to be a GeoJson"""

    type: str
    coordinates: list


class DhisOrgunit(TypedDict):
    id: str
    name: str
    parent: Optional[str]
    coordinates: Optional[str]
    geometry: Optional[DhisGeom]
    organisationUnitGroups: List[DhisGroup]


def orgunit_from_row(row: DhisOrgunit, source, type_dict, unit_dict, group_dict, unknown_unit_type, validate, version):
    org_unit = OrgUnit()
    org_unit.name = row["name"].strip()
    org_unit.sub_source = source.name
    org_unit.version = version
    org_unit.source_ref = row["id"].strip()
    org_unit.validation_status = OrgUnit.VALIDATION_VALID if validate else OrgUnit.VALIDATION_NEW
    org_unit.org_unit_type = find_org_unit_type(row["organisationUnitGroups"], type_dict)
    if not org_unit.org_unit_type:
        logger.warning("unknown type for ", org_unit)
        org_unit.org_unit_type = unknown_unit_type
    map_parent(row, org_unit, unit_dict)
    # if dhis2 version < 2.32
    map_coordinates(row, org_unit)
    # if dhis2 version >= 2.32
    map_geometry(row, org_unit)
    org_unit.save()

    # org_unit should be saved before filling the groups
    for ougroup in row["organisationUnitGroups"]:
        group = get_or_create_group(ougroup, group_dict, version)
        group.org_units.add(org_unit)
    return org_unit


def guess_feature_type(coordinates):
    if coordinates is None:
        return None
    if coordinates.startswith("[[[["):
        return "MULTI_POLYGON"
    if coordinates.startswith("[[["):
        return "POLYGON"
    if coordinates.startswith("["):
        return "POINT"
    return None


def map_coordinates(row, org_unit):
    if "coordinates" in row:
        coordinates = row["coordinates"]
        feature_type = guess_feature_type(row["coordinates"])

        try:
            if feature_type == "POINT" and coordinates:
                x, y = json.loads(coordinates)
                # No altitude in DHIS2, but mandatory in Iaso
                pnt = Point(float(x), float(y), 0)
                if abs(pnt.x) < 180 and abs(pnt.y) < 90:
                    org_unit.location = pnt
                else:
                    logger.warning("Invalid coordinates found in row", coordinates, row)
            if feature_type == "POLYGON" and coordinates:
                j = json.loads(coordinates)
                org_unit.geom = MultiPolygon(Polygon(j[0]))
            if feature_type == "MULTI_POLYGON" and coordinates:
                j = json.loads(coordinates)
                org_unit.geom = MultiPolygon(*[Polygon(i) for i in j[0]])
        except Exception as bad_polygon:
            logger.debug("failed at importing ", feature_type, coordinates, bad_polygon, row)

        org_unit.simplified_geom = org_unit.geom


def map_geometry(row, org_unit):
    if "geometry" in row:
        coordinates = row["geometry"]["coordinates"]
        feature_type = row["geometry"]["type"]

        try:
            if feature_type == "Point" and coordinates:
                # No altitude in DHIS2, but mandatory in Iaso
                org_unit.location = Point(coordinates[0], coordinates[1], 0)
            elif feature_type == "Polygon" and coordinates:
                org_unit.geom = MultiPolygon(Polygon(*coordinates))
                org_unit.simplified_geom = org_unit.geom
            elif feature_type == "MultiPolygon" and coordinates:
                org_unit.geom = MultiPolygon([Polygon(*p) for p in coordinates])
                org_unit.simplified_geom = org_unit.geom
            else:
                logger.warning("Unsupported feature tye")

        except Exception as bad_coord:
            logger.error("failed at importing ", feature_type, coordinates, bad_coord, row)


def get_or_create_group(dhis2_group, group_dict, source_version):
    name = dhis2_group["name"]
    if name in group_dict:
        return group_dict[name]

    group, created = Group.objects.get_or_create(name=name, source_version=source_version, source_ref=dhis2_group["id"])
    logger.debug("group, created ", group, created)
    group_dict[name] = group
    return group


def get_group_set(dhis2_group_set, group_set_dict, source_version):
    name = dhis2_group_set["name"]
    group_set = group_set_dict.get(name, None)
    if group_set is None:
        group_set, created = GroupSet.objects.get_or_create(
            name=name, source_version=source_version, source_ref=dhis2_group_set["id"]
        )
        logger.debug(f"GroupSet {group_set} {'created' if created else 'from_db'} ")
        group_set_dict[id] = group_set

    return group_set


def load_groupsets(options, version, group_dict):
    group_set_dict = {}
    api = get_api(options)
    dhis2_group_sets = api.get(
        "organisationUnitGroupSets", params={"paging": "false", "fields": "id,name,organisationUnitGroups[id,name]"}
    )
    dhis2_group_sets = dhis2_group_sets.json()["organisationUnitGroupSets"]

    for dhis2_group_set in dhis2_group_sets:
        group_set = get_group_set(dhis2_group_set, group_set_dict, version)

        for ougroup in dhis2_group_set["organisationUnitGroups"]:
            group = get_or_create_group(ougroup, group_dict, version)
            group_set.groups.add(group)


def get_api_config(
    url: Optional[str], login: Optional[str], password: Optional[str], source: DataSource
) -> Dict[str, Any]:
    if url and login and password:
        connection_config = {
            "dhis2_url": url,
            "dhis2_password": password,
            "dhis2_user": login,
        }
    # TODO handle case when request doesn't have all 3 fields (url, login, password)
    #  to avoid creating tasks with parameters other than those expected by user
    else:
        if source.credentials:
            connection_config = {
                "dhis2_url": source.credentials.url,
                "dhis2_password": source.credentials.password,
                "dhis2_user": source.credentials.login,
            }
        else:
            raise ValueError("No credentials exist for this source, please provide them ")
    return connection_config


@task_decorator(task_name="dhis2_ou_importer")
def dhis2_ou_importer(
    source_id: int,
    source_version_number: str,
    force: bool,
    validate: bool,
    continue_on_error: bool,
    url: Optional[str],
    login: Optional[str],
    password: Optional[str],
    task: Task = None,
) -> Task:

    the_task = task
    source = DataSource.objects.get(id=source_id)
    source_version, _created = SourceVersion.objects.get_or_create(
        number=int(source_version_number), data_source=source
    )
    start = time.time()

    logger.debug("source", source)
    logger.debug("source_version", source_version)

    connection_config = get_api_config(url, login, password, source)

    the_task.report_progress_and_stop_if_killed(progress_message="Fetching org units")
    orgunits = fetch_orgunits(connection_config)

    version, _created = SourceVersion.objects.get_or_create(number=source_version_number, data_source=source)
    if OrgUnit.objects.filter(version=version).count() > 0:
        raise Exception(f"Version {SourceVersion}is not Empty")

    # Fallback type if we don't find a type
    unknown_unit_type, _created = OrgUnitType.objects.get_or_create(name=f"{source.name}-{'Unknown'}-{source.id:d}")
    unknown_unit_type.projects.set(source.projects.all())

    unit_dict = dict()
    type_dict = {}
    group_dict = {}

    index = 0
    error_count = 0

    the_task.report_progress_and_stop_if_killed(
        progress_value=0, end_value=len(orgunits), progress_message="Importing org units"
    )

    for row in orgunits:
        try:
            org_unit = orgunit_from_row(
                row, source, type_dict, unit_dict, group_dict, unknown_unit_type, validate, version
            )
            unit_dict[org_unit.source_ref] = org_unit

            # log progress every 100 orgunits
            if index % 100 == 0:
                res_string = "%.2f sec, processed %i org units" % (time.time() - start, index)
                the_task.report_progress_and_stop_if_killed(progress_message=res_string, progress_value=index)

        except Exception as e:
            logger.exception(f"Error importing row {index:d}: {row}")

            if not continue_on_error:
                raise e
            error_count += 1
        index += 1

    logger.debug(
        f"Created {index} orgunits",
    )

    load_groupsets(connection_config, version, group_dict)

    end = time.time()
    res_string = f"""Processed {len(unit_dict)} orgunits in {end - start:.2f} seconds
        Orgunits with point: {len([p for p in unit_dict.values() if p.location])},
        Orgunits with polygon: { len([p for p in unit_dict.values() if p.geom])}
        Errors : {error_count}
    """
    if error_count:
        logger.error(f"{error_count} import errors ignored")

    the_task.report_success(message=res_string)
    return the_task
