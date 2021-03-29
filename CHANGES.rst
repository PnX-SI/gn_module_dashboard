=========
CHANGELOG
=========

1.0.0 (2021-03-29)
------------------

**🚀 Nouveautés**

* Création d'une commande geonature de rafraichissement des VML
* Automatisation du rafraichissement des VM via un cron et la commande créé ci-dessus
* Préchargement des graphiques
* Possibilité d'afficher/masquer certains graphiques
* Paramètre pour configurer le type d'entité géographique par défaut
* Implémentation des classes dynamiques 
* Possibilité de configurer le graphique par défaut de "synthèse par entité géographique" (taxons ou observations)

**🐛 Corrections**

* Correction année du slider en dur
* Utilisation de la librairie utils-sqla

**Note de version**

Si vous faites une mise à jour du module. Vous pouvez mettre en place le cron. Ouvrez le fichier crontab: `crontab -e` et copiez la ligne suivante: 
```
* * * * SUN /home/theo/workspace/GeoNature/backend/venv/bin/geonature gn_dashboard_refresh_vm # gn_dashboard cron job
```

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
