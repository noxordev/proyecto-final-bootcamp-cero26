"""Tests de search_movies y get_movie. Llaman de verdad a OMDb: necesitan internet y la API key del .env."""

import pytest

import queries_omdb
from queries_omdb import OmdbError, get_movie, search_movies

THE_MATRIX_ID = "tt0133093"


def test_search_by_title():
    """Buscar solo por título devuelve una lista con películas."""
    movies = search_movies("matrix", "")
    assert len(movies) > 0


def test_search_by_title_and_year():
    """Con año, todas las películas son de ese año, y The Matrix está entre ellas."""
    movies = search_movies("matrix", "1999")
    ids = []
    for movie in movies:
        assert movie["Year"] == "1999"
        ids.append(movie["imdbID"])
    assert THE_MATRIX_ID in ids


def test_unknown_title():
    """Si no hay resultados, se devuelve una lista vacía, no un error."""
    assert search_movies("zzzxqwq", "") == []


def test_too_short_title():
    """Un título demasiado corto hace que OMDb devuelva un error, que llega como OmdbError."""
    with pytest.raises(OmdbError, match="Too many results"):
        search_movies("a", "")


def test_invalid_api_key(monkeypatch):
    """Con una key falsa, OMDb sí responde, con un error que llega como OmdbError."""
    monkeypatch.setattr(queries_omdb, "OMDB_API_KEY", "fake-key")
    with pytest.raises(OmdbError, match="Invalid API key"):
        search_movies("matrix", "")


def test_unreachable_omdb(monkeypatch):
    """Si OMDb no responde (sin internet, servidor caído), llega OmdbError con nuestro mensaje."""
    # El dominio .invalid está reservado: nunca existe, así que la conexión siempre falla.
    monkeypatch.setattr(queries_omdb, "OMDB_URL", "https://omdb.invalid/")
    with pytest.raises(OmdbError, match="No se pudo conectar"):
        search_movies("matrix", "")


def test_get_movie():
    """Con un imdbID que existe, devuelve un diccionario con los datos de esa película."""
    movie = get_movie(THE_MATRIX_ID)
    assert movie["Title"] == "The Matrix"
    assert movie["Year"] == "1999"


def test_get_movie_unknown_id():
    """Con un imdbID que tiene buen formato pero no existe, devuelve None."""
    assert get_movie("tt9999999") is None


def test_get_movie_malformed_id():
    """Con un id mal formado, también devuelve None: para el usuario es lo mismo, no existe."""
    assert get_movie("abc") is None
