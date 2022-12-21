"""add missing index

Revision ID: 3bd3234cab96
Revises: 2628978e1016
Create Date: 2022-12-21 09:03:51.048633

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3bd3234cab96"
down_revision = "2628978e1016"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE unique index IF NOT EXISTS vm_synthese_id_synthese_idx on gn_dashboard.vm_synthese (id_synthese);
        CREATE index IF NOT EXISTS vm_synthese_cd_ref_idx on gn_dashboard.vm_synthese (cd_ref);
        CREATE unique index IF NOT EXISTS vm_synthese_frameworks_acquisition_framework_name_year_idx on gn_dashboard.vm_synthese_frameworks (acquisition_framework_name,year);
        CREATE unique index IF NOT EXISTS vm_taxonomie_name_taxon_level_idx on gn_dashboard.vm_taxonomie (name_taxon,level);
        """
    )


def downgrade():
    pass
