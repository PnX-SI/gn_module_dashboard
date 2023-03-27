import { Component, OnInit, ViewChild, Input } from "@angular/core";
import { FormBuilder, FormGroup } from "@angular/forms";
import { BaseChartDirective } from "ng2-charts";
import DatalabelsPlugin from "chartjs-plugin-datalabels";

// Services
import { DataService } from "../services/data.services";

@Component({
  selector: "dashboard-recontact",
  templateUrl: "dashboard-recontact.component.html",
  styleUrls: ["./dashboard-recontact.component.scss"],
})
export class DashboardRecontactComponent implements OnInit {
  @ViewChild(BaseChartDirective) chart: BaseChartDirective;

  // Type de graphe
  public pietype = "doughnut";
  public pieChartLabels = [
    "Taxons recontactés",
    "Taxons non recontactés",
    "Nouveaux taxons",
  ];
  public pieChartPlugins = [DatalabelsPlugin];

  public pieChartData = [
    {
      data: [],
      backgroundColor: [
        "rgb(119,163,53)",
        "rgb(217,146,30)",
        "rgb(43,132,183)",
      ],
      borderWidth: 0.8,
    },
  ];

  // Dictionnaire contenant les options à implémenter sur le graphe (calcul des pourcentages notamment)
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
            return Math.round((value / total) * 100) + "%";
          }
        },
      },
    },
  };

  // Gestion du formulaire
  recontactForm: FormGroup;
  @Input() distinctYears: any;

  // Pouvoir stoppper le chargement des données si un changement de filtre est opéré avant la fin du chargement
  public subscription: any;
  // Gestion du spinner
  public spinner = true;

  constructor(public dataService: DataService, public fb: FormBuilder) {
    // Déclaration du formulaire contenant les filtres du pie chart
    this.recontactForm = fb.group({
      selectedYear: fb.control(null),
    });
  }

  ngOnInit() {
    // Par défaut, le pie chart s'affiche sur l'année en court
    this.recontactForm.controls["selectedYear"].setValue(
      new Date().getFullYear()
    );
    // Accès aux données de synthèse
    this.spinner = true;
    this.subscription = this.dataService
      .getDataRecontact(this.recontactForm.value.selectedYear)
      .subscribe((data) => {
        // Remplissage de l'array des données à afficher, paramètre du line chart
        data.forEach((elt) => {
          this.pieChartData[0].data.push(elt);
        });
        this.spinner = false;
      });
  }

  // Rafraichissement des données en fonction de l'année renseignée par l'utilisateur
  getCurrentYear(event) {
    this.subscription.unsubscribe();
    this.spinner = true;
    // Réinitialisation de l'array des données à afficher, paramètre du pie chart
    var pieChartDataTemp = [];
    // Accès aux données de synthèse
    this.subscription = this.dataService
      .getDataRecontact(this.recontactForm.value.selectedYear)
      .subscribe((data) => {
        // Remplissage de l'array des données à afficher, paramètre du line chart
        data.forEach((elt) => {
          pieChartDataTemp.push(elt);
        });
        this.pieChartData[0].data = pieChartDataTemp;
        this.chart.chart.update();
        this.spinner = false;
      });
  }
}
