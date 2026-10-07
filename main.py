from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from controller import router

app = FastAPI()

# Conecta a la app todas las rutas definidas en controller.py.
app.include_router(router)

# Sirve los archivos de views/ tal cual; html=True hace que "/" muestre index.html.
# Va después del router: si fuera antes, "/" también capturaría las rutas /api.
app.mount("/", StaticFiles(directory="views", html=True), name="views")
