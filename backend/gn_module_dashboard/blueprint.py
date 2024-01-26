import json
from flask import Blueprint, request, jsonify
from sqlalchemy.sql import func, text, select

from geojson import FeatureCollection, Feature

from sqlalchemy.sql.expression import label, distinct, case
from werkzeug.exceptions import BadRequest

from utils_flask_sqla.response import json_resp
from geonature.utils.env import DB

from .models import VSynthese, VTaxonomie, VFrameworks
from geonature.core.gn_synthese.models import Synthese, CorAreaSynthese
from geonature.core.gn_meta.models import TDatasets
from ref_geo.models import BibAreasTypes
from apptax.taxonomie.models import Taxref

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
    query = select(
        label("year", func.date_part("year", VSynthese.date_min)),
        func.count(VSynthese.id_synthese),
        func.count(distinct(VSynthese.cd_ref)),
    ).group_by("year")
    if ("selectedRegne" in params) and (params["selectedRegne"] != ""):
        query = query.where(VSynthese.regne == params["selectedRegne"])
    if ("selectedPhylum" in params) and (params["selectedPhylum"] != ""):
        query = query.where(VSynthese.phylum == params["selectedPhylum"])
    if "selectedClasse" in params and (params["selectedClasse"] != ""):
        query = query.where(VSynthese.classe == params["selectedClasse"])
    if "selectedOrdre" in params and (params["selectedOrdre"] != ""):
        query = query.where(VSynthese.ordre == params["selectedOrdre"])
    if "selectedFamille" in params and (params["selectedFamille"] != ""):
        query = query.where(VSynthese.famille == params["selectedFamille"])
    if ("selectedGroup2INPN" in params) and (params["selectedGroup2INPN"] != ""):
        query = query.where(VSynthese.group2_inpn == params["selectedGroup2INPN"])
    if ("selectedGroup1INPN" in params) and (params["selectedGroup1INPN"] != ""):
        query = query.where(VSynthese.group1_inpn == params["selectedGroup1INPN"])
    if ("taxon" in params) and (params["taxon"] != ""):
        query = query.where(VSynthese.cd_ref == params["taxon"])
    return DB.session.scalars(query).all()


# Obtenir le nombre d'observations et le nombre de taxons pour chaque zonage avec une échelle donnée (type_code)
@blueprint.route("/areas/<simplify_level>/<type_code>", methods=["GET"])
@json_resp
def get_areas_stat(simplify_level, type_code):
    params = request.args
    # x : Variable contenant les conditions WHERE à ajouter à la requête générale
    year_start = request.args.get("yearStart", None)
    year_end = request.args.get("yearEnd", None)
    x = """ """
    if year_start or year_end:
        x = (
            x
            + """ AND date_part('year', s.date_min) >= """
            + year_start
            + """ AND date_part('year', s.date_max) <= """
            + year_end
        )
    if ("selectedRegne" in params) and (params["selectedRegne"] != ""):
        x = x + """AND t.regne = '""" + params["selectedRegne"] + """' """
    if ("selectedPhylum" in params) and (params["selectedPhylum"] != ""):
        x = x + """AND t.phylum = '""" + params["selectedPhylum"] + """' """
    if ("selectedClasse") in params and (params["selectedClasse"] != ""):
        x = x + """AND t.classe = '""" + params["selectedClasse"] + """' """
    if ("selectedOrdre") in params and (params["selectedOrdre"] != ""):
        x = x + """AND t.ordre = '""" + params["selectedOrdre"] + """' """
    if ("selectedFamille") in params and (params["selectedFamille"] != ""):
        x = x + """AND t.famille = '""" + params["selectedFamille"] + """' """
    if ("taxon") in params and (params["taxon"] != ""):
        x = x + """AND t.cd_ref = """ + params["taxon"] + """ """
    if ("selectedGroup1INPN") in params and (params["selectedGroup1INPN"] != ""):
        x = x + """AND t.group1_inpn = '""" + params["selectedGroup1INPN"] + """' """
    if ("selectedGroup2INPN") in params and (params["selectedGroup2INPN"] != ""):
        x = x + """AND t.group2_inpn = '""" + params["selectedGroup2INPN"] + """' """
    # q : Requête générale
    query = text(
        """ WITH count AS
            (SELECT cor.id_area, count(distinct cor.id_synthese) as nb_obs, count(distinct t.cd_ref) as nb_tax
            FROM gn_synthese.cor_area_synthese cor
            JOIN gn_synthese.synthese s ON s.id_synthese=cor.id_synthese
            JOIN taxonomie.taxref t ON s.cd_nom=t.cd_nom
            JOIN ref_geo.l_areas l ON cor.id_area = l.id_area
            JOIN ref_geo.bib_areas_types lt ON l.id_type = lt.id_type
            WHERE lt.type_code = :code AND l.enable = true
        """
        + x
        + """ GROUP BY cor.id_area)
        SELECT a.area_name, st_asgeojson(st_transform(st_simplifyPreserveTopology(a.geom, :level), 4326)), c.nb_obs, c.nb_tax
        FROM ref_geo.l_areas a
        JOIN count c ON a.id_area = c.id_area
        """
    )
    data = DB.engine.execute(query, level=simplify_level, code=type_code)

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
        select(
            column_taxlevel,
            func.count(VSynthese.id_synthese),
        )
        .group_by(column_taxlevel)
        .order_by(column_taxlevel)
    )
    if "yearStart" in params and "yearEnd" in params:
        q = q.where(func.date_part("year", VSynthese.date_min) >= params["yearStart"])
        q = q.where(func.date_part("year", VSynthese.date_max) <= params["yearEnd"])
    return [{"taxon": d[0], "nb_obs": d[1]} for d in DB.session.scalars(q).all()]


# Obtenir le nombre d'observations par cadre d'acquisition par année
# vm_synthese_frameworks
@blueprint.route("/frameworks", methods=["GET"])
@json_resp
def get_frameworks_stat():
    afs = request.args.getlist("id_acquisition_framework")
    query = select(
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
        query = query.where(VFrameworks.id_acquisition_framework.in_(afs))
    query = query.order_by(VFrameworks.acquisition_framework_name)
    return [d[0] for d in DB.session.scalars(query).all()]


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
    query = (
        select(VTaxonomie.name_taxon)
        .order_by(
            case([(VTaxonomie.name_taxon == "Not defined", 1)], else_=0),
            VTaxonomie.name_taxon,
        )
        .where(VTaxonomie.level == taxLevel)
    ).order_by(VTaxonomie.name_taxon)
    return DB.session.scalars(query).all()


# Obtenir la liste des type_name des areas_types
@blueprint.route("/areas_types", methods=["GET"])
@json_resp
def get_areas_types():
    params = request.args
    query = select(BibAreasTypes)
    if "type_code" in params:
        tab_types_codes = params.getlist("type_code")
        query = query.where(BibAreasTypes.type_code.in_(tab_types_codes))
    data = DB.session.scalars(query).all()
    return [elt.as_dict() for elt in data]


# Obtenir la liste des années au cours desquelles des observations ont été faîtes
# OU obtenir l'année min et l'année max de cette liste
# vm_synthese
@blueprint.route("/years", methods=["GET"])
@json_resp
def get_years():
    q = select(label("year", distinct(func.date_part("year", VSynthese.date_min)))).order_by(
        "year"
    )
    return [d for d in DB.session.scalars(q).all()]


@blueprint.route("/report/<year>", methods=["GET"])
def yearly_recap(year):
    #
    nb_obs_year = DB.session.scalar(
        select(func.count("*"))
        .select_from(Synthese)
        .where(func.date_part("year", Synthese.date_min) == year)
    )
    nb_obs_total = DB.session.scalar(
        select(func.count("*"))
        .select_from(Synthese)
        .where(func.date_part("year", Synthese.date_min) <= year)
    )

    query_base = (
        select(func.distinct(Taxref.cd_ref))
        .select_from(Synthese)
        .join(Taxref, Taxref.cd_nom == Synthese.cd_nom)
    )
    nb_new_species = DB.session.scalar(
        query_base.where(
            ~Taxref.cd_ref.in_(query_base.where(func.date_part("year", Synthese.date_min) <= year))
        )
    )
    nb_new_species = DB.session.scalar(select(func.count("*")).select_from(nb_new_species))

    new_datasets = DB.session.scalar(
        select(func.count("*"))
        .select_from(TDatasets)
        .where(func.date_part("year", TDatasets.meta_create_date) == year)
    )
    new_species = DB.session.execute(
        text(
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
        """
        ),
        {"year": year},
    ).fetchall()
    most_viewed_species = DB.session.execute(
        text(
            """
        SELECT t.nom_complet, t.nom_vern,  t.group2_inpn, count(*)
        FROM gn_synthese.synthese s 
        JOIN taxonomie.taxref t on t.cd_nom = s.cd_nom 
        WHERE date_part('year', date_min) = :year 
        GROUP BY t.nom_complet , t.nom_vern, t.group2_inpn 
        ORDER BY count(*) desc 
        LIMIT 10
        """
        ),
        {"year": year},
    ).fetchall()

    data_by_datasets = DB.session.execute(
        text(
            """
        SELECT  td.dataset_name, count(*)
        FROM gn_synthese.synthese s 
        JOIN gn_meta.t_datasets td on s.id_dataset = td.id_dataset 
        WHERE date_part('year', s.date_min) = :year
        GROUP BY td.dataset_name 
        ORDER BY count(*) desc
        """
        ),
        {"year": year},
    ).fetchall()
    nb_taxon_year = DB.session.execute(
        text(
            """
        SELECT count(distinct cd_ref)
        FROM gn_synthese.synthese s 
        JOIN taxonomie.taxref t on s.cd_nom = t.cd_nom
        WHERE date_part('year', s.date_min) = :year
        """
        ),
        {"year": year},
    ).scalar()
    observations_by_year = DB.session.execute(
        text(
            """
        select count(id_synthese), date_part('year', s.date_min) as year_
        from gn_synthese.synthese s
        WHERE date_part('year', s.date_min) >= 1990
        group by year_
        order by year_ ASC
        """
        )
    ).fetchall()
    yearsWithObs = DB.session.execute(
        text(
            """
        SELECT distinct date_part('year', s.date_min) as year
        FROM gn_synthese.synthese s
        ORDER BY year DESC
        """
        )
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

    return jsonify(
        {
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
    )


@blueprint.cli.command()
def refresh_vm():
    """
    Rafraîchissement des VM du dashboard
    """
    DB.session.execute(func.gn_dashboard.refresh_materialized_view_data())
    DB.session.commit()
