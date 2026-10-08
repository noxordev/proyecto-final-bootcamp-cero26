"""Tests de get_connection."""

import os

import pytest

import connection
from connection import get_connection


def test_missing_database(tmp_path, monkeypatch):
    """Si el archivo de la base de datos no existe, lanza un error claro y no crea un archivo vacío."""
    missing_path = os.path.join(tmp_path, "missing.db")
    monkeypatch.setattr(connection, "DB_PATH", missing_path)
    with pytest.raises(RuntimeError, match="create_db.sql"):
        get_connection()
    assert not os.path.exists(missing_path)
