import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { ConfigService } from '@geonature/services/config.service';

export interface YearRecap {
  yearsWithObs: Array<any>;
  year: number;
  nb_obs_year: number;
  nb_obs_total: number;
  nb_new_species: number;
  nb_taxon_year: number;
  new_datasets: Array<any>;
  new_species: Array<any>;
  most_viewed_species: Array<any>;
  data_by_datasets: Array<any>;
  observations_by_year: Array<any>;
  observations_by_group: Array<any>;
}
@Injectable()
export class DataService {
  constructor(
    private httpClient: HttpClient,
    public config: ConfigService
  ) {}

  getDataSynthese(params?) {
    let queryString = new HttpParams();
    if (params) {
      for (const key in params) {
        if (params[key]) {
          queryString = queryString.set(key, params[key]);
        }
      }
    }
    return this.httpClient.get<any>(
      this.config.API_ENDPOINT + '/' + this.config.DASHBOARD.MODULE_URL + '/synthese',
      { params: queryString }
    );
  }

  getDataAreas(simplify_level, type_code, params?) {
    let queryString = new HttpParams();
    if (params) {
      for (const key in params) {
        if (params[key]) {
          queryString = queryString.set(key, params[key]);
        }
      }
    }
    return this.httpClient.get<any>(
      this.config.API_ENDPOINT +
        '/' +
        this.config.DASHBOARD.MODULE_URL +
        '/areas/' +
        simplify_level +
        '/' +
        type_code,
      { params: queryString }
    );
  }

  getDataSynthesePerTaxLevel(taxLevel, params?) {
    let queryString = new HttpParams();
    if (params) {
      for (const key in params) {
        if (params[key]) {
          queryString = queryString.set(key, params[key]);
        }
      }
    }
    return this.httpClient.get<any>(
      this.config.API_ENDPOINT +
        '/' +
        this.config.DASHBOARD.MODULE_URL +
        '/synthese_per_tax_level/' +
        taxLevel,
      { params: queryString }
    );
  }

  getDataFrameworks(idAfs: Array<number> = []) {
    let queryString = new HttpParams();
    idAfs.forEach((id, index) => {
      queryString = queryString.append('id_acquisition_framework', id.toString());
    });
    return this.httpClient.get<any>(
      this.config.API_ENDPOINT + '/' + this.config.DASHBOARD.MODULE_URL + '/frameworks',
      { params: queryString }
    );
  }

  getDataRecontact(year) {
    return this.httpClient.get<any>(
      this.config.API_ENDPOINT + '/' + this.config.DASHBOARD.MODULE_URL + '/recontact/' + year
    );
  }

  getTaxonomy(taxLevel) {
    return this.httpClient.get<any>(
      this.config.API_ENDPOINT + '/' + this.config.DASHBOARD.MODULE_URL + '/taxonomy/' + taxLevel
    );
  }

  getAreasTypes(types_codes: Array<string>) {
    let queryString = new HttpParams();
    types_codes.forEach((elt) => {
      queryString = queryString.append('type_code', elt);
    });
    return this.httpClient.get<any>(
      this.config.API_ENDPOINT + '/' + this.config.DASHBOARD.MODULE_URL + '/areas_types',
      { params: queryString }
    );
  }

  getYears() {
    return this.httpClient.get<any>(
      this.config.API_ENDPOINT + '/' + this.config.DASHBOARD.MODULE_URL + '/years'
    );
  }

  getAnnualReport(year) {
    return this.httpClient.get<YearRecap>(
      this.config.API_ENDPOINT + '/' + this.config.DASHBOARD.MODULE_URL + '/report/' + year
    );
  }
}
