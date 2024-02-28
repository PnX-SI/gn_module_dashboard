import {
  Component,
  OnInit,
  OnChanges,
  AfterViewInit,
  Input,
  ViewEncapsulation,
} from "@angular/core";
import { FormBuilder, FormGroup, FormControl } from "@angular/forms";
import { MapService } from "@geonature_common/map/map.service";
// Services
import { DataService } from "../services/data.services";
import { distinctUntilChanged, skip } from "@librairies/rxjs/operators";
import { ConfigService } from "@geonature/services/config.service";

@Component({
  selector: "dashboard-maps",
  templateUrl: "dashboard-maps.component.html",
  // encapsulation: ViewEncapsulation.None,
  styleUrls: ["./dashboard-maps.component.scss"],
})
export class DashboardMapsComponent
  implements OnInit, OnChanges, AfterViewInit
{
  // Tableau contenant la géométrie et les données des zonages
  public myAreas: Array<any>;
  public myAreas_length: any;

  // Fonction permettant d'afficher les zonages sur la carte (leaflet)
  public showData = function (feature: any, layer: any) {};
  // Degré de simplication des zonages
  public simplifyLevel = null;
  // Couleurs de bordure des zonages
  public initialBorderColor = "rgb(255, 255, 255)";
  public selectedBorderColor = "rgb(50, 50, 50)";
  // Couleurs de remplissage des zonages pour la représentation en nombre d'observations
  public obsColors = null;
  // Couleurs de remplissage des zonages pour la représentation en nombre de taxons
  public taxColors = null;
  // Encart pour la légende de la carte
  public legend: any;
  // Légende pour la représentation en nombre d'observations
  public divLegendObs: any;
  // Légende pour la représentation en nombre de taxons
  public divLegendTax: any;
  // Chaîne de caractères permettant de gérer le contenu de la légende dynamiquement
  public introLegend = "Placez la souris sur un zonage";
  // Stocker le type de représentation qui a été sélectionné en dernier #1 nb d'observations #2 nb de taxons
  public currentMap = 1; // par défaut, la carte affiche automatiquement le nombre d'observations
  // Stocker le nom du zonage sur lequel la souris est posée
  public currentArea: any;
  // Stocker le nb d'observations du zonage sur lequel la souris est posée
  public currentNbObs: any;
  // Stocker le nb de taxons du zonage sur lequel la souris est posée
  public currentNbTax: any;
  // Stocker le cd_ref du taxon qui a été sélectionné en dernier
  public currentCdRef: any;
  // Gestion du formulaire général
  mapForm: FormGroup;
  @Input() taxonomies: any;
  @Input() yearsMinMax: any;
  public yearRange = [0, new Date().getFullYear()]; // Calcul du range de dates, de 0 à aujourd'hui
  public filtersDict: any;
  public filter: any;
  public disabledTaxButton = false;
  public tabAreasTypes: Array<any>;

  // Gestion du formulaire contrôlant le type de zonage
  public areaTypeControl = null;
  public currentTypeCode = null; // par défaut, la carte affiche la première géographie AREA_TYPE renseignée

  // Pouvoir stoppper le chargement des données si un changement de filtre est opéré avant la fin du chargement
  public subscription: any;
  // Gestion du spinner
  public spinner = true;

  // Récupérer la liste des taxons existants dans la BDD pour permettre la recherche de taxon (pnx-taxonomy)
  public taxonApiEndPoint = null;

  // Réupération des paramètres de configuration
  public NB_CLASS_OBS = null;
  public NB_CLASS_TAX = null;
  public displayNBOBSbydefault = null;

  // Initiatialisation des tableaux vides qui contiendront les bornes des classes. Pour les observations et pour les taxons
  public gradesObs: number[] = new Array(this.NB_CLASS_OBS);
  public gradesTax: number[] = new Array(this.NB_CLASS_TAX);

  // Initialisation de variables qui récupéreront le maximum d'observation ou de taxon par entité géographique
  public maxTaxa: any;
  public maxObs: any;

  constructor(
    public dataService: DataService,
    public fb: FormBuilder,
    public mapService: MapService,
    public config: ConfigService
  ) {
    this.simplifyLevel = this.config.DASHBOARD.SIMPLIFY_LEVEL;
    this.obsColors = this.config.DASHBOARD.OBSCOLORS;
    this.taxColors = this.config.DASHBOARD.TAXCOLORS;
    this.areaTypeControl = new FormControl(this.config.DASHBOARD.AREA_TYPE[0]);
    this.currentTypeCode = this.config.DASHBOARD.AREA_TYPE[0];
    this.NB_CLASS_OBS = this.config.DASHBOARD.NB_CLASS_OBS;
    this.NB_CLASS_TAX = this.config.DASHBOARD.NB_CLASS_TAX;
    this.displayNBOBSbydefault =
      this.config.DASHBOARD.DISPLAY_NBOBS_LEGEND_BY_DEFAULT_IN_GEO_GRAPH;

    this.taxonApiEndPoint = `${this.config.API_ENDPOINT}/synthese/taxons_autocomplete`;
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////COMPOSANTS///////////////////////////////////////////////////
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////

  ngOnInit() {
    // Déclaration du formulaire général contenant les filtres de la carte
    this.mapForm = this.fb.group({
      yearStart: this.fb.control(this.yearsMinMax[0]),
      yearEnd: this.fb.control(this.yearsMinMax[this.yearsMinMax.length - 1]),
      selectedFilter: this.fb.control(null),
      selectedRegne: this.fb.control(null),
      selectedPhylum: this.fb.control(null),
      selectedClasse: this.fb.control(null),
      selectedOrdre: this.fb.control(null),
      selectedFamille: this.fb.control(null),
      selectedGroup1INPN: this.fb.control(null),
      selectedGroup2INPN: this.fb.control(null),
      selectedGroup3INPN: this.fb.control(null),
      taxon: this.fb.control(null),
    });
    console.log(this.yearRange);

    this.currentMap = this.displayNBOBSbydefault ? 1 : 2;
  }

  ngAfterViewInit() {
    // Accès aux données de synthèse
    this.loadData();

    // Récupération des noms de type_area qui seront contenus dans la liste déroulante du formulaire areaTypeControl
    this.dataService
      .getAreasTypes(this.config.DASHBOARD.AREA_TYPE)
      .subscribe((data) => {
        // Création de la liste déroulante
        this.tabAreasTypes = data;
      });

    // Abonnement à la liste déroulante du formulaire areaTypeControl afin de modifier le type de zonage à chaque changement
    this.areaTypeControl.valueChanges
      .pipe(
        distinctUntilChanged(), // le [disableControl] du HTML déclenche l'API sans fin
        skip(1)
      ) // l'initialisation de la liste déroulante sur "Communes" lance l'API une fois
      .subscribe((value) => {
        this.spinner = true;
        this.currentTypeCode = value;
        // Accès aux données de synthèse
        this.loadData();
      });
  }

  ngOnChanges(change) {
    // Récupération des années min et max présentes dans la synthèse de GeoNature
    if (change.yearsMinMax && change.yearsMinMax.currentValue != undefined) {
      this.yearRange = change.yearsMinMax.currentValue;
    }
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////////////////
  ///////////////////////////////////////////////FONCTIONS///////////////////////////////////////////////////
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////

  loadData() {
    console.log(this.filtersDict);

    this.dataService
      .getDataAreas(this.simplifyLevel, this.currentTypeCode, this.filtersDict)
      .subscribe((data) => {
        this.myAreas = data;

        this.maxTaxa = Math.max(
          ...data.features.map((o) => o.properties.nb_taxons),
          0
        ); // à mettre dans la fonction legend tax
        this.maxObs = Math.max(
          ...data.features.map((o) => o.properties.nb_obs),
          0
        ); // à mettre dans la fonction legend tax)

        if (this.NB_CLASS_TAX > this.maxTaxa) {
          this.gradesTax = new Array(this.maxTaxa);
        } else {
          this.gradesTax = new Array(this.NB_CLASS_TAX);
        }
        if (this.NB_CLASS_OBS > this.maxObs) {
          this.gradesObs = new Array(this.maxObs);
        } else {
          this.gradesObs = new Array(this.NB_CLASS_OBS);
        }

        this.createlegend_OBS(this.gradesObs.length, this.maxObs);
        this.createlegend_TAX(this.gradesTax.length, this.maxTaxa);

        // Initialisation de la fonction "showData" : la carte affichée par défaut dépend du choix de l'utilisateur.trice
        if (this.currentMap == 1) {
          this.showData = this.onEachFeatureNbObs;
        } else {
          this.showData = this.onEachFeatureNbTax;
        }

        if (this.legend) {
          this.legend.remove();
        }

        // Implémentation de la légende
        this.add_legend();
        this.spinner = false;
      });
  }

  //////////////////////////////////////////Relatives à la carte/////////////////////////////////////////////

  // Configuration de la carte relative au nombre d'observations
  onEachFeatureNbObs(feature, layer) {
    layer.setStyle({
      fillColor: this.getColorObs(feature.properties.nb_obs),
      color: this.initialBorderColor,
      fillOpacity: 0.9,
      weight: 1,
    });
    layer.on({
      mouseover: this.highlightFeature.bind(this),
      mouseout: this.resetHighlight.bind(this),
      click: this.zoomToFeature.bind(this),
    });
  }

  // Configuration de la carte relative au nombre de taxons
  onEachFeatureNbTax(feature, layer) {
    layer.setStyle({
      fillColor: this.getColorTax(feature.properties.nb_taxons),
      color: this.initialBorderColor,
      fillOpacity: 0.9,
      weight: 1,
    });
    layer.on({
      mouseover: this.highlightFeature.bind(this),
      mouseout: this.resetHighlight.bind(this),
      click: this.zoomToFeature.bind(this),
    });
  }

  //////////////////////////////////////////Relatives à la couleur/////////////////////////////////////////////

  // Couleurs de la carte relative au nombre d'observations
  getColorObs(obs) {
    var nb_classes = this.gradesObs.length;
    for (var i = 1; i < nb_classes; i++) {
      if (obs < this.gradesObs[i]) {
        return this.obsColors[nb_classes][i - 1];
      }
    }
    return this.obsColors[nb_classes][nb_classes - 1];
  }

  // Couleurs de la carte relative au nombre de taxons
  getColorTax(tax) {
    var nb_classes = this.gradesTax.length;
    for (var i = 1; i < nb_classes; i++) {
      if (tax < this.gradesTax[i]) {
        return this.taxColors[nb_classes][i - 1];
      }
    }
    return this.taxColors[nb_classes][nb_classes - 1];
  }

  //////////////////////////////////////////Relatives à la légende/////////////////////////////////////////////

  // Légende concernant le nombre de taxons
  createlegend_TAX(nb_classes, nb_taxa_area) {
    this.divLegendTax = this.mapService.L.DomUtil.create("div", "divLegend");
    this.divLegendTax.innerHTML += "<b>Nombre de taxons</b><br/>";
    if (nb_classes > nb_taxa_area) {
      nb_classes = nb_taxa_area;
      this.gradesTax = new Array(nb_classes);
      this.gradesTax[nb_classes] = nb_taxa_area;
    }
    for (var i = 0; i < nb_classes; i++) {
      this.gradesTax[i] = Math.trunc((i / nb_classes) * nb_taxa_area);
    }
    for (var i = 0; i < nb_classes; i++) {
      this.divLegendTax.innerHTML +=
        '<div class="row row-0"> <i style="background:' +
        this.getColorTax(this.gradesTax[i]) +
        '"></i>' +
        this.gradesTax[i] +
        (this.gradesTax[i + 1]
          ? "&ndash;" + (this.gradesTax[i + 1] - 1) + "</div>"
          : "+ </div>");
    }
  }

  // Légende concernant le nombre d'Obs
  createlegend_OBS(nb_classes, nb_obs_area) {
    this.divLegendObs = this.mapService.L.DomUtil.create("div", "divLegend");
    this.divLegendObs.innerHTML += "<b>Nombre d'observations</b><br/>";
    if (nb_classes > nb_obs_area) {
      nb_classes = nb_obs_area;
      this.gradesObs = new Array(nb_classes);
      this.gradesObs[nb_classes] = nb_obs_area;
    }
    for (var i = 0; i < nb_classes; i++) {
      this.gradesObs[i] = Math.trunc((i / nb_classes) * nb_obs_area);
    }
    for (var i = 0; i < nb_classes; i++) {
      this.divLegendObs.innerHTML +=
        '<div class="row row-0"> <i style="background:' +
        this.getColorObs(this.gradesObs[i]) +
        '"></i>' +
        this.gradesObs[i] +
        (this.gradesObs[i + 1]
          ? "&ndash;" + (this.gradesObs[i + 1] - 1) + "</div>"
          : "+ </div>");
    }
  }

  // Ajout de la légende lors de l'init
  add_legend() {
    this.legend = (this.mapService.L as any).control({
      position: "bottomright",
    });
    if (this.currentMap == 1) {
      this.legend.onAdd = (map) => {
        return this.divLegendObs;
      };
    } else {
      this.legend.onAdd = (map) => {
        return this.divLegendTax;
      };
    }
    this.legend.addTo(this.mapService.map);
  }

  // Afficher les données, configurations (couleurs) et légende relatives au nombre de taxons (switcher)
  changeMapToTax() {
    this.myAreas = Object.assign({}, this.myAreas);
    this.showData = this.onEachFeatureNbTax.bind(this);
    this.mapService.map.removeControl(this.legend);
    this.legend.onAdd = (map) => {
      return this.divLegendTax;
    };
    this.legend.addTo(this.mapService.map);
    this.currentMap = 2; // Permet d'afficher les informations de légende associées au nombre de taxons
  }

  // Afficher les données, configurations (couleurs) et légende relatives au nombre d'observations (switcher)
  changeMapToObs() {
    this.myAreas = Object.assign({}, this.myAreas);
    this.showData = this.onEachFeatureNbObs.bind(this);
    this.mapService.map.removeControl(this.legend);
    this.legend.onAdd = (map) => {
      return this.divLegendObs;
    };
    this.legend.addTo(this.mapService.map);
    this.currentMap = 1; // Permet d'afficher les informations de légende associées au nombre d'observations
  }

  //////////////////////////////////////////Relatives aux filtres/////////////////////////////////////////////

  // Rafraichissement des données en fonction des filtres renseignés par l'utilisateur
  onTaxFilterChange(event) {
    // Déterminer le type de filtre taxonomique qui a été sélectionné pour afficher la liste déroulante adéquate
    this.filter = event.target.value;
    // Réinitialiser l'ancien filtre qui a été sélectionné pour empêcher les erreurs de requête
    this.mapForm.controls["selectedGroup1INPN"].reset();
    this.mapForm.controls["selectedGroup2INPN"].reset();
    this.mapForm.controls["selectedGroup3INPN"].reset();
    this.mapForm.controls["selectedRegne"].reset();
    this.mapForm.controls["selectedPhylum"].reset();
    this.mapForm.controls["selectedClasse"].reset();
    this.mapForm.controls["selectedOrdre"].reset();
    this.mapForm.controls["selectedFamille"].reset();
    this.mapForm.controls["taxon"].reset();
    // Afficher les données d'origine si la valeur vaut ""
    if (this.filter == "") {
      // Accès aux données de synthèse
      this.loadData();
    }
  }

  getCurrentParameters(event) {
    this.spinner = true;
    this.disabledTaxButton = false;
    // Copie des éléments du formulaire pour pouvoir y ajouter cd_ref s'il s'agit d'un filtre par taxon
    this.filtersDict = Object.assign({}, this.mapForm.value);
    // S'il s'agit d'une recherche de taxon...
    if (this.filter == "Rechercher un taxon/une espèce...") {
      // Cas d'une nouvelle recherche de taxon
      if (event.item) {
        // Récupération du cd_ref
        var cd_ref = event.item.cd_ref;
        // Enregistrement du cd_ref pour un potentiel changement de période concernant un taxon
        this.currentCdRef = cd_ref;
        // L'affichage de la carte du nombre de taxons n'a pas de sens lorsqu'on a sélectionné un taxon en particulier
        this.changeMapToObs();
      }
      // Cas d'un changement de la période sur le slider
      else {
        // Récupération du cd_ref
        var cd_ref = this.currentCdRef;
      }
      // Ajout de cd_ref à la liste des paramètres de la requête
      this.filtersDict["taxon"] = cd_ref;
      // Impossibilité d'afficher la carte en mode "Nombre de taxons"
      this.disabledTaxButton = true;
    }
    // Accès aux données de synthèse
    this.loadData();
  }

  //////////////////////////////////////////Relatives à l'UX/////////////////////////////////////////////

  // Changer l'aspect du zonage lorsque la souris passe dessus
  highlightFeature(e) {
    const layer = e.target;
    layer.setStyle({
      color: this.selectedBorderColor,
      weight: 5,
      fillOpacity: 1,
    });
    layer.bringToFront();
    this.introLegend = null;
    this.currentArea = layer.feature.geometry.properties.area_name;
    if (this.currentMap == 1) {
      this.currentNbObs =
        "Nombre d'observations : " + layer.feature.geometry.properties.nb_obs;
    } else if (this.currentMap == 2) {
      this.currentNbTax =
        "Nombre de taxons : " + layer.feature.geometry.properties.nb_taxons;
    }
  }

  // Réinitialiser l'aspect du zonage lorsque la souris n'est plus dessus
  resetHighlight(e) {
    const layer = e.target;
    this.introLegend = "Placez la souris sur un zonage";
    this.currentArea = null;
    this.currentNbObs = null;
    this.currentNbTax = null;
    layer.setStyle({
      color: this.initialBorderColor,
      weight: 1,
      fillOpacity: 0.9,
    });
  }

  // Zoomer sur un zonage en cliquant dessus
  zoomToFeature(e) {
    this.mapService.map.fitBounds(e.target.getBounds());
  }
}
