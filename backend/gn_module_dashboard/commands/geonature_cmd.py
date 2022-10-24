from flask.cli import with_appcontext

from geonature.core.command import main

from geonature.utils.env import DB


@main.command()
@with_appcontext
def gn_dashboard_refresh_vm():
    """
    Rafraîchissement des VM du dashboard
    """
    DB.session.execute("SELECT gn_dashboard.refresh_materialized_view_data()")
