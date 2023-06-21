Dashboard
=========

Module GeoNature permettant de proposer un tableau de bord contenant
plusieurs graphiques et cartes basés sur les données présentes dans la
synthèse de GeoNature.

Développé par Elsa Guilley, stagiaire au Parc national des Ecrins en 2019.

Démo vidéo :
<https://geonature.fr/docs/img/2019-09-GN-dashboard-0.1.0.gif>

**Fonctionnalités** :

-   Nombre d'observations et de taxons par année
-   Nombre d'observations et de taxons par zonage (communes, mailles...)
-   Répartition des observations par rang taxonomique
-   Nombre d'observations par cadre d'acquisition par année
-   Taxons recontactés, non recontactés et nouveaux par année
-   Filtres divers sur chaque élément

**Présentation** :

-   Rapport de stage de Elsa Guilley :
    <https://geonature.fr/documents/2019-09-rapport-stage-Elsa-Guilley-Dashboard-Validation.pdf>
-   Présentation de soutenance de stage de Elsa Guilley :
    <https://geonature.fr/documents/2019-09-soutenance-stage-Elsa-Guilley-Dashboard-Validation.pptx>

Installation
------------

- Téléchargez la dernière version stable du module
  ```bash
  wget https://github.com/PnX-SI/gn_module_dashboard/archive/X.Y.Z.zip
  ```
- Dézippez la dans `/home/myuser/` 
  ```bash
  unzip X.Y.Z.zip
  ```
- Renommer le répertoire
  ```bash
  mv gn_module_dashboard-X.Y.Z gn_module_dashboard
  ```
- Placez-vous dans le répertoire `backend` de GeoNature et lancez les commandes 
  ```bash
  source ~/geonature/backend/venv/bin/activate
  geonature install-gn-module ~/gn_module_dashboard DASHBOARD
  ```
- Vous pouvez sortir du venv
  ```bash
  deactivate
  ```
- Relancez GeoNature 
  ```bash
  sudo systemctl restart geonature
  ```

Configuration
-------------

Vous pouvez modifier la configuration du module en créant un fichier
`dashboard_config.toml` dans le dossier `config` de GeoNature, en vous inspirant 
du fichier `dashboard_config.toml.example` et en surcouchant les paramètres que vous souhaitez.

Pour appliquer les modifications de la configuration du module, consultez 
la [rubrique dédiée de la documentation de GeoNature](https://docs.geonature.fr/installation.html#module-config).

Détail des paramètres modifiables :

-   Paramétrage du niveau de simplification des zonages sur la carte
    "Synthèse par entité géographique" : `SIMPLIFY_LEVEL`. Passer un
    nombre entier : plus cet entier est grand et plus la simplification
    est importante. Ce paramètre est nécessaire pour alléger le temps
    d'affichage des zonages.
-   Paramétrage des zonages affichables sur la carte "Synthèse par
    entité géographique" : `AREA_TYPE`. Passer un tableau de
    `type_code` (table `ref_geo.bib_areas_types`). La première valeur de
    ce tableau sera la valeur utilisée par défaut pour le graphique de
    synthèse par entité géographique.
-   Paramétrage du nombre de classes sur la carte "Synthèse par entité
    géographique" : `NB_CLASS_OBS` (mode 'nombre d'observations') et
    `NB_CLASS_TAX` (mode 'nombre de taxons').
-   Paramétrage de l'affichage des graphiques du dashboard :
    `DISPLAY_XXXX_GRAPH`. Renseigner 'true' pour afficher le graphique
    en question et 'false' pour le masquer.
-   Paramétrage par défaut du graphique "Synthèse par entité
    géographique" du Dashboard :
    `DISPLAY_NBOBS_LEGEND_BY_DEFAULT_IN_GEO_GRAPH`. Renseigner 'true'
    si vous souhaitez afficher par défaut les observations, 'false'
    si vous souhaitez les taxons.

Vues matérialisées
------------------

Dans un soucis de performance, des vues matérialisées ont été mises en
place. Elles sont rafraichies automatiquement par Celery tous les jours à 2h du matin.  
Vous pouvez configurer la périodicité du rafraichissement via le paramètre
de configuration ``CRONTAB`` 
(syntaxe [crontab](https://crontab.guru/), ``CRONTAB=""`` pour désactiver).

Vous pouvez également mettre à jour manuellement les vues matérialisées :

```bash
source ~/geonature/backend/venv/bin/activate
geonature dashboard refresh-vm
```

Cette commande lance la requête SQL suivante :

```sql
SELECT gn_dashboard.refresh_materialized_view_data()
```

Mise à jour du module
---------------------

-   Téléchargez la nouvelle version du module

        wget https://github.com/PnX-SI/gn_module_dashboard/archive/X.Y.Z.zip
        unzip X.Y.Z.zip
        rm X.Y.Z.zip

-   Renommez l'ancien et le nouveau répertoire

        mv ~/gn_module_dashboard ~/gn_module_dashboard_old
        mv ~/gn_module_dashboard-X.Y.Z ~/gn_module_dashboard

-   Si vous avez encore votre configuration du module dans le dossier `config` du module, 
    copiez le vers le dossier de configuration centralisée de GeoNature :

        cp ~/gn_module_dashboard_old/config/conf_gn_module.toml ~/geonature/config/dashboard_conf.toml

-   Lancez la mise à jour du module

        source ~/geonature/backend/venv/bin/activate
        geonature install-gn-module ~/gn_module_dashboard DASHBOARD
        sudo systemctl restart geonature

Licence
-------

-   OpenSource - GPL-3.0
-   Copyleft 2019-2023 - Parc National des Écrins

[![image](https://geonature.fr/img/logo-pne.jpg)](http://www.ecrins-parcnational.fr)
