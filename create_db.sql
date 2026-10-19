-- Crea las tablas de movies.db.
-- Uso: en DB Browser, crea una base de datos nueva llamada movies.db y ejecuta este archivo
-- en la pestaña "Ejecutar SQL".
-- IF NOT EXISTS permite volver a ejecutarlo sobre una base que ya tiene alguna de las tablas:
-- crea solo las que faltan y no toca las que ya existen ni sus datos.

CREATE TABLE IF NOT EXISTS "Comment" (
	"id"	INTEGER,
	"movie_id"	TEXT NOT NULL,
	"person"	TEXT NOT NULL,
	"comment"	TEXT NOT NULL,
	"date"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

-- Calificaciones de 1 a 5 (parte opcional). El CHECK hace que la propia base de datos
-- rechace cualquier otro valor, aunque alguien se salte las validaciones de la app.
CREATE TABLE IF NOT EXISTS "Rating" (
	"id"	INTEGER,
	"movie_id"	TEXT NOT NULL,
	"person"	TEXT NOT NULL,
	"rating"	INTEGER NOT NULL CHECK("rating" BETWEEN 1 AND 5),
	"date"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
