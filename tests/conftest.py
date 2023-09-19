# initialisation des tests effectués par 'pytest' dans ce répertoire (et
# ses sous-répertoires)

import os
import pytest
import warnings
import subprocess

SQLALCHEMY_DATABASE_URI_TEST = "postgresql+psycopg2://flaskrpgadmin:flaskrpgadminpass@localhost:5432/flaskrpgtest"

def execute_sql_file_with_psql(url, filename):
    """Exécute un script SQL via psql en utilisant l'URL fourni pour se connecter"""
    psql_url = url.replace("+psycopg2","")
    #warnings.warn(psql_url)
    #warnings.warn(filename)
    res = subprocess.run(
        ['/usr/bin/psql', '-f', filename, psql_url],
        capture_output=True,
        encoding="utf-8",
        timeout=3,
    )
    if res.stdout != '' :
        warnings.warn(f"\nSTDOUT: {res.stdout}")
    if res.stderr != '' :
        warnings.warn(f"\nSTDERR: {res.stderr}")
    assert res.returncode == 0


@pytest.fixture(autouse=True, scope="session")
def init_test_db():
    """(ré)Initialisation de la structure et des données de la base de test"""
    execute_sql_file_with_psql(SQLALCHEMY_DATABASE_URI_TEST, "sql/schema-postgresql.sql")
    execute_sql_file_with_psql(SQLALCHEMY_DATABASE_URI_TEST, "sql/populate.sql")
    return True
    

@pytest.fixture
def test_app():
    """L'application Flask de test de flaskrpg"""
    os.environ["FLASKRPG_CONFIG"] = "testing"
    from flaskrpg import create_app
    test_app = create_app({
        'TESTING': True,
        #"SQLALCHEMY_DATABASE_URI": SQLALCHEMY_DATABASE_URI_TEST,
        #"TRACE": True,
        #"TRACE_MAPPING": True,
    })
    yield test_app


@pytest.fixture
def web_client(test_app):
    """Un client Web pour simuler des requêtes provenant d'un navigateur"""
    with test_app.test_client() as web_client:
        yield web_client

@pytest.fixture
def db_objects(test_app):
    """Tous les objets pour l'accès à la base de données"""
    from sqlalchemy import text
    from flaskrpg.db import db_session, User, Post, Star
    return (db_session, User, Post, Star)
    
