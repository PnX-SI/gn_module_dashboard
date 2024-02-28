=========
CHANGELOG
=========

1.5.0 (2024-02-28)
------------------

Nécessite la version 2.14.0 (ou plus) de GeoNature.

**🚀 Nouveautés**

* Ajout du Groupe 3 INPN dans les filtres (par @mvergez)
* Compatibilité avec GeoNature 2.14

1.4.0 (2023-08-23)
------------------

Nécessite la version 2.13.0 (ou plus) de GeoNature.

**🚀 Nouveautés**

* Compatibilité avec GeoNature 2.13.0 et la refonte des permissions, en définissant les permissions disponibles du module (#63)

**🐛 Corrections**

* Correction du changement d'année sur le rapport annuel (#61, par @hypsug0)

1.3.0 (2023-03-27)
------------------

Nécessite GeoNature version 2.12.0 (ou plus)

**🚀 Nouveautés**

* Compatibilité avec GeoNature 2.12 (Angular 15, configuration dynamique, configuration centralisée)
* Rafraîchissement automatique des vues matérialisées via Celery Beat tous les jours à 2h.
  La fréquence est modifiable avec le paramètre ``CRONTAB`` de la configuration du module.
* Refonte du graphique des cadres d'acquisition pour le rendre plus lisible (#16)
* Mise à jour de Chart.js version 2 à 4
* Remplacement de noUiSlider par Material slider
* Factorisation et nettoyage général du code du module

**⚠️ Notes de version**

* Si vous aviez mis en place un cron système pour rafraîchir les vues matérialisées (dans `/etc/cron/geonature` ou autre),
  vous pouvez le supprimer car elles sont désormais rafraîchies automatiquement avec Celery Beat.

1.2.1 (2022-12-21)
------------------

Compatible avec GeoNature 2.10, 2.11 et plus.

**🐛 Corrections**

* Suppression d’un import inutile supprimé dans GeoNature 2.11
* Correction et mise à jour de la documentation du module
* Ajout d’indexes potentiellement manquants sur les vieilles installations du module

1.2.0 (2022-11-02)
------------------

Nécessite la version 2.10.0 (ou plus) de GeoNature.

**🚀 Nouveautés**

* Compatibilité avec Angular version 12, mis à jour dans la version 2.10.0 de GeoNature (#38)
* Packaging du module

**🐛 Corrections**

* Correction de la commande de mise à jour des vues matérialisées du module (#46)

**⚠️ Notes de version**

* Suivez la procédure classique de mise à jour du module
* Exécuter la commande suivante afin d’indiquer à Alembic l'état de votre base de données :

  ::

    cd
    source geonature/backend/venv/bin/activate
    geonature db stamp 2628978e1016
    geonature db autoupgrade

1.1.0 (2022-01-03)
------------------

Non compatible avec les versions 2.10 et supérieures de GeoNature.

**🚀 Nouveautés**

* Ajout d'un rapport annuel des observations (#40)

1.0.1 (2021-10-08)
------------------

Nécessite la version 2.8.0 (ou plus) de GeoNature

**🚀 Nouveautés**

* Compatibilité avec Marshmallow 3 / GeoNature 2.8.0

1.0.0 (2021-03-29)
------------------

**🚀 Nouveautés**

* Création d'une commande GeoNature de rafraîchissement des VM (#24)
* Automatisation du rafraîchissement des VM via un cron et la nouvelle commande dédiée (#24)
* Préchargement des graphiques (#17)
* Possibilité d'afficher/masquer certains graphiques (#5)
* Paramètre pour configurer le type d'entité géographique par défaut (#19)
* Implémentation des classes dynamiques (#10)
* Possibilité de configurer le graphique par défaut de "synthèse par entité géographique" (taxons ou observations) (#23)

**🐛 Corrections**

* Correction année du slider en dur (#20)
* Utilisation de la librairie utils-sqla (#30)

**⚠️ Notes de version**

Si vous faites une mise à jour du module :

* Dans le fichier ``config/conf_gn_module.toml``, remplacez les paramètres ``BORNE_TAXON`` et ``BORNE_OBS`` par ``NB_CLASS_OBS`` et ``NB_CLASS_TAX`` comme dans l'exemple (https://github.com/PnX-SI/gn_module_dashboard/blob/master/config/conf_gn_module.toml.example) 
* Vous pouvez mettre en place le cron de rafraîchissement des VM ou le mettre à jour. Ouvrez le fichier crontab (``crontab -e``) et copiez la ligne suivante en adaptant le chemin et éventuellement la fréquence d'exécution (tous les dimanches à minuit dans cet exemple) : 

::

    0 0 * * SUN /home/myuser/geonature/backend/venv/bin/geonature gn_dashboard_refresh_vm # gn_dashboard cron job

0.2.0 (2020-02-20)
------------------

**🐛 Corrections**

* Compatibilité GeoNature 2.3.1
* Optimisation et non prise en compte des communes non actives
* Révision de la documentation d'installation et de mise à jour

0.1.0 (2019-09-12)
------------------

Première version fonctionnelle du module GeoNature de tableau de bord, développé par @ElsaGuilley. 
Compatible avec la version de 2.2.1 de GeoNature.

Démo vidéo : https://geonature.fr/docs/img/2019-09-GN-dashboard-0.1.0.gif

**Fonctionnalités**

* Création d'un schéma dédié ``gn_dashboard`` avec les vues et vues matérialisées nécessaires aux graphiques et cartes de synthèse du module (#1)
* Histogramme du nombre d'observations/nombre de taxons par année
* Carte du nombre d'observations/nombre de taxons par commune ou autre types de zonage (définis en paramètre)
* Répartition des observations par rang taxonomique ou groupe INPN
* Histogramme du nombre d'observations par cadre d'acquisition et par année
* Répartition du nombre d’espèces recontactés, non recontactés ou nouvelles par année
* Filtres par rang taxonomique, groupe ou taxon et par période
