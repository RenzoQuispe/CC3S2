"""
Casos de prueba para el mocking
"""

import json
import os
import sys

import pytest

# Agregar el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import Mock, patch

from requests import Response

from models import IMDb
from models.imdb import TIMEOUT, _enforce_policies


# Fixture para cargar los datos de IMDb desde un archivo JSON
@pytest.fixture(scope="session")
def imdb_data():
    """Carga las respuestas de IMDb necesarias para las pruebas"""
    current_dir = os.path.dirname(__file__)
    fixture_path = os.path.join(current_dir, "fixtures", "imdb_responses.json")
    with open(fixture_path) as json_data:
        data = json.load(json_data)
        print("Contenido de imdb_data:", data)  # Para depuración
        return data


class TestIMDbDatabase:
    """Casos de prueba para la base de datos de IMDb"""

    @pytest.fixture(autouse=True)
    def setup_class(self, imdb_data):
        """Configuración inicial para cargar los datos de IMDb"""
        self.imdb_data = imdb_data

    #  Casos de prueba

    @patch("models.imdb.requests.get")
    def test_search_titles_success(self, mock_get):
        """Prueba que la búsqueda de títulos retorna datos correctamente"""
        # Configurar el mock para devolver una respuesta exitosa
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = self.imdb_data["search_title"]
        mock_get.return_value = mock_response

        imdb = IMDb(apikey="fake_api_key")
        resultado = imdb.search_titles("Bambi")

        assert resultado == self.imdb_data["search_title"]
        mock_get.assert_called_once_with(
            "https://imdb-api.com/API/SearchTitle/fake_api_key/Bambi", timeout=TIMEOUT
        )

    @patch("models.imdb.requests.get")
    def test_search_titles_failure(self, mock_get):
        """Prueba que la búsqueda de títulos maneja errores correctamente"""
        # Configurar el mock para devolver una respuesta fallida con json retornando {}
        mock_response = Mock(spec=Response)
        mock_response.status_code = 404
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        imdb = IMDb(apikey="fake_api_key")
        resultado = imdb.search_titles("TituloInexistente")

        assert resultado == {}
        mock_get.assert_called_once_with(
            "https://imdb-api.com/API/SearchTitle/fake_api_key/TituloInexistente",
            timeout=TIMEOUT,
        )

    @patch("models.imdb.requests.get")
    def test_movie_reviews_success(self, mock_get):
        """Prueba que la obtención de reseñas retorna datos correctamente"""
        # Configurar el mock para devolver una respuesta exitosa
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = self.imdb_data["movie_reviews"]
        mock_get.return_value = mock_response

        imdb = IMDb(apikey="fake_api_key")
        resultado = imdb.movie_reviews("tt1375666")

        assert resultado == self.imdb_data["movie_reviews"]
        mock_get.assert_called_once_with(
            "https://imdb-api.com/API/Reviews/fake_api_key/tt1375666", timeout=TIMEOUT
        )

    @patch("models.imdb.requests.get")
    def test_movie_ratings_success(self, mock_get):
        """Prueba que la obtención de calificaciones retorna datos correctamente"""
        # Configurar el mock para devolver una respuesta exitosa
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = self.imdb_data["movie_ratings"]
        mock_get.return_value = mock_response

        imdb = IMDb(apikey="fake_api_key")
        resultado = imdb.movie_ratings("tt1375666")

        assert resultado == self.imdb_data["movie_ratings"]
        mock_get.assert_called_once_with(
            "https://imdb-api.com/API/Ratings/fake_api_key/tt1375666", timeout=TIMEOUT
        )

    @patch("models.imdb.requests.get")
    def test_search_by_title_failed(self, mock_get):
        """Prueba de búsqueda por título fallida"""
        # Configurar el mock para devolver una respuesta con API Key inválida
        mock_response = Mock(
            spec=Response,
            status_code=200,
            json=Mock(return_value=self.imdb_data["INVALID_API"]),
        )
        mock_get.return_value = mock_response

        imdb = IMDb(apikey="bad-key")
        resultados = imdb.search_titles("Bambi")

        assert resultados is not None
        assert resultados["errorMessage"] == "Invalid API Key"
        mock_get.assert_called_once_with(
            "https://imdb-api.com/API/SearchTitle/bad-key/Bambi", timeout=TIMEOUT
        )

    @patch("models.imdb.requests.get")
    def test_movie_ratings_good(self, mock_get):
        """Prueba de calificaciones de películas con buenas calificaciones"""
        # Configurar el mock para devolver una respuesta exitosa con buenas calificaciones
        mock_response = Mock(
            spec=Response,
            status_code=200,
            json=Mock(return_value=self.imdb_data["movie_ratings"]),
        )
        mock_get.return_value = mock_response

        imdb = IMDb(apikey="fake_api_key")
        resultados = imdb.movie_ratings("tt1375666")

        assert resultados is not None
        assert resultados["title"] == "Bambi"
        assert resultados["filmAffinity"] == 3
        assert resultados["rottenTomatoes"] == 5
        mock_get.assert_called_once_with(
            "https://imdb-api.com/API/Ratings/fake_api_key/tt1375666", timeout=TIMEOUT
        )


class TestSecurityPolicies:
    """Casos de prueba para políticas de seguridad DevSecOps"""

    def test_politica_rechaza_host_no_permitido(self):
        """Verifica que hosts no permitidos sean rechazados"""
        with pytest.raises(ValueError, match="Host no permitido"):
            _enforce_policies("https://malicioso.evil/x")

    def test_politica_rechaza_http(self):
        """Verifica que HTTP (sin TLS) sea rechazado"""
        with pytest.raises(ValueError, match="Se requiere HTTPS"):
            _enforce_policies("http://imdb-api.com/API/SearchTitle/key/title")

    def test_politica_acepta_host_permitido(self):
        """Verifica que hosts permitidos pasen la validación"""
        # No debe lanzar excepción
        _enforce_policies("https://imdb-api.com/API/SearchTitle/key/title")


class TestIMDBconDI:
    """Casos de prueba usando Inyección de Dependencias (sin patches)"""

    @pytest.fixture(autouse=True)
    def setup_class(self, imdb_data):
        """Configuración inicial para cargar los datos de IMDb"""
        self.imdb_data = imdb_data

    def test_search_titles_con_cliente_inyectado(self):
        """Prueba búsqueda de títulos con cliente HTTP inyectado (DI pura)"""
        http = Mock()
        mock_resp = Mock(status_code=200)
        mock_resp.json.return_value = self.imdb_data["search_title"]
        http.get.return_value = mock_resp

        imdb = IMDb(apikey="fake_api_key", http_client=http)
        out = imdb.search_titles("Bambi")

        http.get.assert_called_once_with(
            "https://imdb-api.com/API/SearchTitle/fake_api_key/Bambi",
            timeout=TIMEOUT,
        )
        assert out == self.imdb_data["search_title"]

    def test_movie_reviews_con_cliente_inyectado(self):
        """Prueba obtención de reseñas con cliente HTTP inyectado (DI pura)"""
        http = Mock()
        mock_resp = Mock(status_code=200)
        mock_resp.json.return_value = self.imdb_data["movie_reviews"]
        http.get.return_value = mock_resp

        imdb = IMDb(apikey="fake_api_key", http_client=http)
        out = imdb.movie_reviews("tt1375666")

        http.get.assert_called_once_with(
            "https://imdb-api.com/API/Reviews/fake_api_key/tt1375666",
            timeout=TIMEOUT,
        )
        assert out == self.imdb_data["movie_reviews"]

    def test_movie_ratings_con_cliente_inyectado(self):
        """Prueba obtención de calificaciones con cliente HTTP inyectado (DI pura)"""
        http = Mock()
        mock_resp = Mock(status_code=200)
        mock_resp.json.return_value = self.imdb_data["movie_ratings"]
        http.get.return_value = mock_resp

        imdb = IMDb(apikey="fake_api_key", http_client=http)
        out = imdb.movie_ratings("tt1375666")

        http.get.assert_called_once_with(
            "https://imdb-api.com/API/Ratings/fake_api_key/tt1375666",
            timeout=TIMEOUT,
        )
        assert out == self.imdb_data["movie_ratings"]

    def test_search_titles_failure_con_cliente_inyectado(self):
        """Prueba manejo de errores con cliente HTTP inyectado (status 404)"""
        http = Mock()
        mock_resp = Mock(status_code=404)
        mock_resp.json.return_value = {}
        http.get.return_value = mock_resp

        imdb = IMDb(apikey="fake_api_key", http_client=http)
        out = imdb.search_titles("TituloInexistente")

        http.get.assert_called_once_with(
            "https://imdb-api.com/API/SearchTitle/fake_api_key/TituloInexistente",
            timeout=TIMEOUT,
        )
        assert out == {}

    def test_invalid_api_key_con_cliente_inyectado(self):
        """Prueba respuesta con API Key inválida usando cliente inyectado"""
        http = Mock()
        mock_resp = Mock(status_code=200)
        mock_resp.json.return_value = self.imdb_data["INVALID_API"]
        http.get.return_value = mock_resp

        imdb = IMDb(apikey="bad-key", http_client=http)
        out = imdb.search_titles("Bambi")

        http.get.assert_called_once_with(
            "https://imdb-api.com/API/SearchTitle/bad-key/Bambi",
            timeout=TIMEOUT,
        )
        assert out["errorMessage"] == "Invalid API Key"
