======================
Dashboard
======================

Module GeoNature permettant de proposer un tableau de bord contenant plusieurs graphiques et cartes basés sur les données présentes dans la synthèse de GeoNature. Développé par Elsa Guilley, stagiaire au Parc national des Ecrins en 2019. 

Démo vidéo : https://geonature.fr/docs/img/2019-09-GN-dashboard-0.1.0.gif

.. image :: https://user-images.githubusercontent.com/38694819/57705368-0ab5bb00-7664-11e9-9b40-fe5c43d4d29e.png

**Fonctionnalités** :

* Nombre d'observations et de taxons par année
* Nombre d'observations et de taxons par zonage (communes, mailles...)
* Répartition des observations par rang taxonomique
* Nombre d'observations par cadre d'acquisition par année
* Taxons recontactés, non recontactés et nouveaux par année
* Filtres divers sur chaque élément

**Présentation** :

* Rapport de stage de Elsa Guilley : https://geonature.fr/documents/2019-09-rapport-stage-Elsa-Guilley-Dashboard-Validation.pdf
* Présentation de soutenance de stage de Elsa Guilley : http://geonature.fr/documents/xxxxxxxxxxxxxxxxxxxxx

Installation
============

* Installez GeoNature (https://github.com/PnX-SI/GeoNature)
* Téléchargez la dernière version stable du module (``wget https://github.com/PnX-SI/gn_module_dashboard/archive/X.Y.Z.zip`` ou en cliquant sur le bouton GitHub "Clone or download" de cette page) dans ``/home/myuser/``
* Dézippez la dans ``/home/myuser/`` (``unzip X.Y.Z.zip``)
* Renommer le répertoire ``mv gn_module_dashboard-X.Y.Z gn_module_dashboard``
* Placez-vous dans le répertoire ``backend`` de GeoNature et lancez les commandes ``source venv/bin/activate`` puis ``geonature install_gn_module <mon_chemin_absolu_vers_le_module> <url_relative_du_module>`` pour installer le module (exemple ``geonature install_gn_module /home/`whoami`/gn_module_dashboard /dashboard``)
* Complétez la configuration du module dans le fichier ``config/conf_gn_module.toml`` à partir des paramètres présents dans ``config/conf_gn_module.toml.example``, dont vous pouvez surcoucher les valeurs par défaut. Relancez la mise à jour de la configuration depuis le répertoire ``geonature/backend`` avec les commandes ``source venv/bin/activate`` puis ``geonature update_module_configuration DASHBOARD``
* Vous pouvez sortir du venv en lançant la commande ``deactivate``

Configuration
=============

Un certain nombre de paramètres permettent de customiser le module en modifiant le fichier ``conf/conf_gn_module.toml`` (vous pouvez vous inspirer du fichier ``conf_gn_module.toml.example`` qui liste l'ensemble des paramètres disponibles et leurs valeurs par défaut) :

- Paramétrage du niveau de simplification des zonages sur la carte "Synthèse par entité géographique" : ``SIMPLIFY_LEVEL``. Passer un nombre entier : plus cet entier est grand et plus la simplification est importante. Ce paramètre est nécessaire pour alléger le temps d'affichage des zonages.
- Paramétrage des zonages affichables sur la carte "Synthèse par entité géographique" : ``AREA_TYPE``. Passer un tableau de ``type_code`` (table ``ref_geo.bib_areas_types``). La première valeur de ce tableau sera la valeur utilisée par défaut pour le graphique de synthèse par entité géographique.
- Paramétrage du nombre de classes sur la carte "Synthèse par entité géographique" : ``BORNE_OBS`` (mode 'nombre d'observations') et ``BORNE_TAXON`` (mode 'nombre de taxons'). Passer un tableau contenant les limites inférieures des bornes que l'on souhaite implémenter. 
- Paramétrage de l'affichage des graphiques du dashboard : ``DISPLAY_XXXX_GRAPH``. Renseigner 'true' pour afficher le graphique en question et 'false' pour le masquer. 
- Paramétrage de par défaut du graphique synthèse par entité géographique du dashboard : ``DISPLAY_NBOBS_LEGEND_BY_DEFAULT_IN_GEO_GRAPH`` Renseigner 'true' si vous souhaitez afficher par défault les observations, 'false' si vous souhaitez les taxons

Vues matérialisées
==================

Dans un soucis de performance, des vues matérialisées ont été mises en place. Elles sont renseignées lors de l'installation du module. Il faut rafraichir régulièrement ces vues matérialisées avec la fonction ``REFRESH MATERIALIZED VIEW`` pour prendre en compte les nouvelles données intégrées dans la Synthèse.

Une fonction permet de mettre à jour toutes les vues matérialisées du schéma ``gn_dashboard``.

* Pour lancer manuellement cette fonction, ouvrez une console SQL et exécutez la requête suivante :

  ::

        SELECT gn_dashboard.refresh_materialized_view_data();

* Pour automatiser l'éxecution de cette fonction (toutes les heures dans cet exemple), ajoutez la dans le crontab de l'utilisateur ``postgres`` :

  ::

        sudo su postgres
        crontab -e


Ajouter la ligne suivante pour effectuer un raffraichissement journalier à minuit :

::

    00 00 * * * psql -d geonature2db -c "SELECT gn_dashboard.refresh_materialized_view_data();"

Pour enregistrer et sortir : ``Ctrl + O``, ENTER puis ``Ctrl + X``


Mise à jour du module
=====================

- Téléchargez la nouvelle version du module

  ::
  
        wget https://github.com/PnX-SI/gn_module_dashboard/archive/X.Y.Z.zip
        unzip X.Y.Z.zip
        rm X.Y.Z.zip
  

- Renommez l'ancien et le nouveau répertoire

  ::
  
        mv /home/`whoami`/gn_module_dashboard /home/`whoami`/gn_module_dashboard_old
        mv /home/`whoami`/gn_module_dashboard-X.Y.Z /home/`whoami`/gn_module_dashboard


- Rappatriez le fichiers de configuration

  ::
        
        cp /home/`whoami`/gn_module_dashboard_old/config/conf_gn_module.toml /home/`whoami`/gn_module_dashboard/config/conf_gn_module.toml


- Relancer la compilation en mettant à jour la configuration

  ::
        
        cd /home/`whoami`/geonature/backend
        source venv/bin/activate
        geonature update_module_configuration DASHBOARD



Licence
=======

* OpenSource - GPL-3.0
* Copyleft 2019 - Parc National des Écrins

.. image:: http://geonature.fr/img/logo-pne.jpg
    :target: http://www.ecrins-parcnational.fr
