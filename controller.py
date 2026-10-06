from fastapi import FastAPI

app = FastAPI()


@app.get("/api/hello")
def say_hello():
    """Ruta de prueba: confirma que el servidor responde. No recibe nada y devuelve un saludo."""
    return {"message": "hola"}
