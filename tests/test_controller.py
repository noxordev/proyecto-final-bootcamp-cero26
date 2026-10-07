"""Tests de las rutas de controller.py. Las búsquedas válidas llaman de verdad a OMDb."""

from fastapi.testclient import TestClient # TestClient es una clase que permite hacer pruebas a la API.

import queries_omdb
from main import app

client = TestClient(app)


def test_search():
    """Una búsqueda válida responde 200 con la lista de películas."""
    response = client.get("/api/search", params={"title": "matrix", "year": "1999"})
    assert response.status_code == 200
    titles = []
    for movie in response.json():
        titles.append(movie["Title"])
    assert "The Matrix" in titles


def test_search_without_results():
    """Si OMDb no encuentra nada, la respuesta es 200 con una lista vacía, no un error."""
    response = client.get("/api/search", params={"title": "zzzxqwq"})
    assert response.status_code == 200
    assert response.json() == []


def test_missing_title():
    """Sin el parámetro title, FastAPI responde 422 por sí solo, porque es obligatorio."""
    response = client.get("/api/search")
    assert response.status_code == 422


def test_blank_title():
    """Un título hecho solo de espacios responde 400 con nuestro mensaje."""
    response = client.get("/api/search", params={"title": "   "})
    assert response.status_code == 400
    assert response.json()["detail"] == "Escribe un título para buscar."


def test_year_that_is_not_a_number():
    """Un año con letras responde 400 con nuestro mensaje."""
    response = client.get("/api/search", params={"title": "matrix", "year": "abc"})
    assert response.status_code == 400
    assert response.json()["detail"] == "El año tiene que ser un número."


def test_omdb_failure(monkeypatch): # monkeypatch es una herramienta que permite modificar el 
    # comportamiento de una función o clase para realizar pruebas.
    """Si OMDb no responde, la ruta responde 502 con el mensaje de OmdbError."""
    # El dominio .invalid está reservado: nunca existe, así que la conexión siempre falla.
    monkeypatch.setattr(queries_omdb, "OMDB_URL", "https://omdb.invalid/") #Pruebo a conectar con un dominio que no existe.
    response = client.get("/api/search", params={"title": "matrix"})
    assert response.status_code == 502
    assert response.json()["detail"] == "No se pudo conectar con OMDb."
