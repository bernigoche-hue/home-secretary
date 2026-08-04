import secrets
import string

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms import (
    CreateFamilyGroupForm,
    JoinFamilyGroupForm,
    LoginForm,
    RegistrationForm,
)
from app.models import FamilyGroup, User


main = Blueprint("main", __name__)


def generate_unique_invite_code() -> str:
    """Generate a unique eight-character family invitation code."""
    alphabet = string.ascii_uppercase + string.digits

    while True:
        code = "HS-" + "".join(
            secrets.choice(alphabet) for _ in range(5)
        )

        existing_group = FamilyGroup.query.filter_by(
            invite_code=code
        ).first()

        if existing_group is None:
            return code


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


@main.route("/family")
@login_required
def family():
    """Display the current user's family group."""
    if current_user.family_group is None:
        flash(
            "Create or join a family group first.",
            "info",
        )
        return redirect(url_for("main.dashboard"))

    return render_template(
        "family.html",
        family_group=current_user.family_group,
    )


@main.route("/family/create", methods=["GET", "POST"])
@login_required
def create_family():
    """Create a family group for the authenticated user."""
    if current_user.family_group is not None:
        flash(
            "You already belong to a family group.",
            "warning",
        )
        return redirect(url_for("main.family"))

    form = CreateFamilyGroupForm()

    if form.validate_on_submit():
        family_group = FamilyGroup(
            name=form.name.data.strip(),
            invite_code=generate_unique_invite_code(),
        )

        db.session.add(family_group)
        db.session.flush()

        current_user.family_group = family_group
        current_user.role = "admin"

        db.session.commit()

        flash(
            f"{family_group.name} was created successfully.",
            "success",
        )
        return redirect(url_for("main.family"))

    return render_template("create_family.html", form=form)


@main.route("/family/join", methods=["GET", "POST"])
@login_required
def join_family():
    """Join an existing family group using its invitation code."""
    if current_user.family_group is not None:
        flash(
            "You already belong to a family group.",
            "warning",
        )
        return redirect(url_for("main.family"))

    form = JoinFamilyGroupForm()

    if form.validate_on_submit():
        invite_code = form.invite_code.data.strip().upper()

        family_group = FamilyGroup.query.filter_by(
            invite_code=invite_code
        ).first()

        if family_group is None:
            flash(
                "The invitation code is invalid.",
                "danger",
            )
            return render_template("join_family.html", form=form)

        current_user.family_group = family_group
        current_user.role = "member"
        db.session.commit()

        flash(
            f"You have joined {family_group.name}.",
            "success",
        )
        return redirect(url_for("main.family"))

    return render_template("join_family.html", form=form)


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
