=========
CHANGELOG
=========

1.2.0 (unreleased)
------------------

Nécessite la version 2.10.0 (ou plus) de GeoNature

**Evolutions**

- Compatibilité avec Angular version 12, mis à jour dans la version 2.10.0 de GeoNature (#38)
- Packaging du module (bien suivre les notes de version pour la MAJ)

**Note de version**

Suite au packaging du module, la MAJ necessite unbe procédure particulière.
- Téléchargez la nouvelle version du module

  ::
  
        wget https://github.com/PnX-SI/gn_module_dashboard/archive/X.Y.Z.zip
        unzip X.Y.Z.zip
        rm X.Y.Z.zip
  

- Renommez l'ancien et le nouveau répertoire

  ::
  
        mv /home/`whoami`/gn_module_dashboard /home/`whoami`/gn_module_dashboard_old
        mv /home/`whoami`/gn_module_dashboard-X.Y.Z /home/`whoami`/gn_module_dashboard

- Rapatriez le fichiers de configuration

  ::
        
        cp /home/`whoami`/gn_module_dashboard_old/config/conf_gn_module.toml /home/`whoami`/gn_module_dashboard/config/conf_gn_module.toml

- Réinstallez le module et redémarrez GeoNature

  ::
        cd /home/`whoami`/gn_module_dashboard
        pip install .
        geonature db stamp dashboard@head
        cd /home/`whoami`/geonature
        npm run build
        sudo systemctl restart geonature
        

- Stampez les migration SQL 

  ::

        geonature db stamp 
1.1.0 (2022-01-03)
-----------------

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

**Note de version**

Si vous faites une mise à jour du module :

* Dans le fichier ``config/conf_gn_module.toml``, remplacez les paramètres ``BORNE_TAXON`` et ``BORNE_OBS`` par ``NB_CLASS_OBS`` et ``NB_CLASS_TAX`` comme dans l'exemple (https://github.com/PnX-SI/gn_module_dashboard/blob/master/config/conf_gn_module.toml.example) 
* Vous pouvez mettre en place le cron de rafraîchissement des VM ou le mettre à jour. Ouvrez le fichier crontab (``crontab -e``) et copiez la ligne suivante en adaptant le chemin et éventuellement la fréquence d'exécution (tous les dimanches à minuit dans cet exemple) : 

::

    * * * * SUN /home/myuser/geonature/backend/venv/bin/geonature gn_dashboard_refresh_vm # gn_dashboard cron job

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
