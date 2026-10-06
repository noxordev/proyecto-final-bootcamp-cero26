import os

import httpx
from dotenv import load_dotenv

OMDB_URL = "https://www.omdbapi.com/"
NOT_FOUND_ERROR = "Movie not found!"

load_dotenv() # Carga las variables de entorno desde el archivo .env. 
OMDB_API_KEY = os.getenv("OMDB_API_KEY") # Obtiene la API key de OMDb.


if not OMDB_API_KEY: # Mejor que el servidor no arranque a que falle más tarde.
    raise RuntimeError("Falta OMDB_API_KEY en el archivo .env")


class OmdbError(Exception):
    """Error al consultar OMDb: no responde, o responde con un error distinto de "no encontrada"."""


def search_movies(title, year):
    """Busca películas en OMDb por título y año.

    Recibe el título y el año; si el año es "" o None, OMDb no filtra por año.
    Devuelve la lista de películas encontradas, vacía si no hay ninguna.
    Lanza OmdbError si OMDb no responde o devuelve otro error.
    """
    params = {"apikey": OMDB_API_KEY, "s": title, "y": year, "type": "movie"}
    try:
        data = httpx.get(OMDB_URL, params=params).json()
    except (httpx.HTTPError, ValueError):
        # ValueError = OMDb respondió algo que no es JSON (por ejemplo, una página de error).
        raise OmdbError("No se pudo conectar con OMDb.")

    if data["Response"] == "True": # OMDb envía "True" y "False" como texto, no como booleanos. 
        return data["Search"]
    if data["Error"] == NOT_FOUND_ERROR:
        return []
    raise OmdbError(data["Error"])


