import { Component, OnInit, ViewChild, Input } from "@angular/core";
import { FormBuilder, FormGroup } from "@angular/forms";
import { BaseChartDirective } from "ng2-charts";
import DatalabelsPlugin from "chartjs-plugin-datalabels";

// Services
import { DataService } from "../services/data.services";

@Component({
  selector: "dashboard-taxonomy",
  templateUrl: "dashboard-taxonomy.component.html",
  styleUrls: ["./dashboard-taxonomy.component.scss"],
})
export class DashboardTaxonomyComponent implements OnInit {
  @ViewChild(BaseChartDirective) chart: BaseChartDirective;

  // Type de graphe
  public pietype = "doughnut";
  public pieChartPlugins = [DatalabelsPlugin];

  // Tableau contenant les labels du graphe
  public pieChartLabels = [];
  // Tableau contenant les données du graphe
  public pieChartData = [
    {
      data: [],
      backgroundColor: [],
    },
  ];
  // Dictionnaire contenant les options à implémenter sur le graphe
  public pieChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: "top",
      },
      datalabels: {
        labels: {
          label: {
            color: "white",
            font: {
              weight: "bold",
            },
          },
        },
        formatter: (value, ctx) => {
          if (ctx.chart.data.labels) {
            const total = ctx.chart.data.datasets[0].data.reduce(
              (acc, prev) => acc + prev
            );
            const percentage = Math.round((value / total) * 100);
            return percentage < 5 ? null : percentage + "%";
          }
        },
      },
    },
  };

  // Gestion du formulaire
  pieChartForm: FormGroup;
  @Input() yearsMinMax: any;
  public yearRange = [0, new Date().getFullYear()];

  // Pouvoir stoppper le chargement des données si un changement de filtre est opéré avant la fin du chargement
  public subscription: any;
  public spinner = true;
  public colors = [];

  constructor(public dataService: DataService, public fb: FormBuilder) {
    // Déclaration du formulaire contenant les filtres du pie chart
  }

  ngOnInit() {
    this.pieChartForm = this.fb.group({
      yearStart: this.fb.control(null),
      yearEnd: this.fb.control(null),
      selectedFilter: this.fb.control(null),
    });
    // generate an a tab of random color
    [...Array(100)].forEach((el, index) => {
      this.colors.push(this.dynamicColors());
    });
    // Par défaut, le pie chart s'affiche au niveau du règne
    this.pieChartForm.controls["selectedFilter"].setValue("regne");
    // Initialisation de l'array des labels, paramètre du pie chart
    // this.pieChartLabels = this.taxonomies[this.currentTaxLevel];
    // Accès aux données de la VM vm_synthese
    this.subscription = this.dataService
      .getDataSynthesePerTaxLevel("regne")
      .subscribe((data) => {
        data.forEach((elt, index) => {
          this.pieChartData[0].data.push(elt.nb_obs);
          this.pieChartData[0].backgroundColor.push(this.colors[index]);
          this.pieChartLabels.push(elt.taxon);
        });
        this.chart.chart.update();
        this.spinner = false;
      });
  }

  ngOnChanges(change) {
    // Récupération des années min et max présentes dans la synthèse de GeoNature
    if (change.yearsMinMax && change.yearsMinMax.currentValue != undefined) {
      this.pieChartForm.patchValue({
        yearStart: change.yearsMinMax.currentValue[0],
        yearEnd:
          change.yearsMinMax.currentValue[
            change.yearsMinMax.currentValue.length - 1
          ],
      });
    }
  }
  dynamicColors() {
    var r = Math.floor(Math.random() * 255);
    var g = Math.floor(Math.random() * 255);
    var b = Math.floor(Math.random() * 255);
    return "rgb(" + r + "," + g + "," + b + ")";
  }

  // Rafraichissement des données en fonction des filtres renseignés par l'utilisateur
  getCurrentParameters(event) {
    this.subscription.unsubscribe();
    this.spinner = true;
    this.pieChartData[0].data = [];
    this.pieChartLabels = [];
    this.subscription = this.dataService
      .getDataSynthesePerTaxLevel(
        this.pieChartForm.get("selectedFilter").value,
        this.pieChartForm.value
      )
      .subscribe((data) => {
        data.forEach((elt, index) => {
          this.pieChartData[0].data.push(elt.nb_obs);
          this.pieChartData[0].backgroundColor.push(this.colors[index]);
          this.pieChartLabels.push(elt.taxon);
        });
        this.chart.chart.update();
        this.spinner = false;
      });
  }
}
