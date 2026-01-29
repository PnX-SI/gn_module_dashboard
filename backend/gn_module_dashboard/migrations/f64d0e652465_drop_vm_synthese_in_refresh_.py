"""drop vm_synthese in refresh_materialized_view_data()

Revision ID: f64d0e652465
Revises: 58f1612ce31d
Create Date: 2025-06-23 14:41:28.872196

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "f64d0e652465"
down_revision = "58f1612ce31d"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE OR REPLACE FUNCTION gn_dashboard.refresh_materialized_view_data()
 RETURNS void
 LANGUAGE plpgsql
AS $function$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY gn_dashboard.vm_synthese_frameworks;
  REFRESH MATERIALIZED VIEW CONCURRENTLY gn_dashboard.vm_taxonomie;
END
$function$
;
""")


def downgrade():
    op.execute("""
CREATE OR REPLACE FUNCTION gn_dashboard.refresh_materialized_view_data()
 RETURNS void
 LANGUAGE plpgsql
AS $function$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY gn_dashboard.vm_synthese;
  REFRESH MATERIALIZED VIEW CONCURRENTLY gn_dashboard.vm_synthese_frameworks;
  REFRESH MATERIALIZED VIEW CONCURRENTLY gn_dashboard.vm_taxonomie;
END
$function$
;

""")
