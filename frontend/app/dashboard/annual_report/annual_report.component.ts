import { Component, OnInit, ViewChildren } from '@angular/core';
import { FormControl } from '@angular/forms';
import { DataService, YearRecap } from '../services/data.services';
import { BaseChartDirective } from 'ng2-charts';
import DatalabelsPlugin from 'chartjs-plugin-datalabels';

@Component({
  selector: 'dashboard-annual-report',
  templateUrl: 'annual_report.component.html',
  styleUrls: ['./annual_report.component.scss'],
})
export class AnnualReportComponent implements OnInit {
  public data: YearRecap;
  public dataLoading = true;
  public yearObsLabel: Array<any> = [];
  public yearObsData = [];
  public barChartOptions = {
    responsive: true,
    plugins: {
      labels: [],
    },
  };
  public obsByGroupData = [
    {
      data: [],
    },
  ];
  public obsByGroupLabel = [];
  public obsByGroupColor = [{ backgroundColor: [], borderWidth: 0.8 }];

  public newSpeciesData = [
    {
      data: [],
    },
  ];
  public newSpeciesLabel = [];
  public newSpeciesColors = [];
  public pieChartPlugins = [DatalabelsPlugin];

  public pieChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'left',
      },
      datalabels: {
        labels: {
          label: {
            color: 'black',
            font: {
              weight: 'bold',
            },
          },
        },
        formatter: (value, ctx) => {
          if (ctx.chart.data.labels) {
            const total = ctx.chart.data.datasets[0].data.reduce((acc, prev) => acc + prev);
            return Math.round((value / total) * 100) + '%';
          }
        },
      },
    },
  };

  public currentYearForm;
  public yearsDataForm: Array<number> = [new Date().getFullYear()];

  @ViewChildren(BaseChartDirective) charts: Array<BaseChartDirective>;

  constructor(private _api: DataService) {}

  ngOnInit() {
    this.currentYearForm = new FormControl(new Date().getFullYear());
    this.loadReport(new Date().getFullYear());
    this.currentYearForm.valueChanges.subscribe((year) => {
      this.refreshGraphValues();
      (this.charts as any)._results.forEach((element) => {
        element.chart.update();
      });
      this.loadReport(year, false);
    });
  }

  randomNum = () => Math.floor(Math.random() * (235 - 52 + 1) + 52);

  randomRGB = () => `rgb(${this.randomNum()}, ${this.randomNum()}, ${this.randomNum()})`;

  loadReport(year, loadyearPlot = true) {
    this.dataLoading = true;
    this._api.getAnnualReport(year).subscribe((data) => {
      this.dataLoading = false;
      this.yearsDataForm = data.yearsWithObs.map((el) => el.year);

      this.data = data;
      if (loadyearPlot) {
        const temp = [];
        this.data.observations_by_year.forEach((element) => {
          temp.push(element.count);
          this.yearObsLabel.push(element.year_);
        });
        this.yearObsData = [{ data: temp, label: "Nombre d'observations" }];
      }
      this.data.observations_by_group.forEach((element) => {
        this.obsByGroupLabel.push(element.group2_inpn);
        this.obsByGroupData[0].data.push(element.count);
        // this.obsByGroupColor[0]["backgroundColor"].push(this.randomRGB());
      });

      const tempNewSpecies = {};
      this.data.new_species.forEach((element) => {
        if (element.group2_inpn in tempNewSpecies) {
          tempNewSpecies[element.group2_inpn] += 1;
        } else {
          tempNewSpecies[element.group2_inpn] = 1;
        }
        if (element.group3_inpn in tempNewSpecies) {
          tempNewSpecies[element.group3_inpn] += 1;
        } else {
          tempNewSpecies[element.group3_inpn] = 1;
        }
      });
      const randomColor = [];
      for (let group in tempNewSpecies) {
        this.newSpeciesLabel.push(group);
        this.newSpeciesData[0].data.push(tempNewSpecies[group]);
        randomColor.push(this.randomRGB());
      }

      (this.charts as any)._results.forEach((element) => {
        element.chart.update();
      });
    });
  }

  refreshGraphValues() {
    this.obsByGroupData = [
      {
        data: [],
      },
    ];
    this.obsByGroupLabel = [];
    this.newSpeciesData = [
      {
        data: [],
      },
    ];
    this.newSpeciesLabel = [];
  }
}
