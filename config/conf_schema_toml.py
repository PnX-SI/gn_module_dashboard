"""
   Spécification du schéma toml des paramètres de configurations
   Fichier spécifiant les types des paramètres et leurs valeurs par défaut
   Fichier à ne pas modifier. Paramètres surcouchables dans config/config_gn_module.tml
"""

from marshmallow import Schema, fields, validates_schema, ValidationError


class GnModuleSchemaConf(Schema):
    AREA_TYPE = fields.List(fields.String(), missing=["COM", "M1", "M5", "M10"])
    NB_CLASS_OBS = fields.Integer(missing=5)
    NB_CLASS_TAX = fields.Integer(missing=5)
    BORNE_OBS = fields.List(fields.Integer(), missing=[1, 20, 40, 60, 80, 100, 120])
    BORNE_TAXON = fields.List(fields.Integer(), missing=[1, 5, 10, 15])
    SIMPLIFY_LEVEL = fields.Integer(missing=50)
    DISPLAY_PER_YEAR_GRAPH = fields.Boolean(default=True) 
    DISPLAY_PER_GEO_GRAPH = fields.Boolean(default=True) 
    DISPLAY_PER_TAXONOMIC_RANK_GRAPH = fields.Boolean(default=True) 
    DISPLAY_PER_CA_GRAPH = fields.Boolean(default=True) 
    DISPLAY_TAXONOMIC_CONTACTS_GRAPH = fields.Boolean(default=True)
    DISPLAY_NBOBS_LEGEND_BY_DEFAULT_IN_GEO_GRAPH = fields.Boolean(default=True)

