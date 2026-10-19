"""Tests de las rutas de controller.py. Las búsquedas válidas llaman de verdad a OMDb.

Los de comentarios usan una base de datos temporal, nunca movies.db.
"""

import os

from fastapi.testclient import TestClient # TestClient es una clase que permite hacer pruebas a la API.

import connection
import queries_omdb
from controller import MAX_COMMENT_LENGTH, MAX_PERSON_LENGTH
from main import app
from queries_db import save_comment
from test_queries_db import use_empty_database

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


def test_search_too_short_title():
    """Un título que da demasiados resultados responde 400 con nuestro mensaje en español."""
    response = client.get("/api/search", params={"title": "a"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Hay demasiados resultados: escribe un título más largo."


def test_omdb_failure(monkeypatch): # monkeypatch es una herramienta que permite modificar el 
    # comportamiento de una función o clase para realizar pruebas.
    """Si OMDb no responde, la ruta responde 502 con el mensaje de OmdbError."""
    # El dominio .invalid está reservado: nunca existe, así que la conexión siempre falla.
    monkeypatch.setattr(queries_omdb, "OMDB_URL", "https://omdb.invalid/") #Pruebo a conectar con un dominio que no existe.
    response = client.get("/api/search", params={"title": "matrix"})
    assert response.status_code == 502
    assert response.json()["detail"] == "No se pudo conectar con OMDb."


def test_movie_detail():
    """Un imdbID que existe responde 200 con los datos de la película."""
    response = client.get("/api/movies/tt0133093")
    assert response.status_code == 200
    assert response.json()["Title"] == "The Matrix"


def test_movie_detail_unknown_id():
    """Un imdbID que no existe responde 404 con nuestro mensaje."""
    response = client.get("/api/movies/tt9999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "No existe ninguna película con ese id."


def test_movie_detail_omdb_failure(monkeypatch):
    """Si OMDb no responde, el detalle también responde 502 con el mensaje de OmdbError."""
    monkeypatch.setattr(queries_omdb, "OMDB_URL", "https://omdb.invalid/")
    response = client.get("/api/movies/tt0133093")
    assert response.status_code == 502
    assert response.json()["detail"] == "No se pudo conectar con OMDb."


def test_list_comments(tmp_path, monkeypatch):
    """Los comentarios guardados de una película se devuelven con 200."""
    use_empty_database(tmp_path, monkeypatch)
    save_comment("tt0133093", "Ricardo", "Ricardo aprueba esta película")
    response = client.get("/api/movies/tt0133093/comments")
    assert response.status_code == 200
    assert response.json()[0]["person"] == "Ricardo"


def test_add_comment(tmp_path, monkeypatch):
    """Un comentario válido responde 201 y después aparece en la lista, sin espacios sobrantes."""
    use_empty_database(tmp_path, monkeypatch)
    new_comment = {"person": "  Ana  ", "comment": "  Ricardo, esta ruta también tiene tests  "}
    response = client.post("/api/movies/tt0133093/comments", json=new_comment)
    assert response.status_code == 201
    comments = client.get("/api/movies/tt0133093/comments").json()
    assert comments[0]["person"] == "Ana"
    assert comments[0]["comment"] == "Ricardo, esta ruta también tiene tests"


def test_add_comment_blank_person(tmp_path, monkeypatch):
    """Un nombre hecho solo de espacios responde 400 y no se guarda nada."""
    use_empty_database(tmp_path, monkeypatch)
    new_comment = {"person": "   ", "comment": "Sin nombre"}
    response = client.post("/api/movies/tt0133093/comments", json=new_comment)
    assert response.status_code == 400
    assert response.json()["detail"] == "Escribe tu nombre."
    assert client.get("/api/movies/tt0133093/comments").json() == []


def test_add_comment_blank_comment(tmp_path, monkeypatch):
    """Un comentario hecho solo de espacios responde 400 con nuestro mensaje."""
    use_empty_database(tmp_path, monkeypatch)
    new_comment = {"person": "Ana", "comment": "   "}
    response = client.post("/api/movies/tt0133093/comments", json=new_comment)
    assert response.status_code == 400
    assert response.json()["detail"] == "Escribe un comentario."


def test_add_comment_missing_field():
    """Sin el campo comment, FastAPI responde 422 por sí solo, porque NewComment lo exige."""
    response = client.post("/api/movies/tt0133093/comments", json={"person": "Ana"})
    assert response.status_code == 422


def test_add_comment_long_person(tmp_path, monkeypatch):
    """Un nombre más largo que el límite responde 400 y no se guarda nada."""
    use_empty_database(tmp_path, monkeypatch)
    new_comment = {"person": "R" * (MAX_PERSON_LENGTH + 1), "comment": "Ricardo, este nombre no cabe"}
    response = client.post("/api/movies/tt0133093/comments", json=new_comment)
    assert response.status_code == 400
    assert response.json()["detail"] == "El nombre no puede tener más de 50 caracteres."
    assert client.get("/api/movies/tt0133093/comments").json() == []


def test_add_comment_long_comment(tmp_path, monkeypatch):
    """Un comentario más largo que el límite responde 400 con nuestro mensaje."""
    use_empty_database(tmp_path, monkeypatch)
    new_comment = {"person": "Ana", "comment": "a" * (MAX_COMMENT_LENGTH + 1)}
    response = client.post("/api/movies/tt0133093/comments", json=new_comment)
    assert response.status_code == 400
    assert response.json()["detail"] == "El comentario no puede tener más de 500 caracteres."


def test_add_comment_max_length(tmp_path, monkeypatch):
    """Un nombre y un comentario de justo la longitud máxima sí se guardan."""
    use_empty_database(tmp_path, monkeypatch)
    new_comment = {"person": "R" * MAX_PERSON_LENGTH, "comment": "a" * MAX_COMMENT_LENGTH}
    response = client.post("/api/movies/tt0133093/comments", json=new_comment)
    assert response.status_code == 201


def test_comments_database_error(tmp_path, monkeypatch):
    """Si la base de datos falla, las dos rutas responden 500 con su mensaje."""
    # Un archivo que existe pero no es una base de datos: sqlite3 lanza un error al usarlo.
    broken_path = os.path.join(tmp_path, "broken.db")
    with open(broken_path, "w", encoding="utf-8") as file:
        file.write("Esto no es una base de datos, Ricardo")
    monkeypatch.setattr(connection, "DB_PATH", broken_path)

    response = client.get("/api/movies/tt0133093/comments")
    assert response.status_code == 500
    assert response.json()["detail"] == "No se pudieron cargar los comentarios."

    new_comment = {"person": "Ana", "comment": "Hola"}
    response = client.post("/api/movies/tt0133093/comments", json=new_comment)
    assert response.status_code == 500
    assert response.json()["detail"] == "No se pudo guardar el comentario."
