from fastapi import FastAPI

from controller import router

app = FastAPI()

# Conecta a la app todas las rutas definidas en controller.py.
app.include_router(router)
