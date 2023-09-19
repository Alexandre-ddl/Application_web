import os

TESTING=True
TRACE = False
TRACE_MAPPING = False
SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
SQLALCHEMY_ENGINE_ECHO = False
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://flaskrpgadmin:flaskrpgadminpass@localhost:5432/flaskrpgtest"
