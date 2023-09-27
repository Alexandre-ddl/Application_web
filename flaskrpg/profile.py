from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskrpg.auth import login_required

from sqlalchemy import select, bindparam, func, and_
from sqlalchemy.orm import aliased
from flaskrpg.db import User, Post, Star, db_session

bp = Blueprint("profile", __name__, url_prefix='/profile')

@bp.route("/<int:user_id>", methods=("GET",))
def view(user_id):
    user = db_session.get(User, user_id)
    if user is None:
        flash("Utilisateur introuvable")
        redirect(url_for("root"))
    return render_template("profile/view.html", user=user)
