"""Add dashboard schema

Revision ID: 2628978e1016
Revises: None
Create Date: 2022-08-25 14:19:25.865116

"""

from alembic import op
import sqlalchemy as sa
from importlib.resources import files

# revision identifiers, used by Alembic.
revision = "2628978e1016"
down_revision = None
branch_labels = ("dashboard",)
depends_on = None

schema = "gn_dashboard"


def upgrade():
    sql_file = "dashboard.sql"
    resource_file = files("gn_module_dashboard.migrations") / "data" / sql_file
    operations = resource_file.read_text(encoding="utf-8")
    op.execute(operations)


def downgrade():
    op.execute(f"DROP SCHEMA {schema} CASCADE")
