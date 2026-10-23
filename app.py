import os
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "local-development-only-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cybernews.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")


def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))

        user = db.session.get(User, session["user_id"])

        if not user or user.role != "admin":
            abort(403)

        return function(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template("index.html", articles=articles)


@app.route("/article/<int:article_id>")
def article(article_id):
    news = db.get_or_404(Article, article_id)
    return render_template("article.html", article=news)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("admin" if user.role == "admin" else "home"))

        error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            error = "Username and password are required."

        elif len(password) < 8:
            error = "Password must be at least 8 characters."

        elif User.query.filter_by(username=username).first():
            error = "Username already exists."

        else:
            new_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                role="user"
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))

    return render_template("register.html", error=error)
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/admin")
@admin_required
def admin():
    articles = Article.query.order_by(Article.id.desc()).all()
    return render_template("admin.html", articles=articles)


@app.route("/admin/add", methods=["POST"])
@admin_required
def add_article():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip()
    content = request.form.get("content", "").strip()

    if not title or not category or not content:
        abort(400)

    db.session.add(Article(
        title=title,
        category=category,
        content=content
    ))
    db.session.commit()

    return redirect(url_for("admin"))


@app.route("/admin/delete/<int:article_id>", methods=["POST"])
@admin_required
def delete_article(article_id):
    news = db.get_or_404(Article, article_id)
    db.session.delete(news)
    db.session.commit()
    return redirect(url_for("admin"))


with app.app_context():
    db.create_all()

    if Article.query.count() == 0:
        db.session.add_all([
            Article(
                title="Ransomware Attack",
                category="Ransomware",
                content="Hospital networks affected by a ransomware attack."
            ),
            Article(
                title="Data Breach",
                category="Data Breaches",
                content="Customer information exposed in a security incident."
            ),
            Article(
                title="Security Vulnerability",
                category="Vulnerabilities",
                content="Researchers discover a critical software vulnerability."
            )
        ])
        db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)