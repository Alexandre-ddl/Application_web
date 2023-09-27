import functools
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import make_response
from flask import abort
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from flaskrpg.db import db_session, User
from sqlalchemy import select

from PIL import Image
import io

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = db_session.execute(
            select(User)
            .where(User.id == user_id)
        ).scalars().first()


def login_required(route):
    """Route decorator that checks if user is logged and, if not,
    redirects anonymous users to the login page."""

    @functools.wraps(route)
    def wrapped_route(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return route(**kwargs)

    return wrapped_route


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == "POST":
        username = request.form.get("username", '').strip()
        password = request.form.get("password", '').strip()
        fullname = request.form.get("fullname", None)
        profile_desc = request.form.get("profile_desc", None)
        avatar = request.files.get("avatar", None)
        # l'objet 'avatar' est de type 'werkzeug.datastructures.FileStorage' (ou None)

        error = ""

        if username == '':
            error += "Username is required. "

        if password == '':
            error += "Password is required. "

        preexistant_user = db_session.execute(
            select(User).
            where(User.username == username)
        ).scalars().first()
        if preexistant_user is not None:
            error += f"User {username} is already registered. "

        if avatar is not None:
            if avatar.filename != "":
                if avatar.mimetype != 'image/png' and avatar.mimetype != 'image/jpeg':
                    error += f"Avatar should be a PNG or JPEG image file (instead of {avatar.mimetype}). "
                else:
                    # création en mémoire de l'avatar
                    image = Image.open(io.BytesIO(avatar.read()), mode='r')
                    # réduction de la taille de l'image
                    image.thumbnail((20, 20))
                    # conversion en PNG de l'image réduite dans la la variable png_content
                    png_content = io.BytesIO()
                    image.save(png_content, "PNG")
            else:
                avatar = None

        if error == '':
            # the name is available, store it in the database and go to
            # the login page
            if (avatar is None):
                new_user = User(
                    username=username,
                    password=generate_password_hash(password),
                    fullname=fullname,
                    profile_desc=profile_desc,
                )
            else:
                new_user = User(
                    username=username,
                    password=generate_password_hash(password),
                    fullname=fullname,
                    profile_desc=profile_desc,
                    avatar_mimetype = 'image/png',  # imposé puisque conversion en Png
                    avatar_content=png_content.getvalue()
                )

            db_session.add(new_user)
            db_session.commit()
            flash("Registration ok")
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        error = None

        user = db_session.execute(
            select(User)
            .where(User.username == username)
        ).scalars().first()

        if user is None:
            error = "Incorrect username or password."
        elif not check_password_hash(user.password, password):
            error = "Incorrect username or password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("root"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/avatar/<int:user_id>")
def avatar(user_id):
    user = db_session.execute(
        select(User)
        .where(User.id == user_id)
    ).scalars().first()
    if (user is not None and user.avatar_content):
        response = make_response(user.avatar_content)
        response.headers.set('Content-Type', user.avatar_mimetype)
        return response
    else:
        abort(404)

@login_required
@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("root"))


