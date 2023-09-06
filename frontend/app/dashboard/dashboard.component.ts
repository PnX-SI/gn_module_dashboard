import { Component, OnInit, ViewEncapsulation } from "@angular/core";
import { Title } from "@angular/platform-browser";
// Services
import { DataService } from "./services/data.services";
import { MapService } from "@geonature_common/map/map.service";
import { ConfigService } from "@geonature/services/config.service";

// noinspection TypeScriptValidateJSTypes
@Component({
  selector: "dashboard",
  templateUrl: "dashboard.component.html",
  styleUrls: ["./dashboard.component.scss"],
})
export class DashboardComponent implements OnInit {
  public regnes = [];
  public phylum = [];
  public classes = [];
  public ordres = [];
  public familles = [];
  public group1INPN = [];
  public group2INPN = [];
  public taxonomies: { [taxLevel: string]: any } = {};
  public yearsMinMax: any;
  public distinctYears = [];

  public displaySynthesePerYear = null;
  public displaySyntheseGeo = null;
  public displaySyntheseTaxoRank = null;
  public displaySyntheseCA = null;
  public displaySyntheseTaxoContact = null;

  public showHistogram = false;
  public showMap = false;
  public showPieChart = false;
  public showLineChart = false;
  public showSpecies = false;

  constructor(
    title: Title,
    public dataService: DataService,
    private _mapService: MapService,
    public config: ConfigService
  ) {
    this.displaySynthesePerYear = this.config.DASHBOARD.DISPLAY_PER_YEAR_GRAPH;
    this.displaySyntheseGeo = this.config.DASHBOARD.DISPLAY_PER_GEO_GRAPH;
    this.displaySyntheseTaxoRank =
      this.config.DASHBOARD.DISPLAY_PER_TAXONOMIC_RANK_GRAPH;
    this.displaySyntheseCA = this.config.DASHBOARD.DISPLAY_PER_CA_GRAPH;
    this.displaySyntheseTaxoContact =
      this.config.DASHBOARD.DISPLAY_TAXONOMIC_CONTACTS_GRAPH;

    title.setTitle("GeoNature - Dashboard");
  }

  ngOnInit() {
    // Accès aux noms des différents règnes de la BDD GeoNature
    this.dataService.getTaxonomy("Règne").subscribe((data) => {
      data.forEach((elt) => {
        this.regnes.push(elt[0]);
      });
    });
    this.taxonomies["Règne"] = this.regnes;
    // Accès aux noms des différents phylum de la BDD GeoNature
    this.dataService.getTaxonomy("Phylum").subscribe((data) => {
      data.forEach((elt) => {
        this.phylum.push(elt[0]);
      });
    });
    this.taxonomies["Phylum"] = this.phylum;

    // Accès aux noms des différentes classes de la BDD GeoNature
    this.dataService.getTaxonomy("Classe").subscribe((data) => {
      data.forEach((elt) => {
        this.classes.push(elt[0]);
      });
    });
    this.taxonomies["Classe"] = this.classes;

    // Accès aux noms des différents ordres de la BDD GeoNature
    this.dataService.getTaxonomy("Ordre").subscribe((data) => {
      data.forEach((elt) => {
        this.ordres.push(elt[0]);
      });
    });
    this.taxonomies["Ordre"] = this.ordres;

    // Accès aux noms des différentes familles de la BDD GeoNature
    this.dataService.getTaxonomy("Famille").subscribe((data) => {
      data.forEach((elt) => {
        this.familles.push(elt[0]);
      });
    });
    this.taxonomies["Famille"] = this.familles;

    // Accès aux noms des différents groupes INPN de la BDD GeoNature
    this.dataService.getTaxonomy("Groupe INPN 1").subscribe((data) => {
      data.forEach((elt) => {
        this.group1INPN.push(elt[0]);
      });
    });
    this.taxonomies["Groupe INPN 1"] = this.group1INPN;
    this.dataService.getTaxonomy("Groupe INPN 2").subscribe((data) => {
      data.forEach((elt) => {
        this.group2INPN.push(elt[0]);
      });
    });
    this.taxonomies["Groupe INPN 2"] = this.group2INPN;

    const group3INPN = []
    this.dataService.getTaxonomy("Groupe INPN 3").subscribe((data) => {
      data.forEach((elt) => {
        group3INPN.push(elt[0]);
      });
    });
    this.taxonomies["Groupe INPN 3"] = group3INPN;

    // Accès aux années extrêmes de la BDD
    this.dataService.getYears().subscribe((data) => {
      this.yearsMinMax = data;
    });
    // Accès aux années extrêmes de la BDD
    this.dataService.getYears().subscribe((data) => {
      data.forEach((elt) => {
        this.distinctYears.push(elt);
      });
    });
  }

  hideHistogram(event) {
    this.showHistogram = !this.showHistogram;
  }
  hideMap(event) {
    this.showMap = !this.showMap;
    if (this._mapService?.map) {
      this._mapService.map.invalidateSize();
    }
  }
  hidePieChart(event) {
    this.showPieChart = !this.showPieChart;
  }
  hideLineChart(event) {
    this.showLineChart = !this.showLineChart;
  }
  hideSpecies(event) {
    this.showSpecies = !this.showSpecies;
  }
}
