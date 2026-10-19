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


def save_rating(movie_id, person, rating):
    """Guarda en la tabla Rating una calificación nueva de una película, con la fecha de hoy.

    Recibe el imdbID de la película, el nombre de quien califica y la nota (un entero del 1 al 5).
    No devuelve nada.
    """
    connection = get_connection()
    try:
        connection.execute(
            "INSERT INTO Rating (movie_id, person, rating, date) VALUES (?, ?, ?, ?)",
            [movie_id, person, rating, date.today().isoformat()],
        )
        connection.commit()
    finally:
        connection.close()
    return None


def get_rating_summary(movie_id):
    """Calcula el promedio y el número de calificaciones de una película.

    Recibe el imdbID de la película.
    Devuelve un diccionario {"average": promedio, "count": número de votos}.
    Si no tiene ninguna calificación, devuelve {"average": None, "count": 0}.
    """
    connection = get_connection()
    try:
        # AVG y COUNT resumen todas las filas en una sola, por eso basta con fetchone().
        # Sin filas, AVG da NULL (None en Python) y COUNT da 0: el caso "sin votos" sale solo.
        row = connection.execute(
            "SELECT AVG(rating) AS average, COUNT(*) AS count FROM Rating WHERE movie_id = ?",
            [movie_id],
        ).fetchone()
    finally:
        connection.close()
    return {"average": row["average"], "count": row["count"]}
