"""Tests de save_comment y get_comments. Usan una base de datos temporal, nunca movies.db."""

import os
import sqlite3
from datetime import date

import connection
from queries_db import get_comments, save_comment


def use_empty_database(tmp_path, monkeypatch):
    """Crea una base de datos vacía con create_db.sql y hace que connection.py la use en vez de movies.db.

    Recibe la carpeta temporal y el monkeypatch del test. No devuelve nada.
    """
    db_path = os.path.join(tmp_path, "test.db")
    with open("create_db.sql", encoding="utf-8") as file:
        script = file.read()
    database = sqlite3.connect(db_path)
    database.executescript(script)
    database.close()
    monkeypatch.setattr(connection, "DB_PATH", db_path)
    return None


def test_save_comment(tmp_path, monkeypatch):
    """Un comentario guardado aparece en los comentarios de su película, con la fecha de hoy."""
    use_empty_database(tmp_path, monkeypatch)
    save_comment("tt0133093", "Ana", "Ricardo es un profe genial")
    comments = get_comments("tt0133093")
    assert len(comments) == 1
    assert comments[0]["person"] == "Ana"
    assert comments[0]["comment"] == "Ricardo es un profe genial"
    assert comments[0]["date"] == date.today().isoformat()


def test_get_comments_without_comments(tmp_path, monkeypatch):
    """Una película sin comentarios devuelve una lista vacía."""
    use_empty_database(tmp_path, monkeypatch)
    assert get_comments("tt0133093") == []


def test_get_comments_other_movie(tmp_path, monkeypatch):
    """Los comentarios de una película no aparecen en otra."""
    use_empty_database(tmp_path, monkeypatch)
    save_comment("tt0133093", "Ana", "Ricardo es un profe genial")
    assert get_comments("tt0234215") == []


def test_get_comments_order(tmp_path, monkeypatch):
    """El comentario más reciente sale el primero."""
    use_empty_database(tmp_path, monkeypatch)
    save_comment("tt0133093", "Ana", "Primero")
    save_comment("tt0133093", "Luis", "Segundo")
    comments = get_comments("tt0133093")
    assert comments[0]["comment"] == "Segundo"
    assert comments[1]["comment"] == "Primero"


def test_comment_with_quotes(tmp_path, monkeypatch):
    """Un comentario con comillas se guarda tal cual, sin romper la consulta."""
    use_empty_database(tmp_path, monkeypatch)
    save_comment("tt0133093", "Ana", "It's 'genial'; DROP TABLE Comment")
    assert get_comments("tt0133093")[0]["comment"] == "¡Recomendada por el profe Ricardo!; DROP TABLE Comment"
