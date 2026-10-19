"""Tests de queries_db.py (comentarios y calificaciones). Usan una base de datos temporal, nunca movies.db."""

import os
import sqlite3
from datetime import date

import pytest

import connection
from queries_db import get_comments, get_rating_summary, save_comment, save_rating


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
    text = "¡'Recomendada' por el profe Ricardo!; DROP TABLE Comment"
    save_comment("tt0133093", "Ana", text)
    assert get_comments("tt0133093")[0]["comment"] == text


def test_save_rating(tmp_path, monkeypatch):
    """Una calificación guardada cuenta en el resumen de su película."""
    use_empty_database(tmp_path, monkeypatch)
    save_rating("tt0133093", "Ricardo", 5)
    assert get_rating_summary("tt0133093") == {"average": 5.0, "count": 1}


def test_rating_summary_without_ratings(tmp_path, monkeypatch):
    """Una película sin calificaciones no tiene promedio y tiene 0 votos."""
    use_empty_database(tmp_path, monkeypatch)
    assert get_rating_summary("tt0133093") == {"average": None, "count": 0}


def test_rating_summary_average(tmp_path, monkeypatch):
    """El promedio es la media de todas las calificaciones de la película."""
    use_empty_database(tmp_path, monkeypatch)
    save_rating("tt0133093", "Ricardo", 5)
    save_rating("tt0133093", "Ana", 4)
    assert get_rating_summary("tt0133093") == {"average": 4.5, "count": 2}


def test_rating_summary_other_movie(tmp_path, monkeypatch):
    """Las calificaciones de una película no cuentan en otra."""
    use_empty_database(tmp_path, monkeypatch)
    save_rating("tt0133093", "Ricardo", 5)
    assert get_rating_summary("tt0234215") == {"average": None, "count": 0}


def test_rating_out_of_range(tmp_path, monkeypatch):
    """Una nota fuera del 1 al 5 la rechaza la propia base de datos, por el CHECK de create_db.sql."""
    use_empty_database(tmp_path, monkeypatch)
    with pytest.raises(sqlite3.IntegrityError):
        save_rating("tt0133093", "Ricardo", 6)
