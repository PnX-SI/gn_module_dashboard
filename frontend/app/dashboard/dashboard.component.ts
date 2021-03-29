import { Component, OnInit } from "@angular/core";
import { Title } from "@angular/platform-browser";
// Services
import { DataService } from "./services/data.services";
import { ModuleConfig } from "./../module.config";
import { MapService } from "@geonature_common/map/map.service";

@Component({
  selector: "dashboard",
  templateUrl: "dashboard.component.html",
  styleUrls: ['./dashboard.component.scss']
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

  public displaySynthesePerYear = ModuleConfig.DISPLAY_PER_YEAR_GRAPH;
  public displaySyntheseGeo = ModuleConfig.DISPLAY_PER_GEO_GRAPH;
  public displaySyntheseTaxoRank = ModuleConfig.DISPLAY_PER_TAXONOMIC_RANK_GRAPH; 
  public displaySyntheseCA = ModuleConfig.DISPLAY_PER_CA_GRAPH; 
  public displaySyntheseTaxoContact = ModuleConfig.DISPLAY_TAXONOMIC_CONTACTS_GRAPH;

  public showHistogram = false;
  public showMap = false;
  public showPieChart = false;
  public showLineChart = false;
  public showSpecies = false;

  constructor(title: Title, public dataService: DataService, private _mapService:MapService) {
    title.setTitle("GeoNature - Dashboard")
  }

  ngOnInit() {
    // Accès aux noms des différents règnes de la BDD GeoNature
    this.dataService.getTaxonomy("Règne").subscribe(
      (data) => {
        data.forEach(
          (elt) => {
            this.regnes.push(elt[0]);
          }
        );
      }
    );
    this.taxonomies["Règne"] = this.regnes;

    // Accès aux noms des différents phylum de la BDD GeoNature
    this.dataService.getTaxonomy("Phylum").subscribe(
      (data) => {
        data.forEach(
          (elt) => {
            this.phylum.push(elt[0]);
          }
        );
      }
    );
    this.taxonomies["Phylum"] = this.phylum;

    // Accès aux noms des différentes classes de la BDD GeoNature
    this.dataService.getTaxonomy("Classe").subscribe(
      (data) => {
        data.forEach(
          (elt) => {
            this.classes.push(elt[0]);
          }
        );
      }
    );
    this.taxonomies["Classe"] = this.classes;

    // Accès aux noms des différents ordres de la BDD GeoNature
    this.dataService.getTaxonomy("Ordre").subscribe(
      (data) => {
        data.forEach(
          (elt) => {
            this.ordres.push(elt[0]);
          }
        );
      }
    );
    this.taxonomies["Ordre"] = this.ordres;

    // Accès aux noms des différentes familles de la BDD GeoNature
    this.dataService.getTaxonomy("Famille").subscribe(
      (data) => {
        data.forEach(
          (elt) => {
            this.familles.push(elt[0]);
          }
        );
      }
    );
    this.taxonomies["Famille"] = this.familles;

    // Accès aux noms des différents groupes INPN de la BDD GeoNature
    this.dataService.getTaxonomy("Groupe INPN 1").subscribe(
      (data) => {
        data.forEach(
          (elt) => {
            this.group1INPN.push(elt[0]);
          }
        );
      }
    );
    this.taxonomies["Groupe INPN 1"] = this.group1INPN;
    this.dataService.getTaxonomy("Groupe INPN 2").subscribe(
      (data) => {
        data.forEach(
          (elt) => {
            this.group2INPN.push(elt[0]);
          }
        );
      }
    );
    this.taxonomies["Groupe INPN 2"] = this.group2INPN;

    // Accès aux années extrêmes de la BDD
    this.dataService.getYears("min-max").subscribe(
      (data) => {
        this.yearsMinMax = data[0];
      }
    );
    // Accès aux années extrêmes de la BDD
    this.dataService.getYears("distinct").subscribe(
      (data) => {
        data.forEach(
          (elt) => {
            this.distinctYears.push(elt[0]);
          }
        )
      }
    );
  }

  hideHistogram(event) {
    this.showHistogram = !this.showHistogram;
  }
  hideMap(event) {
    this.showMap = !this.showMap;
    this._mapService.map.invalidateSize();
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
