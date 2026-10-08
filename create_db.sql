-- Crea las tablas de movies.db.
-- Uso: en DB Browser, crea una base de datos nueva llamada movies.db y ejecuta este archivo
-- en la pestaña "Ejecutar SQL".

CREATE TABLE "Comment" (
	"id"	INTEGER,
	"movie_id"	TEXT NOT NULL,
	"person"	TEXT NOT NULL,
	"comment"	TEXT NOT NULL,
	"date"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
