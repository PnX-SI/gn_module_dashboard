"""add id in vm_synthese_frameworks

Revision ID: 488a2eeee4be
Revises: 3bd3234cab96
Create Date: 2023-02-23 16:48:42.267746

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "488a2eeee4be"
down_revision = "3bd3234cab96"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DROP MATERIALIZED VIEW gn_dashboard.vm_synthese_frameworks;
        CREATE MATERIALIZED VIEW gn_dashboard.vm_synthese_frameworks
        TABLESPACE pg_default
        AS SELECT DISTINCT af.acquisition_framework_name, af.id_acquisition_framework,
            date_part('year'::text, s.date_min) AS year,
            count(*) AS nb_obs
        FROM gn_synthese.synthese s
            JOIN gn_meta.t_datasets d ON d.id_dataset = s.id_dataset
            JOIN gn_meta.t_acquisition_frameworks af ON af.id_acquisition_framework = d.id_acquisition_framework
        GROUP BY af.acquisition_framework_name, (date_part('year'::text, s.date_min)), af.id_acquisition_framework
        ORDER BY af.acquisition_framework_name, (date_part('year'::text, s.date_min))
        WITH DATA;
        CREATE unique index IF NOT EXISTS vm_synthese_frameworks_acquisition_framework_name_year_idx on gn_dashboard.vm_synthese_frameworks (id_acquisition_framework,year);

        """
    )


def downgrade():
    op.execute(
        """
        DROP MATERIALIZED VIEW gn_dashboard.vm_synthese_frameworks;
        
        CREATE MATERIALIZED VIEW gn_dashboard.vm_synthese_frameworks
        AS SELECT DISTINCT af.acquisition_framework_name,
            date_part('year'::text, s.date_min) AS year,
            count(*) AS nb_obs
        FROM gn_synthese.synthese s
            JOIN gn_meta.t_datasets d ON d.id_dataset = s.id_dataset
            JOIN gn_meta.t_acquisition_frameworks af ON af.id_acquisition_framework = d.id_acquisition_framework
        GROUP BY af.acquisition_framework_name, (date_part('year'::text, s.date_min))
        ORDER BY af.acquisition_framework_name, (date_part('year'::text, s.date_min))
        WITH DATA;
        CREATE unique index IF NOT EXISTS vm_synthese_frameworks_acquisition_framework_name_year_idx on gn_dashboard.vm_synthese_frameworks (acquisition_framework_name,year);

        """
    )
