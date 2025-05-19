from geonature.utils.config import config

from sqlalchemy.sql import func, text, select

from geonature.core.gn_synthese.models import VSyntheseForWebApp
from geonature.core.gn_synthese.utils.query_select_sqla import SyntheseQuery
from geonature.core.gn_synthese.utils.blurring import (
    build_allowed_geom_cte,
    build_blurred_precise_geom_queries,
    build_synthese_obs_query,
    split_blurring_precise_permissions,
)


def get_blurring_cte(permissions, filters):
    blurring_permissions, precise_permissions = split_blurring_precise_permissions(permissions)
    # Build 2 queries that will be UNIONed
    # Select size hierarchy if mesh mode is selected
    MANDATORY_COLUMNS = [
        "id_synthese",
        "entity_source_pk_value",
        "url_source",
        "cd_nom",
        "id_dataset",
    ]
    columns = []
    for col in MANDATORY_COLUMNS:
        columns.extend([col, getattr(VSyntheseForWebApp, col)])
    observations = func.json_build_object(*columns).label("obs_as_json")
    blurred_geom_query, precise_geom_query = build_blurred_precise_geom_queries(
        filters, select_size_hierarchy=True
    )

    allowed_geom_cte = build_allowed_geom_cte(
        blurring_permissions=blurring_permissions,
        precise_permissions=precise_permissions,
        blurred_geom_query=blurred_geom_query,
        precise_geom_query=precise_geom_query,
        limit=None,
    )

    obs_query = build_synthese_obs_query(
        observations=observations,
        allowed_geom_cte=allowed_geom_cte,
        limit=None,
    )
    obs_query = obs_query.add_columns(VSyntheseForWebApp.id_synthese)
    obs_query = obs_query.add_columns(allowed_geom_cte.c.size_hierarchy.label("size_hierarchy"))
    obs_query = obs_query.cte("OBS")
    return obs_query
