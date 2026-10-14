import sqlite3

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from queries_db import get_comments, save_comment
from queries_omdb import OmdbError, TooManyResultsError, get_movie, search_movies

# Todas las rutas de este archivo empiezan por /api, sin tener que repetirlo en cada una.
router = APIRouter(prefix="/api")


@router.get("/search")
def search(title: str, year: str = ""):
    """Busca películas por título y, si se indica, por año: /api/search?title=matrix&year=1999

    Recibe el título (obligatorio) y el año (puede faltar) desde la dirección.
    Devuelve la lista de películas de OMDb, que FastAPI envía como JSON.
    Responde con error 400 si los datos no son válidos o el título da demasiados resultados,
    y 502 si falla OMDb.
    """
    if not title.strip(): #strip() elimina los espacios en blanco al principio y al final de la cadena.
        raise HTTPException(status_code=400, detail="Escribe un título para buscar.")
    # El año llega como texto desde la dirección; vacío significa "sin filtrar por año".
    if year and not year.isdigit():
        raise HTTPException(status_code=400, detail="El año tiene que ser un número.")
    try:
        return search_movies(title, year)
    except TooManyResultsError:
        # 400: no falla OMDb, es que el título es demasiado corto; lo puede arreglar el usuario.
        raise HTTPException(status_code=400, detail="Hay demasiados resultados: escribe un título más largo.")
    except OmdbError as error:
        # 502: el fallo no es del usuario ni nuestro, sino del servicio externo (OMDb).
        raise HTTPException(status_code=502, detail=str(error))


@router.get("/movies/{movie_id}")
def movie_detail(movie_id: str):
    """Devuelve el detalle de una película por su imdbID: /api/movies/tt0133093

    Recibe el imdbID desde la propia dirección.
    Devuelve todos los datos de la película que da OMDb, que FastAPI envía como JSON.
    Responde con error 404 si no existe y 502 si falla OMDb.
    """
    try:
        movie = get_movie(movie_id)
    except OmdbError as error:
        raise HTTPException(status_code=502, detail=str(error))
    if movie is None:
        raise HTTPException(status_code=404, detail="No existe ninguna película con ese id.")
    return movie


class NewComment(BaseModel):
    """Datos que envía el formulario de comentarios, en JSON: {"person": "...", "comment": "..."}."""

    person: str
    comment: str


@router.get("/movies/{movie_id}/comments")
def list_comments(movie_id: str):
    """Devuelve los comentarios de una película: /api/movies/tt0133093/comments

    Recibe el imdbID desde la dirección.
    Devuelve la lista de comentarios, del más reciente al más antiguo (vacía si no hay ninguno).
    Responde con error 500 si falla la base de datos.
    """
    try:
        return get_comments(movie_id)
    except sqlite3.Error:
        # 500: el fallo es nuestro (la base de datos), no del usuario ni de OMDb.
        raise HTTPException(status_code=500, detail="No se pudieron cargar los comentarios.")


@router.post("/movies/{movie_id}/comments", status_code=201)
def add_comment(movie_id: str, new_comment: NewComment):
    """Guarda un comentario nuevo de una película.

    Recibe el imdbID desde la dirección y, en el cuerpo de la petición, el nombre y el comentario.
    Devuelve un mensaje de confirmación, con el código 201 ("creado").
    Responde con error 400 si falta el nombre o el comentario y 500 si falla la base de datos.
    """
    person = new_comment.person.strip()
    comment = new_comment.comment.strip()
    if not person:
        raise HTTPException(status_code=400, detail="Escribe tu nombre.")
    if not comment:
        raise HTTPException(status_code=400, detail="Escribe un comentario.")
    try:
        save_comment(movie_id, person, comment)
    except sqlite3.Error:
        raise HTTPException(status_code=500, detail="No se pudo guardar el comentario.")
    return {"message": "Comentario guardado."}
