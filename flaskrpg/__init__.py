import click
from flask import Flask, redirect, url_for


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # lecture du fichier de configuration (par défaut dans 'instance/configurations.py')
    app.config.from_envvar('FLASKRPG_SETTINGS')
    # for key, value in app.config.items():
    #     click.echo(f"{key}: {value}")

    if app.config['TRACE']:
        click.echo("create_app:" + __name__)
        click.echo("SQLALCHEMY_DATABASE_URI is: " + app.config["SQLALCHEMY_DATABASE_URI"])

    # register the database commands
    from flaskrpg import db

    db.init_app(app)

    # apply the blueprints to the app
    from flaskrpg import auth, blog

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    @app.route("/")
    def root():
        return redirect(url_for("blog.index"))

    return app
