# Buscador de películas con comentarios

Proyecto final del bootcamp *Aprender a programar desde cero XXVI* (KeepCoding).

Aplicación web para buscar películas con la API de [OMDb](https://www.omdbapi.com/), ver su detalle, dejar comentarios y calificarlas de 1 a 5 estrellas. Comentarios y calificaciones se guardan en una base de datos SQLite.

## Funcionalidades

- Buscar películas por título, o por título y año.
- Ver el detalle de una película: póster, sinopsis, director, reparto, género y duración.
- Escribir comentarios en el detalle de cada película y ver todos los que tiene, del más reciente al más antiguo. Cada comentario guarda la fecha del día en que se escribió.
- Calificar cada película de 1 a 5 (parte opcional del enunciado) y ver el promedio de todas sus calificaciones en estrellas, con el número exacto y la cantidad de votos.
- Control de errores: datos del formulario no válidos, película inexistente, OMDb sin respuesta y fallos de la base de datos. Todos se muestran en la página con un mensaje en español.

## Tecnologías

Python, FastAPI, SQLite, HTML, CSS, Bootstrap 5 y JavaScript. Tests con pytest.

## Instalación

Hace falta **Python 3.14** y una API key gratuita de OMDb, que se pide en [omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx).

> **Ojo con Python 3.15:** con 3.15 la instalación falla, porque algunas librerías (`pydantic-core`, `httptools`, `PyYAML`) todavía no publican versiones para él. Si tienes varias versiones de Python, crea el entorno virtual con 3.14 como se indica abajo.

Todos los comandos se ejecutan desde la carpeta raíz del proyecto.

### 1. Crear y activar el entorno virtual

En Windows, eligiendo Python 3.14:

```powershell
py -3.14 -m venv venv
```

En macOS o Linux:

```bash
python3.14 -m venv venv
```

Activarlo en Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

Activarlo en macOS o Linux:

```bash
source venv/bin/activate
```

### 2. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 3. Guardar la API key de OMDb

Crear en la raíz del proyecto un archivo llamado `.env` con esta línea (sin comillas ni espacios):

```text
OMDB_API_KEY=tu_api_key
```

El archivo `.env` no se sube al repositorio: cada persona usa su propia key.

### 4. Crear la base de datos

La base de datos se llama `movies.db` y se crea a partir de `create_db.sql`. Hay dos formas:

**Con DB Browser for SQLite:**

1. *Nueva base de datos* → guardarla en la raíz del proyecto como `movies.db`.
2. Cerrar la ventana de crear tabla que se abre sola.
3. Pestaña *Ejecutar SQL* → pegar el contenido de `create_db.sql` → ejecutar.
4. *Escribir cambios* (`Ctrl+S`).

**O con un solo comando de Python:**

```bash
python -c "import sqlite3; sqlite3.connect('movies.db').executescript(open('create_db.sql', encoding='utf-8').read())"
```

## Uso

```bash
fastapi dev main.py
```

Después, abrir [http://127.0.0.1:8000](http://127.0.0.1:8000) en el navegador. La documentación automática de la API está en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Tests

```bash
python -m pytest -v
```

Los tests de OMDb hacen peticiones reales, así que necesitan internet y la API key del `.env`. Los de la base de datos crean una base temporal con `create_db.sql`, nunca tocan `movies.db`.

## Estructura (MVC)

| Capa | Archivo | Qué hace |
|---|---|---|
| Arranque | `main.py` | Crea la app de FastAPI, le añade las rutas y sirve la carpeta `views/` |
| Controlador | `controller.py` | Rutas `/api/...`: valida lo que llega y traduce los errores a respuestas HTTP |
| Modelo | `queries_omdb.py` | Consultas a la API de OMDb |
| Modelo | `queries_db.py` | Consultas SQL de los comentarios y las calificaciones |
| Modelo | `connection.py` | Conexión con `movies.db` |
| Vista | `views/` | `index.html` + `search.js` (buscador) y `detail.html` + `detail.js` (detalle, calificación y comentarios) |
| Base de datos | `create_db.sql` | Crea las tablas `Comment` y `Rating` (se puede volver a ejecutar: solo crea las que falten) |
| Tests | `tests/` | Un archivo de tests por cada archivo de Python, y `test_omdb_api.py`, que documenta cómo responde OMDb |

### Rutas de la API

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/api/search?title=...&year=...` | Busca películas (el año es opcional) |
| GET | `/api/movies/{movie_id}` | Detalle de una película por su imdbID |
| GET | `/api/movies/{movie_id}/comments` | Comentarios de una película |
| POST | `/api/movies/{movie_id}/comments` | Guarda un comentario: `{"person": "...", "comment": "..."}` |
| GET | `/api/movies/{movie_id}/rating` | Promedio y número de calificaciones: `{"average": 4.5, "count": 2}` (`average` es `null` sin votos) |
| POST | `/api/movies/{movie_id}/rating` | Guarda una calificación: `{"person": "...", "rating": 4}` |

## Proceso de desarrollo

En [`BACKLOG.md`](BACKLOG.md) están la arquitectura con el recorrido de una petición, las historias de usuario divididas en tareas por capa y el registro de todas las decisiones tomadas, con su porqué.

## Decisiones respecto al enunciado

- **Búsqueda solo por año:** OMDb no la permite, porque siempre exige un título (lo comprueba el test `test_search_by_year_alone`). Por eso el año es un filtro opcional de la búsqueda por título.
- **`movie_id` es texto, no un entero:** guarda el imdbID que da OMDb (por ejemplo `tt0133093`), que es lo que relaciona los comentarios con cada película.
- **Nombres en inglés:** las tablas son `Comment (id, movie_id, person, comment, date)` y `Rating (id, movie_id, person, rating, date)`, con el visto bueno del profesor.
- **Las estrellas del promedio son enteras** (el promedio se redondea), y debajo se muestra el número exacto con un decimal.
