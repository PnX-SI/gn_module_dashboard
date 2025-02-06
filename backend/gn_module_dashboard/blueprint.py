import json
from flask import Blueprint, request, jsonify
from sqlalchemy.sql import func, text, select
import sqlalchemy as sa

from geojson import FeatureCollection, Feature

from sqlalchemy.sql.expression import label, distinct, case
from werkzeug.exceptions import BadRequest

from utils_flask_sqla.response import json_resp
from geonature.utils.env import DB, db

from .models import VSynthese, VTaxonomie, VFrameworks
from geonature.core.gn_synthese.models import Synthese, CorAreaSynthese
from ref_geo.models import BibAreasTypes, LAreas

# # import des fonctions utiles depuis le sous-module d'authentification
# from geonature.core.gn_permissions import decorators as permissions
# from geonature.core.gn_permissions.tools import get_or_fetch_user_cruved

blueprint = Blueprint("dashboard", __name__, cli_group="dashboard")


# Obtenir le nombre d'observations et le nombre de taxons pour chaque année
# vm_synthese
@blueprint.route("/synthese", methods=["GET"])
@json_resp
def get_synthese_stat():
    params = request.args
    query = sa.select(
        func.date_part("year", VSynthese.date_min).label("year"),
        func.count(VSynthese.id_synthese).label("count_id_synthese"),
        func.count(distinct(VSynthese.cd_ref)).label("count_cd_ref"),
    ).group_by("year")

    filters = {
        "selectedRegne": VSynthese.regne,
        "selectedPhylum": VSynthese.phylum,
        "selectedClasse": VSynthese.classe,
        "selectedOrdre": VSynthese.ordre,
        "selectedFamille": VSynthese.famille,
        "selectedGroup3INPN": VSynthese.group3_inpn,
        "selectedGroup2INPN": VSynthese.group2_inpn,
        "selectedGroup1INPN": VSynthese.group1_inpn,
        "taxon": VSynthese.cd_ref,
    }

    for param, column in filters.items():
        if param in params and params[param] != "":
            query = query.filter(column == params[param])
    return db.session.execute(query).all()


# Obtenir le nombre d'observations et le nombre de taxons pour chaque zonage avec une échelle donnée (type_code)
@blueprint.route("/areas/<simplify_level>/<type_code>", methods=["GET"])
@json_resp
def get_areas_stat(simplify_level, type_code):
    params = request.args
    # x : Variable contenant les conditions WHERE à ajouter à la requête générale
    year_start = request.args.get("yearStart", None)
    year_end = request.args.get("yearEnd", None)

    where_clause = []
    if year_start:
        where_clause.append(sa.func.date_part("year", VSynthese.date_min) >= year_start)

    if year_end:
        where_clause.append(sa.func.date_part("year", VSynthese.date_max) <= year_end)
    filters = {
        "selectedRegne": VSynthese.regne,
        "selectedPhylum": VSynthese.phylum,
        "selectedClasse": VSynthese.classe,
        "selectedOrdre": VSynthese.ordre,
        "selectedFamille": VSynthese.famille,
        "taxon": VSynthese.cd_ref,
        "selectedGroup1INPN": VSynthese.group1_inpn,
        "selectedGroup2INPN": VSynthese.group2_inpn,
        "selectedGroup3INPN": VSynthese.group3_inpn,
    }

    for param, column in filters.items():
        if param in params and params[param] != "":
            where_clause.append(column == params[param])

    count_cte = (
        sa.select(
            CorAreaSynthese.id_area,
            func.count(VSynthese.id_synthese).label("nb_obs"),
            func.count(func.distinct(VSynthese.cd_ref)).label("nb_tax"),
        )
        .join(
            CorAreaSynthese,
            CorAreaSynthese.id_synthese == VSynthese.id_synthese,
        )
        .join(LAreas, LAreas.id_area == CorAreaSynthese.id_area)
        .join(BibAreasTypes, BibAreasTypes.id_type == LAreas.id_type)
        .where(
            BibAreasTypes.type_code == type_code,
            LAreas.enable == True,
            *where_clause,
        )
        .group_by(CorAreaSynthese.id_area)
        .cte()
    )

    query = select(
        LAreas.area_name,
        func.st_asgeojson(
            func.st_transform(func.st_simplifyPreserveTopology(LAreas.geom, simplify_level), 4326)
        ),
        count_cte.c.nb_obs,
        count_cte.c.nb_tax,
    ).join(count_cte, count_cte.c.id_area == LAreas.id_area)
    # q : Requête générale

    data = db.session.execute(query)

    geojson_features = []
    for elt in data:
        geojson = json.loads(elt[1])
        properties = {
            "area_name": elt[0],
            "nb_obs": int(elt[2]),
            "nb_taxons": int(elt[3]),
        }
        geojson["properties"] = properties
        geojson_features.append(geojson)
    return FeatureCollection(geojson_features)


# Obtenir le nombre d'observations pour chaque taxon avec un rang taxonomique donné
# vm_synthese
@blueprint.route("/synthese_per_tax_level/<taxLevel>", methods=["GET"])
@json_resp
def get_synthese_per_tax_level_stat(taxLevel):
    params = request.args
    try:
        column_taxlevel = getattr(VSynthese, taxLevel)
    except AttributeError:
        raise BadRequest(f"No attribute {taxLevel} in VSynthese VM")
    q = (
        DB.session.query(
            column_taxlevel,
            func.count(VSynthese.id_synthese),
        )
        .group_by(column_taxlevel)
        .order_by(column_taxlevel)
    )
    if "yearStart" in params and "yearEnd" in params:
        q = q.filter(func.date_part("year", VSynthese.date_min) >= params["yearStart"])
        q = q.filter(func.date_part("year", VSynthese.date_max) <= params["yearEnd"])
    return [{"taxon": d[0], "nb_obs": d[1]} for d in q.all()]


# Obtenir le nombre d'observations par cadre d'acquisition par année
# vm_synthese_frameworks
@blueprint.route("/frameworks", methods=["GET"])
@json_resp
def get_frameworks_stat():
    afs = request.args.getlist("id_acquisition_framework")
    q = DB.session.query(
        func.json_build_object(
            "acquisition_framework_name",
            VFrameworks.acquisition_framework_name,
            "data",
            func.array_agg(
                func.json_build_object("year", VFrameworks.year, "nb_obs", VFrameworks.nb_obs)
            ),
        )
    ).group_by(VFrameworks.acquisition_framework_name)
    if afs:
        q = q.filter(VFrameworks.id_acquisition_framework.in_(afs))
    q = q.order_by(VFrameworks.acquisition_framework_name)
    return [d[0] for d in q.all()]


# Obtenir le nombre de taxons recontactés, non recontactés et nouveaux pour une année donnée
@blueprint.route("/recontact/<year>", methods=["GET"])
@json_resp
def get_recontact_stat(year):
    q = text(
        """ WITH recontactees AS
                (SELECT DISTINCT cd_ref FROM gn_synthese.synthese s JOIN taxonomie.taxref t ON t.cd_nom=s.cd_nom WHERE date_part('year', date_min) < :selectedYear
                INTERSECT
                SELECT DISTINCT cd_ref FROM gn_synthese.synthese s JOIN taxonomie.taxref t ON t.cd_nom=s.cd_nom WHERE date_part('year', date_min) = :selectedYear),
            non_recontactees AS
                (SELECT DISTINCT cd_ref FROM gn_synthese.synthese s JOIN taxonomie.taxref t ON t.cd_nom=s.cd_nom WHERE date_part('year', date_min) < :selectedYear
                EXCEPT
                SELECT DISTINCT cd_ref FROM gn_synthese.synthese s JOIN taxonomie.taxref t ON t.cd_nom=s.cd_nom WHERE date_part('year', date_min) = :selectedYear),
            nouvelles AS
                (SELECT DISTINCT cd_ref FROM gn_synthese.synthese s JOIN taxonomie.taxref t ON t.cd_nom=s.cd_nom WHERE date_part('year', date_min) = :selectedYear
                EXCEPT
                SELECT DISTINCT cd_ref FROM gn_synthese.synthese s JOIN taxonomie.taxref t ON t.cd_nom=s.cd_nom WHERE date_part('year', date_min) < :selectedYear)

            SELECT count(cd_ref) FROM recontactees
            UNION ALL
            SELECT count(cd_ref) FROM non_recontactees
            UNION ALL
            SELECT count(cd_ref) FROM nouvelles """
    )
    data = DB.engine.execute(q, selectedYear=year)
    return [elt[0] for elt in data]


# Obtenir la liste des taxons observés pour un rang taxonomique donné
# vm_taxonomie
@blueprint.route("/taxonomy/<taxLevel>", methods=["GET"])
@json_resp
def get_taxonomy(taxLevel):
    q = (
        DB.session.query(VTaxonomie.name_taxon)
        .order_by(
            case([(VTaxonomie.name_taxon == "Not defined", 1)], else_=0),
            VTaxonomie.name_taxon,
        )
        .filter(VTaxonomie.level == taxLevel)
    ).order_by(VTaxonomie.name_taxon)
    return q.all()


# Obtenir la liste des type_name des areas_types
@blueprint.route("/areas_types", methods=["GET"])
@json_resp
def get_areas_types():
    params = request.args
    q = DB.session.query(BibAreasTypes)
    if "type_code" in params:
        tab_types_codes = params.getlist("type_code")
        q = q.filter(BibAreasTypes.type_code.in_(tab_types_codes))
    data = q.all()
    return [elt.as_dict() for elt in data]


# Obtenir la liste des années au cours desquelles des observations ont été faîtes
# OU obtenir l'année min et l'année max de cette liste
# vm_synthese
@blueprint.route("/years", methods=["GET"])
@json_resp
def get_years():
    q = DB.session.query(
        label("year", distinct(func.date_part("year", VSynthese.date_min)))
    ).order_by("year")
    return [d[0] for d in q.all()]


@blueprint.route("/report/<year>", methods=["GET"])
def yearly_recap(year):
    nb_obs_year = DB.session.execute(
        """
        SELECT count(*) 
        FROM gn_synthese.synthese
        WHERE date_part('year', date_min) = :year
        """,
        {"year": year},
    ).scalar()
    nb_obs_total = DB.session.execute(
        """
        SELECT count(*) 
        FROM gn_synthese.synthese
        WHERE date_part('year', date_min) <= :year
        """,
        {"year": year},
    ).scalar()
    nb_new_species = DB.session.execute(
        """
        SELECT COUNT(*) FROM (
            SELECT DISTINCT t.cd_ref 
            FROM gn_synthese.synthese s JOIN taxonomie.taxref t ON t.cd_nom=s.cd_nom 
            WHERE date_part('year', date_min) = :year
            EXCEPT
            SELECT DISTINCT t.cd_ref 
            FROM gn_synthese.synthese s JOIN taxonomie.taxref t ON t.cd_nom=s.cd_nom 
            WHERE date_part('year', date_min) < :year 
        ) sub
        """,
        {"year": year},
    ).scalar()
    new_datasets = DB.session.execute(
        """
        SELECT count(*)
        FROM gn_meta.t_datasets td 
        WHERE date_part('year', td.meta_create_date) = :year
        """,
        {"year": year},
    ).scalar()
    new_species = DB.session.execute(
        """
        SELECT t.nom_complet, t.nom_vern, t.group2_inpn, count(s.*) FROM (
            SELECT DISTINCT t.cd_ref 
            FROM gn_synthese.synthese s JOIN taxonomie.taxref t ON t.cd_nom=s.cd_nom 
            WHERE date_part('year', date_min) = :year
            EXCEPT
            SELECT DISTINCT t.cd_ref 
            FROM gn_synthese.synthese s JOIN taxonomie.taxref t ON t.cd_nom=s.cd_nom 
            WHERE date_part('year', date_min) < :year 
            ) sub
            JOIN gn_synthese.synthese s  ON sub.cd_ref = taxonomie.find_cdref(s.cd_nom)
            JOIN taxonomie.taxref t on t.cd_nom = sub.cd_ref
            WHERE date_part('year', date_min) = :year
            GROUP BY t.nom_vern, t.nom_complet, t.group2_inpn
            ORDER BY t.nom_complet ASC
        """,
        {"year": year},
    ).fetchall()
    most_viewed_species = DB.session.execute(
        """
        SELECT t.nom_complet, t.nom_vern,  t.group2_inpn, count(*)
        FROM gn_synthese.synthese s 
        JOIN taxonomie.taxref t on t.cd_nom = s.cd_nom 
        WHERE date_part('year', date_min) = :year 
        GROUP BY t.nom_complet , t.nom_vern, t.group2_inpn 
        ORDER BY count(*) desc 
        LIMIT 10
        """,
        {"year": year},
    ).fetchall()

    data_by_datasets = DB.session.execute(
        """
        SELECT  td.dataset_name, count(*)
        FROM gn_synthese.synthese s 
        JOIN gn_meta.t_datasets td on s.id_dataset = td.id_dataset 
        WHERE date_part('year', s.date_min) = :year
        GROUP BY td.dataset_name 
        ORDER BY count(*) desc
        """,
        {"year": year},
    ).fetchall()
    nb_taxon_year = DB.session.execute(
        """
        SELECT count(distinct cd_ref)
        FROM gn_synthese.synthese s 
        JOIN taxonomie.taxref t on s.cd_nom = t.cd_nom
        WHERE date_part('year', s.date_min) = :year
        """,
        {"year": year},
    ).scalar()
    observations_by_year = DB.session.execute(
        """
        select count(id_synthese), date_part('year', s.date_min) as year_
        from gn_synthese.synthese s
        WHERE date_part('year', s.date_min) >= 1990
        group by year_
        order by year_ ASC
        """
    ).fetchall()
    yearsWithObs = DB.session.execute(
        """
        SELECT distinct date_part('year', s.date_min) as year
        FROM gn_synthese.synthese s
        ORDER BY year DESC
        """
    ).fetchall()
    observations_by_group = DB.session.execute(
        """
        SELECT count(*), t.group2_inpn
        FROM gn_synthese.synthese s
        JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom
        WHERE date_part('year', s.date_min) = :year
        GROUP BY t.group2_inpn
        """,
        {"year": year},
    )
    t = {
        "yearsWithObs": [dict(row) for row in yearsWithObs],
        "year": year,
        "nb_obs_year": nb_obs_year,
        "nb_obs_total": nb_obs_total,
        "nb_new_species": nb_new_species,
        "nb_taxon_year": nb_taxon_year,
        "new_datasets": new_datasets,
        "new_species": [dict(row) for row in new_species],
        "most_viewed_species": [dict(row) for row in most_viewed_species],
        "observations_by_group": [dict(row) for row in observations_by_group],
        "data_by_datasets": [dict(row) for row in data_by_datasets],
        "observations_by_year": [dict(row) for row in observations_by_year],
    }

    return jsonify(t)


@blueprint.cli.command()
def refresh_vm():
    """
    Rafraîchissement des VM du dashboard
    """
    DB.session.execute(func.gn_dashboard.refresh_materialized_view_data())
    DB.session.commit()
