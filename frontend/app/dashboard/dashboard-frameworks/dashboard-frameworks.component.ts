import { Component, OnInit, ViewChild } from '@angular/core';
import { FormControl } from '@angular/forms';
import { ChartConfiguration, ChartOptions } from 'chart.js';

// Services
import { DataService } from '../services/data.services';

@Component({
  selector: 'dashboard-frameworks',
  templateUrl: 'dashboard-frameworks.component.html',
  styleUrls: ['./dashboard-frameworks.component.scss'],
})
export class DashboardFrameworksComponent implements OnInit {
  chart;
  public afForm = new FormControl([]);
  public distinctYear = new Set();
  // Dictionnaire contenant les options à implémenter sur le graphe
  public lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        title: {
          display: true,
          text: 'Années',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Nb Obs.',
        },
      },
    },
  };

  public chartData = {
    datasets: [],
    labels: [],
  };
  public colors = [];

  constructor(public dataService: DataService) {}

  ngOnInit(): void {
    // generate random colors
    [...Array(100)].forEach((el, index) => {
      this.colors.push(this.dynamicColors());
    });
  }

  dynamicColors() {
    var r = Math.floor(Math.random() * 255);
    var g = Math.floor(Math.random() * 255);
    var b = Math.floor(Math.random() * 255);
    return 'rgb(' + r + ',' + g + ',' + b + ')';
  }

  searchAF() {
    this.chartData.datasets = [];
    this.chartData.labels = [];
    this.distinctYear = new Set();

    if (this.afForm.value.length > 0) {
      this.dataService.getDataFrameworks(this.afForm.value).subscribe((afs) => {
        afs.forEach((af, index) => {
          this.chartData.datasets.push({
            data: af.data.map((el) => {
              this.distinctYear.add(el.year);
              return {
                x: el.year.toString(),
                y: el.nb_obs,
              };
            }),
            label: af.acquisition_framework_name,
            backgroundColor: this.colors[index],
            // backgroundColor: null,
          });
        });
        this.chartData.labels = Array.from(this.distinctYear)
          .sort()
          .map((el) => el.toString());

        this.chartData = Object.assign({}, this.chartData);
      });
    } else {
      // clear the form if no AF asked
      this.chartData = Object.assign({}, this.chartData);
    }
  }
}
