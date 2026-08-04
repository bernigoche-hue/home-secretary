import secrets
import string
from datetime import date

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms import (
    CreateFamilyGroupForm,
    EventForm,
    JoinFamilyGroupForm,
    LoginForm,
    RegistrationForm,
)
from app.models import Event, FamilyGroup, User


main = Blueprint("main", __name__)


def generate_unique_invite_code() -> str:
    """Generate a unique family invitation code."""
    alphabet = string.ascii_uppercase + string.digits

    while True:
        code = "HS-" + "".join(
            secrets.choice(alphabet) for _ in range(5)
        )

        if FamilyGroup.query.filter_by(invite_code=code).first() is None:
            return code


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        if User.query.filter_by(email=email).first() is not None:
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

        flash(f"Welcome back, {user.full_name}.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("login.html", form=form)


@main.route("/dashboard")
@login_required
def dashboard():
    upcoming_events = []

    if current_user.family_group_id is not None:
        upcoming_events = (
            Event.query
            .filter(
                Event.family_group_id == current_user.family_group_id,
                Event.event_date >= date.today(),
                Event.status == "scheduled",
            )
            .order_by(Event.event_date.asc(), Event.start_time.asc())
            .limit(5)
            .all()
        )

    return render_template(
        "dashboard.html",
        upcoming_events=upcoming_events,
    )


@main.route("/family")
@login_required
def family():
    if current_user.family_group is None:
        flash("Create or join a family group first.", "info")
        return redirect(url_for("main.dashboard"))

    return render_template(
        "family.html",
        family_group=current_user.family_group,
    )


@main.route("/family/create", methods=["GET", "POST"])
@login_required
def create_family():
    if current_user.family_group is not None:
        flash("You already belong to a family group.", "warning")
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
    if current_user.family_group is not None:
        flash("You already belong to a family group.", "warning")
        return redirect(url_for("main.family"))

    form = JoinFamilyGroupForm()

    if form.validate_on_submit():
        invite_code = form.invite_code.data.strip().upper()

        family_group = FamilyGroup.query.filter_by(
            invite_code=invite_code
        ).first()

        if family_group is None:
            flash("The invitation code is invalid.", "danger")
            return render_template("join_family.html", form=form)

        current_user.family_group = family_group
        current_user.role = "member"
        db.session.commit()

        flash(f"You have joined {family_group.name}.", "success")
        return redirect(url_for("main.family"))

    return render_template("join_family.html", form=form)


@main.route("/events")
@login_required
def events():
    """Display events belonging to the user's family."""
    if current_user.family_group_id is None:
        flash(
            "Create or join a family group before managing events.",
            "warning",
        )
        return redirect(url_for("main.dashboard"))

    family_events = (
        Event.query
        .filter_by(family_group_id=current_user.family_group_id)
        .order_by(Event.event_date.asc(), Event.start_time.asc())
        .all()
    )

    return render_template(
        "events.html",
        events=family_events,
    )


@main.route("/events/create", methods=["GET", "POST"])
@login_required
def create_event():
    """Create a new event for the user's family group."""
    if current_user.family_group_id is None:
        flash(
            "Create or join a family group before creating events.",
            "warning",
        )
        return redirect(url_for("main.dashboard"))

    form = EventForm()

    if form.validate_on_submit():
        if form.event_date.data < date.today():
            flash(
                "The event date cannot be in the past.",
                "danger",
            )
            return render_template("create_event.html", form=form)

        event = Event(
            title=form.title.data.strip(),
            description=(
                form.description.data.strip()
                if form.description.data
                else None
            ),
            event_date=form.event_date.data,
            start_time=form.start_time.data,
            location=(
                form.location.data.strip()
                if form.location.data
                else None
            ),
            family_group_id=current_user.family_group_id,
            created_by_id=current_user.id,
        )

        db.session.add(event)
        db.session.commit()

        flash(
            f"{event.title} was created successfully.",
            "success",
        )
        return redirect(url_for("main.events"))

    return render_template("create_event.html", form=form)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("main.index"))
