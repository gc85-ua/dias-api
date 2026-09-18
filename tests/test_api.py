from datetime import date, datetime
from unittest.mock import patch
from urllib.parse import quote

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.services import (
    Festivo,
    FestivosResponse,
    Laborables,
    LaborablesResponse,
)

client = TestClient(app, raise_server_exceptions=False)


class TestHealthCheck:
    def test_ping_returns_pong(self):
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.json() == {"message": "pong"}

    def test_root_redirects_to_docs(self):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/docs" in response.headers["location"]


class TestLaborablesEndpoint:
    @patch("app.api.v1.endpoints.laborables.gl")
    def test_get_laborables_success(self, mock_gl):
        laborables = Laborables(
            enero=22, febrero=20, marzo=22, abril=21,
            mayo=22, junio=21, julio=22, agosto=22,
            septiembre=21, octubre=23, noviembre=20, diciembre=22, total=258
        )
        mock_gl.return_value = LaborablesResponse(
            año=2024, municipio="Madrid",
            fuente="https://example.com", laborables=laborables
        )

        encoded = quote("Madrid")
        response = client.get(f"/v1/laborables/?municipio={encoded}&año=2024")

        assert response.status_code == 200
        data = response.json()
        assert data["año"] == 2024
        assert data["municipio"] == "Madrid"
        assert "laborables" in data
        assert data["laborables"]["total"] == 258
        mock_gl.assert_called_once_with(year=2024, location="Madrid")

    @patch("app.api.v1.endpoints.laborables.gl")
    def test_get_laborables_default_year(self, mock_gl):
        laborables = Laborables(
            enero=22, febrero=20, marzo=22, abril=21,
            mayo=22, junio=21, julio=22, agosto=22,
            septiembre=21, octubre=23, noviembre=20, diciembre=22, total=258
        )
        mock_gl.return_value = LaborablesResponse(
            año=2026, municipio="Barcelona",
            fuente="https://example.com", laborables=laborables
        )

        encoded = quote("Barcelona")
        response = client.get(f"/v1/laborables/?municipio={encoded}")

        assert response.status_code == 200
        data = response.json()
        assert data["año"] == 2026
        mock_gl.assert_called_once_with(year=datetime.now(tz=__import__('datetime').UTC).year, location="Barcelona")

    @patch("app.api.v1.endpoints.laborables.gl")
    def test_get_laborables_not_found(self, mock_gl):
        from app.exceptions import LocationNotFoundError
        mock_gl.side_effect = LocationNotFoundError("NonExistentCity")

        encoded = quote("NonExistentCity")
        response = client.get(f"/v1/laborables/?municipio={encoded}&año=2024")

        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "LOCATION_NOT_FOUND"
        assert data["message"] == "The requested location was not found."


class TestFestivosEndpoint:
    @patch("app.api.v1.endpoints.festivos.gf")
    def test_get_festivos_success(self, mock_gf):
        festivos = [
            Festivo(fecha=date(2024, 1, 1), nombre="Año Nuevo", tipo="nacional"),
            Festivo(fecha=date(2024, 1, 6), nombre="Día de Reyes", tipo="nacional"),
        ]
        mock_gf.return_value = FestivosResponse(
            año=2024, municipio="Madrid",
            fuente="https://example.com", festivos=festivos
        )

        encoded = quote("Madrid")
        response = client.get(f"/v1/festivos/?municipio={encoded}&año=2024")

        assert response.status_code == 200
        data = response.json()
        assert data["año"] == 2024
        assert data["municipio"] == "Madrid"
        assert len(data["festivos"]) == 2
        assert data["festivos"][0]["nombre"] == "Año Nuevo"
        mock_gf.assert_called_once_with(year=2024, location="Madrid")

    @patch("app.api.v1.endpoints.festivos.gf")
    def test_get_festivos_default_year(self, mock_gf):
        mock_gf.return_value = FestivosResponse(
            año=2026, municipio="Sevilla",
            fuente="https://example.com", festivos=[]
        )

        encoded = quote("Sevilla")
        response = client.get(f"/v1/festivos/?municipio={encoded}")

        assert response.status_code == 200
        data = response.json()
        assert data["año"] == 2026
        mock_gf.assert_called_once()

    @patch("app.api.v1.endpoints.festivos.gf")
    def test_get_festivos_not_found(self, mock_gf):
        from app.exceptions import LocationNotFoundError
        mock_gf.side_effect = LocationNotFoundError("NonExistentCity")

        encoded = quote("NonExistentCity")
        response = client.get(f"/v1/festivos/?municipio={encoded}&año=2024")

        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "LOCATION_NOT_FOUND"
        assert data["message"] == "The requested location was not found."

    @patch("app.api.v1.endpoints.festivos.gf")
    def test_get_festivos_empty_list(self, mock_gf):
        mock_gf.return_value = FestivosResponse(
            año=2024, municipio="Madrid",
            fuente="https://example.com", festivos=[]
        )

        encoded = quote("Madrid")
        response = client.get(f"/v1/festivos/?municipio={encoded}&año=2024")

        assert response.status_code == 200
        data = response.json()
        assert data["festivos"] == []
