import os
import tempfile
import warnings
import re

# Tests basiques de l'application

def test_01_config_testing(test_app):
    """Vérification de l'utilisation de la base de tests"""
    assert test_app.testing is True


# Test d'utilisation de la base de données
def test_01_consultation(db_objects):
    """Test d'accès à la base de données"""
    db_session, User, Post, Star = db_objects
    from sqlalchemy import select

    ordre = select(User)
    all_users = db_session.execute(ordre).scalars().all()
    assert len(all_users) == 2
    for user in all_users:
        assert isinstance(user, User)
        for post in user.all_posts:
            assert isinstance(post, Post)
        for post in user.all_starred_posts:
            assert isinstance(post, Post)
        for star in user.all_stars:
            assert isinstance(star, Star)

def test_02_create_and_delete_user(db_objects):
    """Création et destruction d'un utilisateur dans la base de données"""
    db_session, User, Post, Star = db_objects
    from sqlalchemy import select

    username = "test user"
    password = "aaa"
    # on vérifie que l'utilisateur n'existe pas
    db_user = db_session.execute(select(User).where(User.username == username)).scalars().first()
    assert db_user is None
    # on le crée en mémoire
    user = User(username=username, password=password)
    assert isinstance(user, User)
    # on le prépare à être créé dans le base
    db_session.add(user)
    assert user.id is None
    # on le crée réellement (on peut récuper son id automatique)
    db_session.flush()
    assert user.id is not None
    # on le cherche dans la base
    db_user = db_session.execute(select(User).where(User.username == username)).scalars().first()
    assert db_user is not None
    assert isinstance(db_user, User)
    # on vérifie que l'ORM a bien fait son boulot (les deux objets sont les mêmes)
    assert user is db_user
    # on efface l'utilisateur
    db_session.delete(user)
    db_session.flush()
    # on vérifie qu'il n'existe plus dans la base
    db_user = db_session.execute(select(User).where(User.username == username)).scalars().first()
    assert db_user is None
    # on annule la transaction
    db_session.rollback()


# Tests d'authentification

def register_new_user(web_client):
    # on crée un nouvel utilisateur
    response = web_client.post('/auth/register', data={
        'username': 'test user',
        'password': 'abcdefgh',
        'avatar': None,
    })
    assert response.status_code == 302

    # on se connecte
    response = web_client.post('/auth/login', data={
        'username': 'test user',
        'password': 'abcdefgh',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert re.search('test user', response.get_data(as_text=True)) is not None

    
def remove_new_user(db_objects):
    """ à exécuter après chaque test"""
    # on supprime le nouvel utilisateur (directement dans la base
    # puisque rien n'est prévu dans l'interface Web pour qu'un
    # utilisateur puisse supprimer son compte) si il a été créé
    db_session, User, Post, Star = db_objects
    from sqlalchemy import select

    db_user = db_session.execute(
        select(User).where(User.username == "test user")
    ).scalars().first()
    if db_user is not None:
        db_session.delete(db_user)
        db_session.commit()

    
def test_01_register_without_data(web_client):
    # on tente de créer un nouvel utilisateur (sans envoyer de données)
    response = web_client.post('/auth/register')
    assert response.status_code == 200
    response_as_text = response.get_data(as_text=True)
    assert re.search('Username is required', response_as_text) is not None

    
def test_02_register_without_password(web_client):
    # on tente de créer un nouvel utilisateur (sans toutes les données)
    response = web_client.post('/auth/register', data={
        'username': 'test user',
    })
    assert response.status_code == 200
    response_as_text = response.get_data(as_text=True)
    assert re.search('Password is required', response_as_text) is not None

    
def test_03_register_with_empty_password(web_client):
    # on tente de créer un nouvel utilisateur (avec mot de passe vide)
    response = web_client.post('/auth/register', data={
        'username': 'test user',
        'password': '',
    })
    assert response.status_code == 200
    response_as_text = response.get_data(as_text=True)
    assert re.search('Password is required', response_as_text) is not None

    
def test_04_register_and_login(web_client):
    register_new_user(web_client)


def test_05_remove_new_user(db_objects):
    remove_new_user(db_objects)
