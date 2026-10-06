import os

from dotenv import load_dotenv

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

# Mejor que el servidor no arranque a que falle más tarde, en cada búsqueda, con un error confuso de OMDb.
if not OMDB_API_KEY:
    raise RuntimeError("Falta OMDB_API_KEY en el archivo .env")
