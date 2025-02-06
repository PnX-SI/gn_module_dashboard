import json
from flask import Blueprint, request, jsonify
from sqlalchemy.sql import func, text, select
import sqlalchemy as sa

from geojson import FeatureCollection, Feature

from sqlalchemy.sql.expression import label, distinct, case
from werkzeug.exceptions import BadRequest

from utils_flask_sqla.response import json_resp
from geonature.utils.env import db

from .models import VSynthese, VTaxonomie, VFrameworks
from geonature.core.gn_synthese.models import Synthese, CorAreaSynthese
from ref_geo.models import BibAreasTypes, LAreas
from ref_geo.schemas import AreaTypeSchema
from apptax.taxonomie.models import Taxref
from geonature.core.gn_meta.models import TDatasets

# # import des fonctions utiles depuis le sous-module d'authentification
# from geonature.core.gn_permissions import decorators as permissions
# from geonature.core.gn_permissions.tools import get_or_fetch_user_cruved

blueprint = Blueprint("dashboard", __name__, cli_group="dashboard")


# Obtenir le nombre d'observations et le nombre de taxons pour chaque année
# vm_synthese
@blueprint.route("/synthese", methods=["GET"])
@json_resp
def get_synthese_stat():
    """
    Retourne le nombre d'observations et le nombre de taxons pour chaque année.

    Parameters
    ----------
    selectedRegne : string
        Règne taxonomique
    selectedPhylum : string
        Phylum taxonomique
    selectedClasse : string
        Classe taxonomique
    selectedOrdre : string
        Ordre taxonomique
    selectedFamille : string
        Famille taxonomique
    selectedGroup1INPN : string
        Groupe 1 INPN
    selectedGroup2INPN : string
        Groupe 2 INPN
    selectedGroup3INPN : string
        Groupe 3 INPN
    taxon : string
        Code du taxon

    Returns
    -------
    year : int
        Année
    count_id_synthese : integer
        Nombre d'observations
    count_cd_ref : int
        Nombre de taxons
    """
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
            query = query.where(column == params[param])
    return db.session.execute(query).all()


# Obtenir le nombre d'observations et le nombre de taxons pour chaque zonage avec une échelle donnée (type_code)
@blueprint.route("/areas/<simplify_level>/<type_code>", methods=["GET"])
@json_resp
def get_areas_stat(simplify_level, type_code):
    """
    Retourne le nombre d'observations et le nombre de taxons pour chaque zone
    avec une échelle donnée (type_code) et un niveau de simplification donnée
    (simplify_level).

    Parameters
    ----------
    simplify_level : int
        Niveau de simplification de la géométrie des zones.
    type_code : string
        Code de l'échelle souhaitée.

    Returns
    -------
    geojson : FeatureCollection
        Une collection de Feature au format geojson contenant le nombre
        d'observations et le nombre de taxons pour chaque zone.
    """
    params = request.args

    year_start = params.get("yearStart", None)
    year_end = params.get("yearEnd", None)

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

    response = db.session.execute(query)

    geojson_features = []
    for area_name, geojson_, nb_obs, nb_tax in response:
        geojson = json.loads(geojson_)
        geojson["properties"] = {
            "area_name": area_name,
            "nb_obs": int(nb_obs),
            "nb_taxons": int(nb_tax),
        }
        geojson_features.append(geojson)
    return FeatureCollection(geojson_features)


@blueprint.route("/synthese_per_tax_level/<taxLevel>", methods=["GET"])
@json_resp
def get_synthese_per_tax_level_stat(taxLevel):
    """
    Obtenir le nombre d'observations pour chaque taxon avec un rang taxonomique donné

    Parameters
    ----------
    taxLevel : str
        rang taxonomique

    Returns
    -------
    List of dictionaries
        taxon_name : str
            nom du taxon
        nb_obs : int
            nombre d'observations
    """
    params = request.args
    try:
        column_taxlevel = getattr(VSynthese, taxLevel)
    except AttributeError:
        raise BadRequest(f"No attribute {taxLevel} in VSynthese VM")
    query = (
        sa.select(
            column_taxlevel,
            func.count(VSynthese.id_synthese),
        )
        .group_by(column_taxlevel)
        .order_by(column_taxlevel)
    )
    if "yearStart" in params and "yearEnd" in params:
        query = query.where(func.date_part("year", VSynthese.date_min) >= params["yearStart"])
        query = query.where(func.date_part("year", VSynthese.date_max) <= params["yearEnd"])
    return [
        {"taxon": taxon, "nb_obs": nb_obs}
        for (taxon, nb_obs) in db.session.execute(query).all()  # TODO rename taxon to taxonLevel?
    ]


@blueprint.route("/frameworks", methods=["GET"])
@json_resp
def get_frameworks_stat():
    """
    Obtenir le nombre d'observations par cadre d'acquisition par année
    vm_synthese_frameworks

    Parameters
    ----------
    id_acquisition_framework : list of int
        liste des id des cadres d'acquisitions à filtre

    Returns
    -------
    list[dict]
        acquisition_framework_name : str
            nom du cadre d'acquisition
        data : list of dictionaries
            year : int
                année
            nb_obs : int
                nombre d'observations
    """
    afs = request.args.getlist("id_acquisition_framework")
    query = sa.select(
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
    return [d[0] for d in db.session.execute(query).all()]


@blueprint.route("/recontact/<year>", methods=["GET"])
@json_resp
def get_recontact_stat(year):
    """
    Obtenir le nombre de taxons recontactés, non recontactés et nouveaux pour une année donnée.

    Parameters
    ----------
    year : int
        Année pour laquelle les statistiques de recontact doivent être calculées.

    Returns
    -------
    List[int]
        Une liste contenant trois entiers :
        - Le nombre de taxons recontactés (observés à la fois l'année spécifiée et les années précédentes).
        - Le nombre de taxons non recontactés (observés uniquement les années précédentes).
        - Le nombre de nouveaux taxons (observés uniquement l'année spécifiée).
    """

    cd_ref_actual_year = (
        sa.select(func.distinct(Taxref.cd_ref))
        .select_from(Synthese)
        .join(Taxref, Taxref.cd_nom == Synthese.cd_nom)
        .where(sa.func.date_part("year", Synthese.date_min) == year)
    )
    cd_ref_year_before = (
        sa.select(func.distinct(Taxref.cd_ref))
        .select_from(Synthese)
        .join(Taxref, Taxref.cd_nom == Synthese.cd_nom)
        .where(sa.func.date_part("year", Synthese.date_min) < year)
    )

    recontactees_query = sa.intersect(cd_ref_year_before, cd_ref_actual_year)
    non_recontactees_query = sa.except_(cd_ref_year_before, cd_ref_actual_year)
    nouvelles_query = sa.except_(cd_ref_actual_year, cd_ref_year_before)

    query = sa.union_all(
        select(func.count()).select_from(recontactees_query.subquery()),
        select(func.count()).select_from(non_recontactees_query.subquery()),
        select(func.count()).select_from(nouvelles_query.subquery()),
    )

    data = db.session.execute(query).all()
    return [elt[0] for elt in data]


@blueprint.route("/taxonomy/<taxLevel>", methods=["GET"])
@json_resp
def get_taxonomy(taxLevel):
    """
    Retourne la liste des taxons observés pour un rang taxonomique donné.

    Parameters
    ----------
    taxLevel : string
        Le rang taxonomique souhaité (par exemple, 'Règne', 'Famille', etc.).

    Returns
    -------
    list
        Une liste de noms de taxons.
    """
    query = (
        sa.select(VTaxonomie.name_taxon)
        .order_by(
            case([(VTaxonomie.name_taxon == "Not defined", 1)], else_=0),
            VTaxonomie.name_taxon,
        )
        .where(VTaxonomie.level == taxLevel)
    ).order_by(VTaxonomie.name_taxon)
    return db.session.execute(query).all()


@blueprint.route("/areas_types", methods=["GET"])
@json_resp
def get_areas_types():
    """
    Retourne la liste des types de zonages.

    Parameters
    ----------
    type_code : string (optional)
        Si fourni, filtre les résultats pour ne garder que les types de zonages
        portant ce code.

    Returns
    -------
    list
        Une liste de dictionnaires, chaque dictionnaire contenant les clés
        `type_code` et `type_name` pour chaque type de zonage.
    """
    query = sa.select(BibAreasTypes)
    if "type_code" in request.args:
        tab_types_codes = request.args.getlist("type_code")
        query = query.where(BibAreasTypes.type_code.in_(tab_types_codes))

    return jsonify(
        AreaTypeSchema(many=True).dump(
            db.session.scalars(query).unique().all(),
        )
    )


@blueprint.route("/years", methods=["GET"])
@json_resp
def get_years():
    """
    Renvoie la liste des années distinctes pour lesquelles des observations
    ont été faites.

    Returns
    -------
    list[int]
        Une liste triée des années uniques extraites du champ 'date_min'
        de la vue VSynthese.
    """

    query = sa.select(
        func.distinct(
            sa.cast(
                func.date_part(
                    "year",
                    VSynthese.date_min,
                ),
                sa.Integer,
            ),
        ).label("year")
    ).order_by(text("year"))
    return db.session.scalars(query).all()


@blueprint.route("/report/<year>", methods=["GET"])
def yearly_recap(year):
    """
    Renvoie un objet JSON contenant les informations suivantes pour une
    année donnée :
    - yearsWithObs: une liste des années pour lesquelles des observations
      ont été faites
    - year: l'année demandée
    - nb_obs_year: le nombre d'observations pour l'année demandée
    - nb_obs_total: le nombre total d'observations
    - nb_new_species: le nombre de nouvelles espèces observées
    - new_datasets: le nombre de nouveaux jeux de données
    - new_species: une liste des nouvelles espèces observées
    - most_viewed_species: une liste des 10 espèces les plus vues
    - observations_by_group: une liste du nombre d'observations par groupe
    - data_by_datasets: une liste du nombre d'observations par jeu de données
    - observations_by_year: une liste du nombre d'observations par année
    """
    nb_obs_year = db.session.scalar(
        sa.select(sa.func.count())
        .select_from(VSynthese)
        .where(sa.func.date_part("year", VSynthese.date_min) == year)
    )

    nb_obs_total = db.session.scalar(
        sa.select(sa.func.count())
        .select_from(VSynthese)
        .where(sa.func.date_part("year", VSynthese.date_min) <= year)
    )

    new_species_query = sa.except_(
        sa.select(VSynthese.cd_ref)
        .join(Taxref, Taxref.cd_nom == VSynthese.cd_nom)
        .where(sa.func.date_part("year", VSynthese.date_min) == year),
        sa.select(VSynthese.cd_ref)
        .join(Taxref, Taxref.cd_nom == VSynthese.cd_nom)
        .where(sa.func.date_part("year", VSynthese.date_min) < year),
    )
    new_species_cte = new_species_query.cte()

    nb_new_species = db.session.scalar(
        sa.select(sa.func.count()).select_from(new_species_query.subquery())
    )

    new_datasets = db.session.scalar(
        sa.select(func.count()).where(
            func.date_part("year", TDatasets.meta_create_date) == year,
        )
    )
    new_species = (
        sa.select(
            Taxref.nom_complet,
            Taxref.nom_vern,
            Taxref.group2_inpn,
            func.count(VSynthese.id_synthese),
        )
        .select_from(new_species_cte)
        .join(VSynthese, VSynthese.cd_ref == new_species_cte.c.cd_ref)
        .join(Taxref, Taxref.cd_ref == new_species_cte.c.cd_ref)
        .where(func.date_part("year", VSynthese.date_min) == year)
        .group_by(Taxref.nom_complet, Taxref.nom_vern, Taxref.group2_inpn)
        .order_by(
            Taxref.nom_complet,
        )
    )
    new_species = db.session.execute(new_species).all()

    most_viewed_species_query = (
        sa.select(
            Taxref.nom_complet, Taxref.nom_vern, Taxref.group2_inpn, func.count().label("count")
        )
        .join(VSynthese, Taxref.cd_nom == VSynthese.cd_nom)
        .where(func.date_part("year", VSynthese.date_min) == year)
        .group_by(Taxref.nom_complet, Taxref.nom_vern, Taxref.group2_inpn)
        .order_by(sa.desc("count"))
        .limit(10)
    )
    most_viewed_species = db.session.execute(most_viewed_species_query).fetchall()

    data_by_datasets = db.session.execute(
        sa.select(TDatasets.dataset_name, sa.func.count())
        .join(VSynthese, VSynthese.id_dataset == TDatasets.id_dataset)
        .where(func.date_part("year", VSynthese.date_min) == year)
        .group_by(TDatasets.dataset_name)
        .order_by(sa.desc(sa.func.count()))
    ).all()

    nb_taxon_year = db.session.execute(
        sa.select(sa.func.count(sa.distinct(VSynthese.cd_ref)))
        .join(Taxref, Taxref.cd_nom == VSynthese.cd_nom)
        .where(sa.func.date_part("year", VSynthese.date_min) == year)
    ).scalar()
    observations_by_year = db.session.execute(
        sa.select(
            sa.func.count(VSynthese.id_synthese),
            sa.cast(sa.func.date_part("year", VSynthese.date_min), sa.Integer).label("year_"),
        )
        .where(sa.func.date_part("year", VSynthese.date_min) >= 1990)
        .group_by("year_")
        .order_by(sa.asc("year_"))  # TODO add asc ordering
    ).fetchall()
    yearsWithObs = db.session.execute(
        sa.select(
            sa.func.distinct(
                sa.cast(sa.func.date_part("year", VSynthese.date_min), sa.Integer)
            ).label("year")
        ).order_by(sa.desc(text("year")))
    ).fetchall()

    observations_by_group = db.session.execute(
        sa.select(
            sa.func.count(),
            Taxref.group2_inpn,
        )
        .select_from(VSynthese)
        .join(Taxref, Taxref.cd_nom == VSynthese.cd_nom)
        .where(sa.func.date_part("year", VSynthese.date_min) == year)
        .group_by(Taxref.group2_inpn)
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
    db.session.execute(func.gn_dashboard.refresh_materialized_view_data())
    db.session.commit()
