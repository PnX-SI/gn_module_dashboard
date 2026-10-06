"""
Tests for dashboard blueprint endpoints
"""

import pytest
import json
from flask import url_for
from werkzeug.exceptions import Forbidden, Unauthorized, BadRequest

from geonature.utils.env import db
from geonature.core.gn_synthese.models import Synthese, VSyntheseForWebApp
from geonature.core.gn_meta.models import TDatasets
from ref_geo.models import BibAreasTypes, LAreas
from apptax.taxonomie.models import Taxref
from geonature.tests.utils import set_logged_user


@pytest.mark.usefixtures("client_class")
class TestDashboardEndpoints:
    """Test suite for dashboard blueprint endpoints"""

    def test_get_synthese_stat(self, synthese_data):
        """Test /synthese endpoint returns observation and taxa counts by year"""
        response = self.client.get(url_for("dashboard.get_synthese_stat"))
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "year" in data[0]
            assert "count_id_synthese" in data[0]
            assert "count_cd_ref" in data[0]

    def test_get_synthese_stat_with_filters(self, synthese_data):
        """Test /synthese endpoint with taxonomic filters"""
        response = self.client.get(
            url_for("dashboard.get_synthese_stat"),
            query_string={"selectedRegne": "Animalia"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_get_synthese_per_tax_level_stat(self, synthese_data):
        """Test /synthese_per_tax_level/<taxLevel> endpoint"""
        response = self.client.get(
            url_for("dashboard.get_synthese_per_tax_level_stat", taxLevel="classe")
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "taxon" in data[0]
            assert "nb_obs" in data[0]

    def test_get_synthese_per_tax_level_stat_with_year_filter(self, synthese_data):
        """Test /synthese_per_tax_level with year filters"""
        response = self.client.get(
            url_for("dashboard.get_synthese_per_tax_level_stat", taxLevel="classe"),
            query_string={"yearStart": "2020", "yearEnd": "2025"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_get_synthese_per_tax_level_invalid_attribute(self, synthese_data):
        """Test /synthese_per_tax_level with invalid taxLevel"""
        response = self.client.get(
            url_for("dashboard.get_synthese_per_tax_level_stat", taxLevel="invalid_level")
        )
        assert response.status_code == 400

    def test_get_frameworks_stat(self, synthese_data):
        """Test /frameworks endpoint returns observations by acquisition framework"""
        response = self.client.get(url_for("dashboard.get_frameworks_stat"))
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "acquisition_framework_name" in data[0]
            assert "data" in data[0]
            assert isinstance(data[0]["data"], list)

    def test_get_frameworks_stat_with_filter(self, synthese_data):
        """Test /frameworks endpoint with framework ID filter"""
        response = self.client.get(
            url_for("dashboard.get_frameworks_stat"),
            query_string={"id_acquisition_framework": [1]},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_get_recontact_stat(self, synthese_data):
        """Test /recontact/<year> endpoint returns recontact statistics"""
        response = self.client.get(url_for("dashboard.get_recontact_stat", year=2025))
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_get_recontact_stat_various_years(self, synthese_data):
        """Test /recontact for different years"""
        for year in [2020, 2022, 2025]:
            response = self.client.get(url_for("dashboard.get_recontact_stat", year=year))
            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data, list)
            assert len(data) == 3

    def test_get_taxonomy(self, synthese_data):
        """Test /taxonomy/<taxLevel> endpoint"""
        response = self.client.get(url_for("dashboard.get_taxonomy", taxLevel="classe"))
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_get_areas_types(self):
        """Test /areas_types endpoint returns area types"""
        response = self.client.get(url_for("dashboard.get_areas_types"))
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "type_code" in data[0]
            assert "type_name" in data[0]

    def test_get_areas_types_with_filter(self):
        """Test /areas_types endpoint with type_code filter"""
        response = self.client.get(
            url_for("dashboard.get_areas_types"),
            query_string={"type_code": ["COM"]},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        for area_type in data:
            assert area_type["type_code"] == "COM"

    def test_get_years(self, synthese_data):
        """Test /years endpoint returns available years with observations"""
        response = self.client.get(url_for("dashboard.get_years"))
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        for year in data:
            assert isinstance(year, int)

    def test_get_areas_stat_requires_permission(self, users):
        """Test /areas endpoint requires SYNTHESE read permission"""
        simplify_level = 10
        type_code = "COM"

        response = self.client.get(
            url_for(
                "dashboard.get_areas_stat",
                simplify_level=simplify_level,
                type_code=type_code,
            )
        )
        assert response.status_code == Unauthorized.code

        set_logged_user(self.client, users["admin_user"])
        response = self.client.get(
            url_for(
                "dashboard.get_areas_stat",
                simplify_level=simplify_level,
                type_code=type_code,
            )
        )
        assert response.status_code == 200

    def test_get_areas_stat_returns_geojson(self, users, synthese_data):
        """Test /areas endpoint returns valid GeoJSON FeatureCollection"""
        set_logged_user(self.client, users["admin_user"])
        simplify_level = 10
        type_code = "COM"

        response = self.client.get(
            url_for(
                "dashboard.get_areas_stat",
                simplify_level=simplify_level,
                type_code=type_code,
            )
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "type" in data
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        assert isinstance(data["features"], list)
        if len(data["features"]) > 0:
            feature = data["features"][0]
            assert "properties" in feature
            assert "area_name" in feature["properties"]
            assert "nb_obs" in feature["properties"]
            assert "nb_taxons" in feature["properties"]

    def test_get_areas_stat_with_year_filter(self, users, synthese_data):
        """Test /areas endpoint with year filters"""
        set_logged_user(self.client, users["admin_user"])
        simplify_level = 10
        type_code = "COM"

        response = self.client.get(
            url_for(
                "dashboard.get_areas_stat",
                simplify_level=simplify_level,
                type_code=type_code,
            ),
            query_string={"yearStart": "2020", "yearEnd": "2025"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["type"] == "FeatureCollection"

    def test_yearly_recap(self, synthese_data):
        """Test /report/<year> endpoint returns yearly report data"""
        response = self.client.get(url_for("dashboard.yearly_recap", year=2025))
        assert response.status_code == 200
        data = response.get_json()

        expected_fields = [
            "yearsWithObs",
            "year",
            "nb_obs_year",
            "nb_obs_total",
            "nb_new_species",
            "nb_taxon_year",
            "new_datasets",
            "new_species",
            "most_viewed_species",
            "observations_by_group",
            "data_by_datasets",
            "observations_by_year",
        ]
        for field in expected_fields:
            assert field in data

        assert data["year"] == "2025" or data["year"] == 2025
        assert isinstance(data["nb_obs_year"], (int, type(None)))
        assert isinstance(data["nb_obs_total"], (int, type(None)))
        assert isinstance(data["nb_new_species"], (int, type(None)))
        assert isinstance(data["new_species"], list)
        assert isinstance(data["most_viewed_species"], list)
        assert isinstance(data["observations_by_group"], list)
        assert isinstance(data["data_by_datasets"], list)
        assert isinstance(data["observations_by_year"], list)

    def test_yearly_recap_new_species_structure(self, synthese_data):
        """Test /report/<year> new_species field contains expected structure"""
        response = self.client.get(url_for("dashboard.yearly_recap", year=2025))
        assert response.status_code == 200
        data = response.get_json()

        if len(data["new_species"]) > 0:
            species = data["new_species"][0]
            assert "nom_complet" in species
            assert "nom_vern" in species
            assert "group2_inpn" in species

    def test_yearly_recap_most_viewed_species_structure(self, synthese_data):
        """Test /report/<year> most_viewed_species field contains expected structure"""
        response = self.client.get(url_for("dashboard.yearly_recap", year=2025))
        assert response.status_code == 200
        data = response.get_json()

        if len(data["most_viewed_species"]) > 0:
            species = data["most_viewed_species"][0]
            assert "nom_complet" in species
            assert "nom_vern" in species
            assert "group2_inpn" in species

    def test_yearly_recap_observations_by_year_structure(self, synthese_data):
        """Test /report/<year> observations_by_year contains count and year"""
        response = self.client.get(url_for("dashboard.yearly_recap", year=2025))
        assert response.status_code == 200
        data = response.get_json()

        if len(data["observations_by_year"]) > 0:
            obs_year = data["observations_by_year"][0]
            assert "count" in obs_year or "count_1" in obs_year
            assert "year_" in obs_year or "year" in obs_year

    def test_yearly_recap_various_years(self, synthese_data):
        """Test /report for different years"""
        for year in [2020, 2022, 2025]:
            response = self.client.get(url_for("dashboard.yearly_recap", year=year))
            assert response.status_code == 200
            data = response.get_json()
            assert data["year"] == str(year) or data["year"] == year


@pytest.mark.usefixtures("client_class")
class TestDashboardFilters:
    """Test suite for dashboard filter combinations"""

    def test_synthese_with_multiple_filters(self, synthese_data):
        """Test /synthese with multiple taxonomic filters"""
        response = self.client.get(
            url_for("dashboard.get_synthese_stat"),
            query_string={
                "selectedRegne": "Animalia",
                "selectedPhylum": "Chordata",
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_areas_stat_with_all_filters(self, users, synthese_data):
        """Test /areas endpoint with taxonomic and year filters"""
        set_logged_user(self.client, users["admin_user"])

        response = self.client.get(
            url_for("dashboard.get_areas_stat", simplify_level=10, type_code="COM"),
            query_string={
                "yearStart": "2020",
                "yearEnd": "2025",
                "selectedRegne": "Animalia",
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["type"] == "FeatureCollection"

    def test_get_areas_types_multiple_codes(self):
        """Test /areas_types with multiple type_code filters"""
        response = self.client.get(
            url_for("dashboard.get_areas_types"),
            query_string={"type_code": ["COM", "DEP"]},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
