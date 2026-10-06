from typing import Optional

from sqlalchemy import ForeignKey, Integer, Unicode
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import select

from utils_flask_sqla.serializers import serializable
from geonature.utils.env import DB


# vm_taxonomie
@serializable
class VTaxonomie(DB.Model):
    __tablename__ = "vm_taxonomie"
    __table_args__ = {"schema": "gn_dashboard"}
    level: Mapped[Optional[str]] = mapped_column(Unicode)
    name_taxon: Mapped[str] = mapped_column(Unicode, primary_key=True)


# vm_synthese_frameworks
@serializable
class VFrameworks(DB.Model):
    __tablename__ = "vm_synthese_frameworks"
    __table_args__ = {"schema": "gn_dashboard"}
    id_acquisition_framework: Mapped[int] = mapped_column(Integer, primary_key=True)
    acquisition_framework_name: Mapped[Optional[str]] = mapped_column(Unicode)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    nb_obs: Mapped[Optional[int]] = mapped_column(Integer)
