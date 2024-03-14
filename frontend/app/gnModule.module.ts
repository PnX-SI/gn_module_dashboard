import { NgModule } from '@angular/core';
import { GN2CommonModule } from '@geonature_common/GN2Common.module';
import { Routes, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { MatTabsModule } from '@angular/material/tabs';
import { NgChartsModule } from 'ng2-charts';
import { HttpClient } from '@angular/common/http';
import { MatSliderModule } from '@angular/material/slider';

// Components
import { DashboardComponent } from './dashboard/dashboard.component';
import { DashboardMapsComponent } from './dashboard/dashboard-maps/dashboard-maps.component';
import { DashboardHistogramComponent } from './dashboard/dashboard-histogram/dashboard-histogram.component';
import { DashboardTaxonomyComponent } from './dashboard/dashboard-taxonomy/dashboard-taxonomy.component';
import { DashboardFrameworksComponent } from './dashboard/dashboard-frameworks/dashboard-frameworks.component';
import { DashboardRecontactComponent } from './dashboard/dashboard-recontact/dashboard-recontact.component';
import { AnnualReportComponent } from './dashboard/annual_report/annual_report.component';
// Services
import { DataService } from './dashboard/services/data.services';
import { MapService } from '@geonature_common/map/map.service';

// my module routing
const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'maps', component: DashboardMapsComponent },
  { path: 'histogram', component: DashboardHistogramComponent },
  { path: 'piechart', component: DashboardTaxonomyComponent },
  { path: 'linechart', component: DashboardFrameworksComponent },
  { path: 'annual_report', component: AnnualReportComponent },
];

@NgModule({
  declarations: [
    DashboardComponent,
    DashboardMapsComponent,
    DashboardHistogramComponent,
    DashboardTaxonomyComponent,
    DashboardFrameworksComponent,
    DashboardRecontactComponent,
    AnnualReportComponent,
  ],
  imports: [
    GN2CommonModule,
    RouterModule.forChild(routes),
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatTabsModule,
    NgChartsModule,
    MatSliderModule,
  ],
  providers: [DataService, MapService, HttpClient],
  bootstrap: [DashboardComponent],
})
export class GeonatureModule {}
