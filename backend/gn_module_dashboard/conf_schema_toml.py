"""
   Spécification du schéma toml des paramètres de configurations
   Fichier spécifiant les types des paramètres et leurs valeurs par défaut
   Fichier à ne pas modifier. Paramètres surcouchables dans config/config_gn_module.tml
"""

from marshmallow import Schema, fields, validates_schema, ValidationError
from marshmallow.validate import Range


class GnModuleSchemaConf(Schema):
    CRONTAB = fields.String(load_default="2 0 * * *")
    AREA_TYPE = fields.List(fields.String(), load_default=["COM", "M1", "M5", "M10"])
    NB_CLASS_OBS = fields.Integer(load_default=5, validate=Range(min=1, max=10))
    NB_CLASS_TAX = fields.Integer(load_default=5, validate=Range(min=1, max=10))
    SIMPLIFY_LEVEL = fields.Integer(load_default=50)
    DISPLAY_PER_YEAR_GRAPH = fields.Boolean(load_default=True)
    DISPLAY_PER_GEO_GRAPH = fields.Boolean(load_default=True)
    DISPLAY_PER_TAXONOMIC_RANK_GRAPH = fields.Boolean(load_default=True)
    DISPLAY_PER_CA_GRAPH = fields.Boolean(load_default=True)
    DISPLAY_TAXONOMIC_CONTACTS_GRAPH = fields.Boolean(load_default=True)
    DISPLAY_NBOBS_LEGEND_BY_DEFAULT_IN_GEO_GRAPH = fields.Boolean(load_default=True)
    OBSCOLORS = fields.Dict(
        missing={
            "1": ["#BE8096"],
            "2": ["#BE8096", "#64112E"],
            "3": ["#D4AAB9", "#89173F", "#320917"],
            "4": ["#D4AAB9", "#9E4161", "#64112E", "#260712"],
            "5": ["#E9D4DC", "#B36B84", "#89173F", "#4B0D23", "#19050C"],
            "6": ["#E9D4DC", "#C995A7", "#9E4161", "#711334", "#3F0B1D", "#0D0306"],
            "7": ["#E9D4DC", "#C995A7", "#A95673", "#89173F", "#64112E", "#3F0B1D", "#19050C"],
            "8": [
                "#F4E9ED",
                "#DEBFCA",
                "#BE8096",
                "#9E4161",
                "#7D153A",
                "#580F29",
                "#320917",
                "#0D0306",
            ],
            "9": [
                "#F4E9ED",
                "#DEBFCA",
                "#BE8096",
                "#9E4161",
                "#89173F",
                "#64112E",
                "#3F0B1D",
                "#260712",
                "#0D0306",
            ],
            "10": [
                "#F4E9ED",
                "#DEBFCA",
                "#BE8096",
                "#9E4161",
                "#89173F",
                "#711334",
                "#580F29",
                "#3F0B1D",
                "#260712",
                "#0D0306",
            ],
        }
    )
    TAXCOLORS = fields.Dict(
        missing={
            "1": ["#8AB2B2"],
            "2": ["#8AB2B2", "#1E5454"],
            "3": ["#B1CCCC", "#297373", "#0F2A2A"],
            "4": ["#B1CCCC", "#4F8C8C", "#1E5454", "#0C2020"],
            "5": ["#D8E5E5", "#76A5A5", "#297373", "#173F3F", "#081515"],
            "6": ["#D8E5E5", "#9DBFBF", "#4F8C8C", "#225F5F", "#133535", "#040B0B"],
            "7": ["#D8E5E5", "#9DBFBF", "#639999", "#297373", "#1E5454", "#133535", "#081515"],
            "8": [
                "#EBF2F2",
                "#C4D8D8",
                "#8AB2B2",
                "#4F8C8C",
                "#266969",
                "#1B4A4A",
                "#0F2A2A",
                "#040B0B",
            ],
            "9": [
                "#EBF2F2",
                "#C4D8D8",
                "#8AB2B2",
                "#4F8C8C",
                "#297373",
                "#1E5454",
                "#133535",
                "#0C2020",
                "#040B0B",
            ],
            "10": [
                "#EBF2F2",
                "#C4D8D8",
                "#8AB2B2",
                "#4F8C8C",
                "#297373",
                "#225F5F",
                "#1B4A4A",
                "#133535",
                "#0C2020",
                "#040B0B",
            ],
        }
    )
