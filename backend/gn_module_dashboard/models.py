from sqlalchemy import ForeignKey
from sqlalchemy.sql import select

from utils_flask_sqla.serializers import serializable
from geonature.utils.env import DB


# vm_taxonomie
@serializable
class VTaxonomie(DB.Model):
    __tablename__ = "vm_taxonomie"
    __table_args__ = {"schema": "gn_dashboard"}
    level = DB.Column(DB.Unicode)
    name_taxon = DB.Column(DB.Unicode, primary_key=True)


# vm_synthese_frameworks
@serializable
class VFrameworks(DB.Model):
    __tablename__ = "vm_synthese_frameworks"
    __table_args__ = {"schema": "gn_dashboard"}
    id_acquisition_framework = DB.Column(DB.Integer, primary_key=True)
    acquisition_framework_name = DB.Column(DB.Unicode)
    year = DB.Column(DB.Integer)
    nb_obs = DB.Column(DB.Integer)
