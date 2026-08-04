import secrets
import string
from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms import (
    CreateFamilyGroupForm,
    EventForm,
    JoinFamilyGroupForm,
    LoginForm,
    RegistrationForm,
    TaskForm,
)
from app.models import Event, FamilyGroup, Task, User


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
    outstanding_tasks = []

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

        outstanding_tasks = (
            Task.query
            .filter(
                Task.family_group_id == current_user.family_group_id,
                Task.status != "completed",
            )
            .order_by(Task.due_date.asc())
            .limit(5)
            .all()
        )

    return render_template(
        "dashboard.html",
        upcoming_events=upcoming_events,
        outstanding_tasks=outstanding_tasks,
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
@main.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_event(event_id: int):
    """Edit an existing family event."""
    event = db.session.get(Event, event_id)

    if (
        event is None
        or event.family_group_id != current_user.family_group_id
    ):
        flash("The requested event could not be found.", "danger")
        return redirect(url_for("main.events"))

    if event.created_by_id != current_user.id and current_user.role != "admin":
        flash(
            "Only the event creator or family administrator can edit it.",
            "danger",
        )
        return redirect(url_for("main.events"))

    form = EventForm(obj=event)

    if form.validate_on_submit():
        if form.event_date.data < date.today():
            flash("The event date cannot be in the past.", "danger")
            return render_template(
                "edit_event.html",
                form=form,
                event=event,
            )

        event.title = form.title.data.strip()
        event.event_date = form.event_date.data
        event.start_time = form.start_time.data
        event.location = (
            form.location.data.strip()
            if form.location.data
            else None
        )
        event.description = (
            form.description.data.strip()
            if form.description.data
            else None
        )

        db.session.commit()

        flash(
            f"{event.title} was updated successfully.",
            "success",
        )
        return redirect(url_for("main.events"))

    if not form.is_submitted():
        form.submit.label.text = "Save changes"

    return render_template(
        "edit_event.html",
        form=form,
        event=event,
    )


@main.route("/events/<int:event_id>/delete", methods=["POST"])
@login_required
def delete_event(event_id: int):
    """Delete an event after validating access rights."""
    event = db.session.get(Event, event_id)

    if (
        event is None
        or event.family_group_id != current_user.family_group_id
    ):
        flash("The requested event could not be found.", "danger")
        return redirect(url_for("main.events"))

    if event.created_by_id != current_user.id and current_user.role != "admin":
        flash(
            "Only the event creator or family administrator can delete it.",
            "danger",
        )
        return redirect(url_for("main.events"))

    event_title = event.title

    db.session.delete(event)
    db.session.commit()

    flash(
        f"{event_title} was deleted successfully.",
        "success",
    )
    return redirect(url_for("main.events"))
@main.route("/tasks")
@login_required
def tasks():
    """Display household tasks for the user's family group."""
    if current_user.family_group_id is None:
        flash(
            "Create or join a family group before managing tasks.",
            "warning",
        )
        return redirect(url_for("main.dashboard"))

    family_tasks = (
        Task.query
        .filter_by(family_group_id=current_user.family_group_id)
        .order_by(Task.status.asc(), Task.due_date.asc())
        .all()
    )

    return render_template(
        "tasks.html",
        tasks=family_tasks,
    )


@main.route("/tasks/create", methods=["GET", "POST"])
@login_required
def create_task():
    """Create and assign a household task."""
    if current_user.family_group_id is None:
        flash(
            "Create or join a family group before creating tasks.",
            "warning",
        )
        return redirect(url_for("main.dashboard"))

    form = TaskForm()

    family_members = (
        User.query
        .filter_by(family_group_id=current_user.family_group_id)
        .order_by(User.full_name.asc())
        .all()
    )

    form.assigned_to.choices = [
        (member.id, member.full_name)
        for member in family_members
    ]

    if form.validate_on_submit():
        assignee = db.session.get(User, form.assigned_to.data)

        if (
            assignee is None
            or assignee.family_group_id != current_user.family_group_id
        ):
            flash(
                "The selected assignee is not a member of your family group.",
                "danger",
            )
            return render_template("create_task.html", form=form)

        task = Task(
            title=form.title.data.strip(),
            description=(
                form.description.data.strip()
                if form.description.data
                else None
            ),
            due_date=form.due_date.data,
            priority=form.priority.data,
            status="pending",
            family_group_id=current_user.family_group_id,
            created_by_id=current_user.id,
            assigned_to_id=assignee.id,
        )

        db.session.add(task)
        db.session.commit()

        flash(
            f"{task.title} was created and assigned to "
            f"{assignee.full_name}.",
            "success",
        )
        return redirect(url_for("main.tasks"))

    return render_template("create_task.html", form=form)


@main.route("/tasks/<int:task_id>/status/<string:new_status>", methods=["POST"])
@login_required
def update_task_status(task_id: int, new_status: str):
    """Update a task through its controlled status lifecycle."""
    allowed_statuses = {"pending", "in_progress", "completed"}

    if new_status not in allowed_statuses:
        flash("The requested task status is invalid.", "danger")
        return redirect(url_for("main.tasks"))

    task = db.session.get(Task, task_id)

    if (
        task is None
        or task.family_group_id != current_user.family_group_id
    ):
        flash("The task could not be found.", "danger")
        return redirect(url_for("main.tasks"))

    task.status = new_status

    if new_status == "completed":
        task.completed_at = datetime.utcnow()
    else:
        task.completed_at = None

    db.session.commit()

    flash(
        f"{task.title} is now marked as "
        f"{new_status.replace('_', ' ')}.",
        "success",
    )
    return redirect(url_for("main.tasks"))
@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("main.index"))
