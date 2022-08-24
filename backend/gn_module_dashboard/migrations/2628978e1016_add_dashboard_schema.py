"""Add dashboard schema

Revision ID: 2628978e1016
Revises: None
Create Date: 2022-08-25 14:19:25.865116

"""
from alembic import op
import sqlalchemy as sa
import pkg_resources

# revision identifiers, used by Alembic.
revision = "2628978e1016"
down_revision = None
branch_labels = ("dashboard",)
depends_on = None

schema = "gn_dashboard"

def upgrade():
    sql_file = "dashboard.sql"
    operations = pkg_resources.resource_string(
        "gn_module_dashboard.migrations", f"data/{sql_file}"
    ).decode("utf-8")
    op.execute(operations)

def downgrade():
    op.execute(f"DROP SCHEMA if exists {schema} cascade")
