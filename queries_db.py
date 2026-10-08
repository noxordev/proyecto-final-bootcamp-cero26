from datetime import date # Importa el módulo date para obtener la fecha actual.

from connection import get_connection # Importa la función get_connection para obtener la conexión a la base de datos.


def save_comment(movie_id, person, comment):
    """Guarda en la tabla Comment un comentario nuevo de una película, con la fecha de hoy.

    Recibe el imdbID de la película, el nombre de quien comenta y el texto del comentario.
    No devuelve nada.
    """
    connection = get_connection()
    try:
        # Los ? se rellenan con la lista, en orden. sqlite3 trata esos valores siempre como
        # datos, nunca como SQL, así que un comentario con comillas no puede romper la consulta.
        connection.execute(
            "INSERT INTO Comment (movie_id, person, comment, date) VALUES (?, ?, ?, ?)",
            [movie_id, person, comment, date.today().isoformat()],
        )
        connection.commit()
    finally:
        connection.close()
    return None


def get_comments(movie_id):
    """Busca los comentarios de una película, del más reciente al más antiguo.

    Recibe el imdbID de la película.
    Devuelve una lista de diccionarios con id, person, comment y date; vacía si no hay ninguno.
    """
    connection = get_connection()
    try:
        # Se ordena por id y no por fecha: la fecha no tiene hora, y el id crece con cada comentario nuevo.
        rows = connection.execute(
            "SELECT id, person, comment, date FROM Comment WHERE movie_id = ? ORDER BY id DESC",
            [movie_id],
        ).fetchall()
    finally:
        connection.close()

    comments = []
    for row in rows:
        comments.append(dict(row))
    return comments
