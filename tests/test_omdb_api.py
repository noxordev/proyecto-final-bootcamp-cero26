"""Tests que muestran cómo se comporta OMDb.

Explica por qué queries_omdb.py está escrito como está. Si alguno falla, es que OMDb ha
cambiado y hay que revisar queries_omdb.py.
"""

import httpx

from queries_omdb import DETAIL_NOT_FOUND_ERRORS, NOT_FOUND_ERROR, OMDB_API_KEY, OMDB_URL


def ask_omdb(params):
    """Pregunta a OMDb directamente, sin pasar por search_movies.

    Recibe los parámetros de búsqueda (sin la key) y devuelve la respuesta entera como diccionario.
    """
    # ** copia dentro del nuevo diccionario todos los pares de params.
    params_with_key = {"apikey": OMDB_API_KEY, **params}
    return httpx.get(OMDB_URL, params=params_with_key).json()


def test_response():
    """OMDb envía "True" como texto, no como booleano. Por eso search_movies compara con == "True"."""
    data = ask_omdb({"s": "matrix"})
    assert isinstance(data["Response"], str)
    assert data["Response"] == "True"


def test_not_found():
    """Sin resultados, OMDb no envía una lista vacía sino un error con este texto exacto."""
    data = ask_omdb({"s": "zzzxqwq"})
    assert data == {"Response": "False", "Error": NOT_FOUND_ERROR}


def test_empty_year():
    """Con el año vacío, OMDb responde igual que sin año: por eso search_movies pasa siempre el año."""
    assert ask_omdb({"s": "matrix", "y": ""}) == ask_omdb({"s": "matrix"})


def test_search_by_year_alone():
    """Sin título, OMDb no busca por año: por eso no hay búsqueda "solo por año"."""
    data = ask_omdb({"y": "1999"})
    assert data["Response"] == "False"
    assert data["Error"] == "Incorrect IMDb ID."


def test_detail_not_found():
    """Por id, OMDb dice "no existe" con dos mensajes distintos: por eso DETAIL_NOT_FOUND_ERRORS tiene dos."""
    well_formed = ask_omdb({"i": "tt9999999"})
    malformed = ask_omdb({"i": "abc"})
    assert well_formed["Error"] == DETAIL_NOT_FOUND_ERRORS[0]
    assert malformed["Error"] == DETAIL_NOT_FOUND_ERRORS[1]
