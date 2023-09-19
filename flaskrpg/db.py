import click
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.automap import name_for_collection_relationship
from sqlalchemy.ext.automap import name_for_scalar_relationship
from flask.cli import with_appcontext
from flask_sqlalchemy_session import flask_scoped_session
# from sqlalchemy.orm import scoped_session

# Les éléments suivants seront définis lorsque l'automap aura fait son
# travail...
db_session = None
User = None
Post = None
Star = None


def connect_db(app):
    '''Connextion à la base de données via l'automap'''
    # click.echo("db.connect_db")
    if app.config['TRACE_MAPPING']:
        click.echo("DB mapping...")

    # ORM: correpondances nom de table => nom de classe
    model_map = {
        'user': 'User',
        'post': 'Post',
        'star': 'Star',
    }

    # ORM: correpondances association => attribut
    relation_map = {
        # l'association 1:N entre User et Post
        'User=>Post(post_author_id_fkey)': 'all_posts',
        'Post=>User(post_author_id_fkey)': 'author',
        # l'association N:M entre Post et User (via Star)
        'Post=>Star(star_post_id_fkey)': 'all_stars',
        'User=>Star(star_user_id_fkey)': 'all_stars',
        'Post=>User(star_post_id_fkey)': 'all_starring_users',
        'User=>Post(star_user_id_fkey)': 'all_starred_posts',
    }

    url_de_connexion = app.config['SQLALCHEMY_DATABASE_URI']
    sqlalchemy_engine_echo = app.config['SQLALCHEMY_ENGINE_ECHO']

    if app.config['TRACE_MAPPING']:
        click.echo("URL de connexion:" + url_de_connexion)

    engine = create_engine(
        url_de_connexion,
        # si True, pratique pour déboguer (mais très verbeux)
        echo=sqlalchemy_engine_echo,
        # pour disposer des fonctionnalités de la version 2.0
        future=True,
    )
    our_metadata = MetaData()
    our_metadata.reflect(engine, only=model_map.keys())
    # print("our_metadata: ok")
    Base = automap_base(metadata=our_metadata)

    class User(Base):
        __tablename__ = 'user'

        # la déclaration suivante est indispensable (pour le viewonly)
        all_starred_posts = relationship(
            "Post", collection_class=set, secondary="star", viewonly=True
        )

        def __str__(self):
            return f"User({self.id},{self.username})"

    class Post(Base):
        __tablename__ = 'post'

        # la déclaration suivante est indispensable (pour le viewonly)
        all_starring_users = relationship(
            "User", collection_class=set, secondary="star", viewonly=True
        )

        def __str__(self):
            return f"Post({self.id},{self.author_id},{self.created})"

    class Star(Base):
        __tablename__ = 'star'

        def __str__(self):
            return f"Star({self.user_id},{self.post_id})"

    def map_names(type, orig_func):
        """fonction d'aide à la mise en correspondance"""
        def _map_names(base, local_cls, referred_cls, constraint):
            auto_name = orig_func(base, local_cls, referred_cls, constraint)
            # la clé de l'association
            key = f"{local_cls.__name__}=>{referred_cls.__name__}({constraint.name})"
            # quelle correpondance ?
            if key in relation_map:
                # Yes, return it
                name = relation_map[key]
            else:
                name = auto_name
            if app.config['TRACE_MAPPING']:
                # affiche la relation créée (pour comprendre ce qui se passe)
                click.echo(f" {type:>10s}: {key} {auto_name} => {name}")
            return name

        return _map_names

    Base.prepare(
        name_for_scalar_relationship=map_names('scalar',
                                               name_for_scalar_relationship),
        name_for_collection_relationship=map_names('collection',
                                                   name_for_collection_relationship),
    )

    # On rend les tables du modèle globales à ce module
    for cls in [User, Post, Star]:
        cls.__table__.info = dict(bind_key='main')
        globals()[cls.__name__] = cls

    Session = sessionmaker(
        bind=engine,
        future=True,
        class_=sqlalchemy.orm.Session
    )
    globals()['db_session'] = flask_scoped_session(Session, app)

    if app.config['TRACE_MAPPING']:
        click.echo("DB mapping done.")


@click.command("check-db")
@with_appcontext
def check_db_command():
    """Vérifie que le mapping vers la base de données fonctionne bien."""
    assert db_session is not None

    # on fait quelques requêtes SQL
    ordre = select(User)
    all_users = db_session.execute(ordre).scalars().all()
    for user in all_users:
        assert isinstance(user, User)


def init_app(app):
    """Initialisation du lien avec la base de données"""

    if app.config['TRACE']:
        click.echo(
            f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}"
        )

    connect_db(app)

    app.cli.add_command(check_db_command)
