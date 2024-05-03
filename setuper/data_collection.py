import uuid
from datetime import datetime, timedelta
from submissions import submission2xml
import random


def setup_instances(account_name, iaso_client):
    print("-- Setting up a form")
    project_id = iaso_client.get("/api/projects/")["projects"][0]["id"]
    org_unit_types = iaso_client.get("/api/v2/orgunittypes/")["orgUnitTypes"]
    org_unit_type_ids = [out["id"] for out in org_unit_types if out["name"] != "Formation sanitaire"]

    # create a form
    data = {
        "id": None,
        "name": "Equipment/Pop/Social mob./Microplans",
        "short_name": "",
        "depth": None,
        "org_unit_type_ids": org_unit_type_ids,
        "project_ids": [project_id],
        "single_per_period": False,
        "periods_before_allowed": 0,
        "periods_after_allowed": 0,
        "device_field": "deviceid",
        "location_field": "gps",
        "label_keys": [],
    }

    form_id = iaso_client.post("/api/forms/", json=data)["id"]

    # associate it's form version and upload xlsform

    xlsx_file = "data/default_forms_for_other_level_than_health_facility.xlsx"
    data = {"form_id": form_id, "xls_file": xlsx_file}
    form_files = {"xls_file": open(xlsx_file, "rb")}

    form_version = iaso_client.post("/api/formversions/", files=form_files, data=data)

    ######## creating submissions/instances
    print("-- Downloading org units")

    # fetch orgunit ids belong to the org unit type

    for org_unit_type_id in org_unit_type_ids:
        limit = 10
        orgunits = iaso_client.get("/api/orgunits/", params={"limit": limit, "orgUnitTypeId": org_unit_type_id})[
            "orgunits"
        ]
        org_unit_ids = [ou["id"] for ou in orgunits]

        print("-- Submitting %d submissions" % limit)
        count = 0
        for org_unit_id in org_unit_ids:
            the_uuid = str(uuid.uuid4())
            file_name = "example_%s.xml" % the_uuid
            local_path = "generated/%s" % file_name
            current_datetime = int(datetime.now().timestamp())

            instance_body = [
                {
                    "id": the_uuid,
                    "latitude": None,
                    "created_at": current_datetime,
                    "updated_at": current_datetime,
                    "orgUnitId": org_unit_id,
                    "formId": form_id,
                    "longitude": None,
                    "accuracy": 0,
                    "altitude": 0,
                    "imgUrl": "imgUrl",
                    "file": local_path,
                    "name": file_name,
                }
            ]

            iaso_client.post(f"/api/instances/?app_id={account_name}", json=instance_body)

            bool_choice = random.choice(["yes", "no"])
            current_datetime = datetime.now()
            date_rdv = datetime.now() - timedelta(days=random.randint(4, 100))
            estimated_pop_village = int(random.randint(50, 100))

            instance_json = {
                "note_intro": {
                    "presence_cdf": bool_choice,
                    "type_equipement": (
                        random.choice(["refrigerateur", "congelateur", "chambre_froide", "aucun"])
                        if bool_choice == "yes"
                        else None
                    ),
                    "fabriquant": random.choice(["Fabriquant 1", "Fabriquant 2", "Fabriquant 3", "Fabriquant ..."]),
                    "modele": random.choice(["Modele 1", "Modele 2", "Modele 3", "Modele ..."]),
                    "num_serie": f"S{random.randint(1045, 304552)}NG",
                    "longueur": random.randint(5, 20),
                    "largeur": random.randint(2, 25),
                    "hauteur": random.randint(10, 25),
                    "stokage": random.randint(15, 20),
                    "source_energie": random.choice(["Electricite", "Solaire", "Petrol", "Gaz", "Gasoil"]),
                    "etat_fonctionnement": random.choice(["FB", "FR", "NF", "NI"]),
                    "cause_panne": random.choice(["RAS", "Manque de stabilisateur de tension"]),
                },
                "population": {
                    "target_population_9_59_easily_accessible": random.randint(100, 2500),
                    "target_population_9_59_accessible_by_advanced_team": random.randint(89, 2412),
                    "target_population_9_59_hard_to_access": random.randint(51, 1212),
                    "target_population_9_59_humanitarian_target_mobile": random.randint(50, 100),
                    "target_population_9_59_total": random.randint(100, 1200),
                    "population_2023": random.randint(10200, 24500),
                    "children_0_11_month": random.randint(1200, 4500),
                    "children_12_23_month": random.randint(1000, 3500),
                },
                "autorite_presente_reunion": {
                    "autorite_presente": random.choice(
                        [
                            "autorite_administrative superviseurs secteurs_apparente",
                            "autorite_administrative influenceurs_locaux partenaires_au_developpement",
                            "autorite_administrative superviseurs secteurs_apparente leaders_religieux leaders_traditionnels influenceurs_locaux partenaires_au_developpement autres_autorite",
                            "superviseurs secteurs_apparente leaders_religieux leaders_traditionnels influenceurs_locaux partenaires_au_developpement autres_autorite",
                            "superviseurs leaders_religieux influenceurs_locaux autres_autorite",
                        ]
                    ),
                    "nbre_femme": random.randint(3, 10),
                    "nbre_homme": random.randint(2, 15),
                    "engagements_sensibilisation": random.choice(
                        [
                            "mobilisation_des_autres_leaders mobilisation_des_associations",
                            "mobilisation_de_la_communaute communication_dans_les_lieux_de_culte media_au_niveau_local",
                            "mobilisation_des_autres_leaders mobilisation_des_associations mobilisation_de_la_communaute communication_dans_les_lieux_de_culte media_au_niveau_local",
                            "materiel_de_communication outils_de_travail",
                            "materiel_de_communication outils_de_travail mobilisation_des_associations",
                            "mobilisation_des_autres_leaders mobilisation_des_associations mobilisation_de_la_communaute communication_dans_les_lieux_de_culte media_au_niveau_local mobilisation_des_autres_leaders mobilisation_des_associations mobilisation_de_la_communaute communication_dans_les_lieux_de_culte media_au_niveau_local materiel_de_communication outils_de_travail",
                        ]
                    ),
                    "engagements_rh": random.choice(
                        [
                            "volontaires securisation_des_mobilisateurs autre_engagement_rh",
                            "securisation_des_mobilisateurs autre_engagement_rh",
                            "volontaires autre_engagement_rh",
                            "volontaires securisation_des_mobilisateurs",
                        ]
                    ),
                    "engagements_materiel": random.choice(
                        [
                            "logistique_de_poste_de_vaccination__tent moyen_de_d_placement__moto__v_lo__pirogu carburant",
                            "rafra_chissement__eau__nourriture__banan autre_engagement_materiel",
                            "logistique_de_poste_de_vaccination__tent moyen_de_d_placement__moto__v_lo__pirogu carburant rafra_chissement__eau__nourriture__banan autre_engagement_materiel",
                        ]
                    ),
                    "lieu_rdv": random.choice(["chefferies", "lieux_de_culte", "march_s", "ecoles", "autres"]),
                    "date_rdv": date_rdv.date(),
                },
                "microplan": {
                    "Population_estimee_du_village": estimated_pop_village,
                    "strategie": random.choice(["1 2 3 4", "1 2", "3 4", "1 3", "1 4", "2 3", "2 4"]),
                },
                "meta": {"instanceID": "uuid:" + the_uuid},
            }

            # see hat/sync/views.py
            image_number = (count % 3) + 1
            with open(f"./data/fosa{image_number}.jpeg", "rb") as fp_image:
                iaso_client.post(
                    "/sync/form_upload/",
                    files={
                        "xml_submission_file": (
                            local_path,
                            submission2xml(
                                instance_json, form_version_id=form_version["version_id"], form_id="SAMPLE_FORM_new5"
                            ),
                        ),
                        "imgUrl": fp_image,
                    },
                )

            count = count + 1

            ## mobile code
            # https://github.com/BLSQ/iaso-mobile-app/blob/develop/odk-collect/src/main/java/org/odk/collect/android/tasks/InstanceServerUploaderTask.java#L88
            # https://github.com/BLSQ/iaso-mobile-app/blob/develop/odk-collect/src/main/java/org/odk/collect/android/upload/InstanceServerUploader.java#L70
            # https://github.com/BLSQ/iaso-mobile-app/blob/develop/collect_app/src/main/java/com/bluesquare/iaso/usecase/SyncInstances.kt
            if count % 5 == 0:
                print("\t%d submissions done" % count)

    print(iaso_client.get("/api/instances", params={"limit": 1})["count"], "instances created")
