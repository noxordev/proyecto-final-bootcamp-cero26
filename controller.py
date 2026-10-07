from fastapi import APIRouter, HTTPException

from queries_omdb import OmdbError, search_movies

# Todas las rutas de este archivo empiezan por /api, sin tener que repetirlo en cada una.
router = APIRouter(prefix="/api")


@router.get("/search")
def search(title: str, year: str = ""):
    """Busca películas por título y, si se indica, por año: /api/search?title=matrix&year=1999

    Recibe el título (obligatorio) y el año (puede faltar) desde la dirección.
    Devuelve la lista de películas de OMDb, que FastAPI envía como JSON.
    Responde con error 400 si los datos no son válidos y 502 si falla OMDb.
    """
    if not title.strip(): #strip() elimina los espacios en blanco al principio y al final de la cadena.
        raise HTTPException(status_code=400, detail="Escribe un título para buscar.")
    # El año llega como texto desde la dirección; vacío significa "sin filtrar por año".
    if year and not year.isdigit():
        raise HTTPException(status_code=400, detail="El año tiene que ser un número.")
    try:
        return search_movies(title, year)
    except OmdbError as error:
        # 502: el fallo no es del usuario ni nuestro, sino del servicio externo (OMDb).
        raise HTTPException(status_code=502, detail=str(error))
