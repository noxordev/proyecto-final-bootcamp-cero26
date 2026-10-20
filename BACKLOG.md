# Backlog del proyecto final

Plan y seguimiento del desarrollo: arquitectura, historias de usuario, calidad y registro de decisiones.
Se fue actualizando al terminar cada paso. En GitHub las casillas se ven directamente; en el editor,
con la vista previa (`Ctrl+Shift+V`).

---

## 1. Arquitectura (MVC)

```text
NAVEGADOR (Vista)            SERVIDOR: FastAPI (Controlador)          DATOS (Modelo)
views/                       controller.py                            queries_omdb.py ──httpx────▶ OMDb (internet)
  index.html + search.js       rutas /api/...                         queries_db.py
  detail.html + detail.js      - valida lo que llega                    └─ connection.py ─sqlite3─▶ movies.db
                               - llama al modelo
        ── fetch ──────────▶   - traduce errores a 400/404/502
        ◀─────────── JSON ──

main.py: crea la app, le conecta las rutas de controller.py y sirve los archivos de views/
```

Regla de oro: cada capa solo habla con la de al lado. La vista nunca toca la base de datos,
y el modelo no sabe nada de HTML ni de rutas.

### Recorrido de una petición (ejemplo: buscar "matrix" de 1999)

1. `search.js`: al enviar el formulario, hace `fetch("/api/search?title=matrix&year=1999")`.
2. `main.py`: la app recibe la petición y la pasa al router de `controller.py`.
3. `controller.py` → `search()`: comprueba que el título no esté vacío y que el año sea un número.
4. `queries_omdb.py` → `search_movies()` → `fetch_omdb()`: pide los datos a OMDb con la API key.
5. OMDb responde; `search_movies()` devuelve la lista de películas (o `[]`, o lanza `OmdbError`).
6. `controller.py` devuelve la lista; FastAPI la convierte en JSON (o responde 400/502 con `detail`).
7. `search.js` → `showMovies()`: pinta cada película como un enlace a `detail.html?id=...`.

---

## 2. Historias de usuario

Cada historia atraviesa todas las capas: modelo → controlador → vista → tests.

### HU1. Buscar películas por título ✅
- [x] Modelo: `fetch_omdb()` y `search_movies()` en `queries_omdb.py`
- [x] Controlador: `GET /api/search` (valida título y año; errores 400 y 502)
- [x] Vista: formulario en `index.html` y `search.js` (`async` / `await`)
- [x] Tests: `test_queries_omdb.py`, `test_controller.py`, `test_omdb_api.py`

### HU2. Buscar películas por año ✅
- [x] Título + año (el año es opcional en la misma búsqueda)
- [x] Solo por año: OMDb no lo permite (documentado en `test_search_by_year_alone`)

### HU3. Ver el detalle de una película ✅
- [x] Modelo: `get_movie()` (devuelve `None` si no existe)
- [x] Controlador: `GET /api/movies/{movie_id}` (errores 404 y 502)
- [x] Vista: `detail.html` y `detail.js`
- [x] Tests

### HU4. Registrar comentarios desde el detalle ✅
- [x] Base de datos: tabla `Comment` creada en DB Browser; receta en `create_db.sql`
- [x] Modelo: `get_connection()` en `connection.py`
- [x] Modelo: `save_comment()` en `queries_db.py` (+ tests con base de datos temporal)
- [x] Controlador: `POST /api/movies/{movie_id}/comments` (valida nombre y comentario no vacíos; error de base de datos → 500)
- [x] Vista: formulario de comentario en `detail.html` + `sendComment()` en `detail.js` (al guardar, vacía el formulario y recarga la lista)
- [x] Tests de la ruta

### HU5. Ver todos los comentarios en el detalle ✅
- [x] Modelo: `get_comments()` en `queries_db.py` (+ tests)
- [x] Controlador: `GET /api/movies/{movie_id}/comments`
- [x] Vista: lista de comentarios en `detail.html`: `loadComments()` y `showComments()` en `detail.js` (con `textContent`, nunca `innerHTML`)
- [x] Tests de la ruta

### HU6. Calificar de 1 a 5 y ver el promedio en estrellas (opcional)
- [x] Base de datos: tabla `Rating` en `create_db.sql`, con `CHECK` del 1 al 5 (creada en `movies.db` con DB Browser)
- [x] Modelo: `save_rating()` y `get_rating_summary()` en `queries_db.py` (+ tests)
- [x] Controlador: `GET` y `POST` en `/api/movies/{movie_id}/rating` (nota del 1 al 5 → si no, 400; si no es entero, 422; nombre con `validate_person()`)
- [x] Vista: promedio en estrellas en `detail.html` (`loadRating()` y `showRating()` en `detail.js`)
- [ ] Vista: formulario con estrellas para votar
- [ ] Tests

---

## 3. Calidad y entrega

### Repaso de errores
- [x] OMDb no responde → 502 con mensaje en español
- [x] "Too many results." → `TooManyResultsError` en el modelo → 400 con mensaje en español
- [x] Errores de base de datos → respuesta 500 con mensaje claro
- [x] `detail.html` abierto sin `?id=` (o vacío): muestra un mensaje y no hace peticiones
- [x] Límite de longitud en los comentarios: nombre de 50 caracteres y comentario de 500 → 400 (y `maxlength` en el HTML)

### Entrega
- [x] `requirements.txt` al día
- [x] `README.md`: entorno virtual, `pip install -r requirements.txt`, `.env` con la API key, crear `movies.db` con `create_db.sql`, arrancar con `fastapi dev main.py`, tests con `python -m pytest -v`
- [x] Prueba final completa desde cero (clonar, instalar y usar): con Python 3.14 todo funciona; con 3.15 falla la instalación
- [ ] Subir al repositorio remoto y entregar el enlace

---

## 4. Definición de "hecho"

Un paso está terminado cuando:
1. Funciona en el navegador o en `/docs`.
2. Tiene tests, si es código del trabajo final, y pasan todos (`python -m pytest -v`).
3. Cada función tiene su comentario o docstring en español.
4. Está en un commit.

---

## 5. Registro de decisiones

| Decisión | Por qué |
|---|---|
| MVC en archivos planos, al estilo del profesor | Más simple para este tamaño y sigue la estructura vista en clase |
| `APIRouter` en `controller.py`, app en `main.py` (aprobado por el profesor) | `/api` se escribe una sola vez; cada archivo, una responsabilidad |
| FastAPI devuelve JSON y el JavaScript pinta con `fetch` | Es como en clase |
| FastAPI sirve también `views/` | Un solo servidor; `fetch` con rutas cortas (`/api/...`) |
| `httpx` para OMDb, `python-dotenv` para la key | Ya venían con `fastapi[standard]`: nada nuevo que instalar |
| No hay búsqueda solo por año | OMDb exige título (test `test_search_by_year_alone`) |
| Detalle en una página aparte, `detail.html` | El botón "atrás" y recargar funcionan sin código extra |
| Tablas y columnas en inglés (aprobado por el profesor) | Coherencia con el resto del código |
| `movie_id` es TEXT | El imdbID es texto: `tt0133093` |
| `create_db.sql` se sube, `movies.db` no | Lo prefiere el enunciado y los tests crean su base con la misma receta |
| Errores: 400 datos inválidos, 404 no existe, 500 falla la base de datos, 502 falla OMDb | El frontend muestra el `detail` de cada error |
| "Demasiados resultados" tiene su propio error (`TooManyResultsError`) y responde 400 | No es un fallo de OMDb sino del título escrito: el usuario lo puede arreglar. Los demás errores de OMDb (key inválida, límite diario) siguen como 502 con su texto original, porque los resuelve quien instala la app |
| Límites de 50 (nombre) y 500 (comentario) caracteres, comprobados en el controlador con un 400 | Coherente con el resto de validaciones (pydantic podría hacerlo con `Field(max_length=...)`, pero respondería un 422 en inglés). El `maxlength` del HTML es solo una comodidad que copia esos números |
| El `POST` no comprueba que la película exista en OMDb | Costaría una llamada extra por comentario, y desde la página solo se comenta una película que ya cargó bien |
| `Rating` es una tabla aparte de `Comment`, con `CHECK` del 1 al 5 | Lo pide el enunciado; se puede votar sin comentar, y la base rechaza notas fuera de rango aunque alguien se salte la app |
| `create_db.sql` usa `CREATE TABLE IF NOT EXISTS` | Se puede ejecutar entero sobre una base existente: crea solo las tablas que faltan |
| `validate_person()` en el controlador comprueba el nombre (vacío, longitud) | Es la misma regla para comentarios y calificaciones: vive en un solo sitio |
| Las estrellas del promedio se redondean a estrellas enteras, y debajo se muestra el número con un decimal | Sin iconos ni CSS extra (caracteres ★ y ☆); el decimal da la precisión que las estrellas pierden |
| `get_rating_summary` devuelve el promedio sin redondear (o `None` sin votos) | El modelo da el dato; cómo mostrarlo (redondeo, estrellas) lo decide la vista |
| El controlador captura `sqlite3.Error`; `queries_db.py` no captura nada | El modelo solo cierra la conexión; quien decide la respuesta HTTP es el controlador |
| `POST` de comentarios responde 201 con un mensaje; la vista vuelve a pedir la lista | Más simple que devolver el comentario creado |
| `movieId` se lee una sola vez, arriba de `detail.js` | Lo usan la película, sus comentarios y el formulario |
| La sección de comentarios va dentro de `#movie` | Si la película no existe, tampoco se ven sus comentarios |
| Los tests de rutas reutilizan `use_empty_database` de `test_queries_db.py` | No repetir cómo se crea la base de pruebas (en equipos se suele usar un *fixture* en `conftest.py`) |
| `textContent` en vez de `innerHTML` | Un comentario con HTML no se puede ejecutar en el navegador |
| El README pide Python 3.14 (`py -3.14 -m venv venv`) | Con Python 3.15, recién salido, `pydantic-core`, `httptools` y `PyYAML` aún no tienen versión compilada y `pip install` falla |
| El README da dos formas de crear `movies.db`: DB Browser o un comando de Python | El enunciado prefiere instrucciones; el comando sirve a quien no tenga DB Browser |
| Tests con pytest; OMDb real y base de datos temporal | Prueban el comportamiento de verdad sin tocar `movies.db` |
