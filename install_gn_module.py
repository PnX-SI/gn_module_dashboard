import subprocess
from pathlib import Path
from crontab import CronTab
from geonature.utils.env import BACKEND_DIR as GN_BACKEND_DIR
DASHBOARD_ROOT_DIR = Path(__file__).absolute().parent


def gnmodule_install_app(gn_db, gn_app):
    """
        Fonction principale permettant de réaliser les opérations d'installation du module
    """
    with gn_app.app_context():
        # To run a SQL script use the gn_db parameter
        gn_db.session.execute(
            open(str(DASHBOARD_ROOT_DIR / "data/dashboard.sql"), "r").read())
        gn_db.session.commit()
        # Création script cron
        write_in_cron_tab()

def write_in_cron_tab():
    """
        Fonction qui écrit dans le cron tab la commande
            nocturne de rafraichissement 
    """
    cron_cmd = str(GN_BACKEND_DIR) + "/venv/bin/geonature gn_dashboard_refresh_vm"
    cron_cmt = "gn_dashboard cron job"

    cron = CronTab(user=True)

    # Test si le job exist alors suppression
    cron.remove_all(comment=cron_cmt)

    # Création nouveau job
    job = cron.new(command=cron_cmd, comment=cron_cmt)

    # Configuration de la planification => @weekly
    job.dow.on('SUN')
    
    # Ecriture dans cron tab
    cron.write()
