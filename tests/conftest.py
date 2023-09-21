# initialisation des tests effectués par 'pytest' dans ce répertoire (et
# ses sous-répertoires)

import os
import pytest
import warnings

from sqlalchemy import create_engine
from sqlalchemy import text


SQLALCHEMY_DATABASE_URI_TEST = "postgresql+psycopg2://flaskrpgadmin:flaskrpgadminpass@localhost:5432/flaskrpgtest"

def execute_sql_file(url, filename):
    """Exécute un script SQL en utilisant l'URL fourni pour se connecter"""
    engine = create_engine(SQLALCHEMY_DATABASE_URI_TEST, echo=True)

    with engine.begin() as con:
        with open(filename) as file:
            query = text(file.read())
            con.execute(query)

@pytest.fixture(scope="session")
def create_test_tables():
    """(ré)Initialisation de la structure de la base de test"""
    execute_sql_file(SQLALCHEMY_DATABASE_URI_TEST, "sql/schema-postgresql.sql")
    return True
    
@pytest.fixture(autouse=True, scope="session")
def populate_test_tables(create_test_tables):
    """(ré)Initialisation des données de la base de test"""
    execute_sql_file(SQLALCHEMY_DATABASE_URI_TEST, "sql/populate.sql")
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
    
