from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms import LoginForm, RegistrationForm
from app.models import User


main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Display the public landing page."""
    return render_template("index.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user account."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        existing_user = User.query.filter_by(email=email).first()

        if existing_user is not None:
            flash(
                "An account already exists for that email address.",
                "warning",
            )
            return render_template("register.html", form=form)

        user = User(
            full_name=form.full_name.data.strip(),
            email=email,
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash(
            "Your account has been created. You can now log in.",
            "success",
        )
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)


@main.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate an existing user."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(form.password.data):
            flash(
                "The email address or password is incorrect.",
                "danger",
            )
            return render_template("login.html", form=form)

        login_user(user, remember=form.remember_me.data)

        flash(
            f"Welcome back, {user.full_name}.",
            "success",
        )
        return redirect(url_for("main.dashboard"))

    return render_template("login.html", form=form)


@main.route("/dashboard")
@login_required
def dashboard():
    """Display the authenticated user dashboard."""
    return render_template("dashboard.html")


@main.route("/logout")
@login_required
def logout():
    """Log out the current user."""
    logout_user()

    flash(
        "You have been logged out successfully.",
        "info",
    )
    return redirect(url_for("main.index"))