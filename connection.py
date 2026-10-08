import os
import sqlite3

DB_PATH = "movies.db" # Ruta de la base de datos. Por si se quiere cambiar, se puede hacer aquí. 


def get_connection():
    """Abre una conexión nueva con la base de datos movies.db.

    No recibe nada. Devuelve la conexión, preparada para leer cada fila por el nombre
    de su columna (fila["person"]) en vez de por su posición (fila[2]).
    Lanza RuntimeError si movies.db no existe.
    """
    # Sin esta comprobación, sqlite3 crearía un movies.db vacío sin avisar, y el error
    # saldría después.  
    if not os.path.exists(DB_PATH):
        raise RuntimeError(f"Falta {DB_PATH}: créala con create_db.sql (ver README).") 
        # Si el archivo no existe, lanza un error.
    connection = sqlite3.connect(DB_PATH) # Conecta a la base de datos.
    connection.row_factory = sqlite3.Row 
    # Configura la conexión para que cada fila se pueda leer por el nombre de su columna 
    # (fila["person"]) en vez de por su posición (fila[2]).
    return connection # Devuelve la conexión.
