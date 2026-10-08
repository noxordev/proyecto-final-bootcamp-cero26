import os

import httpx
from dotenv import load_dotenv

OMDB_URL = "https://www.omdbapi.com/"
NOT_FOUND_ERROR = "Movie not found!"
# Con estos mensajes OMDb dice que no hay película con ese imdbID: el primero si el id
# tiene buen formato pero no existe, el segundo si el formato es incorrecto.
DETAIL_NOT_FOUND_ERRORS = ["Error getting data.", "Incorrect IMDb ID."]

load_dotenv() # Carga las variables de entorno desde el archivo .env. 
OMDB_API_KEY = os.getenv("OMDB_API_KEY") # Obtiene la API key de OMDb del .env.


if not OMDB_API_KEY: # Mejor que el servidor no arranque a que falle más tarde.
    raise RuntimeError("Falta OMDB_API_KEY en el archivo .env")

class OmdbError(Exception):
    """Error al consultar OMDb: no responde, o responde con un error distinto de "no encontrada"."""


def fetch_omdb(params):
    """Hace una petición a OMDb con la API key y los parámetros recibidos.

    Devuelve la respuesta de OMDb como diccionario, tal cual llega (puede traer "Response": "False").
    Lanza OmdbError si OMDb no responde o no devuelve JSON.
    """
    params_with_key = {"apikey": OMDB_API_KEY, **params}
    try:
        return httpx.get(OMDB_URL, params=params_with_key).json()
    except (httpx.HTTPError, ValueError):
        # ValueError = OMDb respondió algo que no es JSON (por ejemplo, una página de error).
        raise OmdbError("No se pudo conectar con OMDb.")


def get_movie(movie_id):
    """Pide a OMDb el detalle de una película por su imdbID (por ejemplo "tt0133093").

    Devuelve un diccionario con todos sus datos (título, año, director, sinopsis, póster...),
    o None si no existe ninguna película con ese id.
    Lanza OmdbError si OMDb no responde o devuelve otro error.
    """
    # plot=full pide la sinopsis completa en vez de la corta.
    data = fetch_omdb({"i": movie_id, "plot": "full"})
    if data["Response"] == "True": # Igual que en search_movies: "True" llega como texto.
        return data
    if data["Error"] in DETAIL_NOT_FOUND_ERRORS:
        return None
    raise OmdbError(data["Error"])


def search_movies(title, year):
    """Busca películas en OMDb por título y año.

    Recibe el título y el año; si el año es "" o None, OMDb no filtra por año.
    Devuelve la lista de películas encontradas, vacía si no hay ninguna.
    Lanza OmdbError si OMDb no responde o devuelve otro error.
    """
    data = fetch_omdb({"s": title, "y": year, "type": "movie"})
    if data["Response"] == "True": # OMDb envía "True" y "False" como texto, no como booleanos. 
        return data["Search"]
    if data["Error"] == NOT_FOUND_ERROR:
        return []
    raise OmdbError(data["Error"])


