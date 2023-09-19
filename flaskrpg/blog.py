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


bp = Blueprint("blog", __name__, url_prefix='/blog')


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    if g.user:
        user_id = g.user.id
    else:
        user_id = -1

    sort_order = request.args.get('sort', 'by_date')

    # noms des types de tris autorisés
    order_by_choices = dict(
        by_date=Post.created.desc(),
        by_star=func.count(Star.user_id).desc(),
    )
    # choix de l'ordre de tri
    if sort_order not in order_by_choices.keys():
        sort_order = 'by_date'

    # alias pour effectuer deux jointures avec la table Star
    Star2 = aliased(Star)
    # request for all data
    posts = db_session.execute(
        select(
            Post.id, Post.title, Post.body, Post.created, Post.author_id,
            User.username,
            User.avatar_mimetype,
            func.count(Star.user_id).label('nb_stars'),
            func.count(Star2.user_id).label('stared_by_user'),
        )
        .select_from(Post)
        .join(User, User.id == Post.author_id)
        .join(Star, Star.post_id == Post.id, isouter=True)
        .join(Star2, and_(Star2.post_id == Post.id, Star2.user_id == user_id), isouter=True)
        .group_by(Post.id, User.id, Star2.user_id)
        .order_by(order_by_choices[sort_order])
    ).all()
    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    ordre = (
        select(Post)
        .where(Post.id == bindparam('id'))
    )
    post = db_session.execute(ordre, {'id': id}).scalars().first()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post.author_id != g.user.id:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form.get("title", None)
        body = request.form.get("body", None)

        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            new_post = Post(
                title=title,
                body=body,
                author_id=g.user.id
            )
            db_session.add(new_post)
            db_session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form.get("title", None)
        body = request.form.get("body", None)

        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            post.title = title
            post.body = body
            db_session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)

@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    post = get_post(id)
    db_session.delete(post)
    db_session.commit()
    return redirect(url_for("blog.index"))


@bp.route("/<int:id>/voteup", methods=("POST",))
@login_required
def vote(id):
    """Vote/Unvote for a post."""
    post = get_post(id, check_author=False)
    if post.author_id == g.user.id:
        error = "Can't vote for your own post"
        flash(error)
    else:
        ordre = (
            select(Star)
            .where(Star.user_id == g.user.id, Star.post_id == post.id)
        )
        star = db_session.execute(ordre).scalars().first()
        if star:
            # Unvote
            db_session.delete(star)
        else:
            # Vote
            new_star = Star(user_id=g.user.id, post_id=post.id)
            db_session.add(new_star)
        db_session.commit()
    return redirect(url_for("blog.index"))
