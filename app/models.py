from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


class FamilyGroup(db.Model):
    """A household group containing Home Secretary users."""

    __tablename__ = "family_groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    invite_code = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    members = db.relationship(
        "User",
        back_populates="family_group",
        lazy=True,
    )

    events = db.relationship(
        "Event",
        back_populates="family_group",
        cascade="all, delete-orphan",
        lazy=True,
    )

    tasks = db.relationship(
        "Task",
        back_populates="family_group",
        cascade="all, delete-orphan",
        lazy=True,
    )

    shopping_items = db.relationship(
        "ShoppingItem",
        back_populates="family_group",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self) -> str:
        return f"<FamilyGroup {self.name}>"


class User(UserMixin, db.Model):
    """A registered Home Secretary user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="member")
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    family_group_id = db.Column(
        db.Integer,
        db.ForeignKey("family_groups.id"),
        nullable=True,
    )

    family_group = db.relationship(
        "FamilyGroup",
        back_populates="members",
    )

    created_events = db.relationship(
        "Event",
        back_populates="creator",
        foreign_keys="Event.created_by_id",
        lazy=True,
    )

    created_tasks = db.relationship(
        "Task",
        back_populates="creator",
        foreign_keys="Task.created_by_id",
        lazy=True,
    )

    assigned_tasks = db.relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assigned_to_id",
        lazy=True,
    )

    added_shopping_items = db.relationship(
        "ShoppingItem",
        back_populates="added_by",
        foreign_keys="ShoppingItem.added_by_id",
        lazy=True,
    )

    purchased_shopping_items = db.relationship(
        "ShoppingItem",
        back_populates="purchased_by",
        foreign_keys="ShoppingItem.purchased_by_id",
        lazy=True,
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Event(db.Model):
    """A shared event belonging to one family group."""

    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    status = db.Column(
        db.String(20),
        nullable=False,
        default="scheduled",
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    family_group_id = db.Column(
        db.Integer,
        db.ForeignKey("family_groups.id"),
        nullable=False,
    )

    created_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    family_group = db.relationship(
        "FamilyGroup",
        back_populates="events",
    )

    creator = db.relationship(
        "User",
        back_populates="created_events",
        foreign_keys=[created_by_id],
    )

    def __repr__(self) -> str:
        return f"<Event {self.title}>"


class Task(db.Model):
    """A household task assigned within a family group."""

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=False)

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="medium",
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    family_group_id = db.Column(
        db.Integer,
        db.ForeignKey("family_groups.id"),
        nullable=False,
    )

    created_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    assigned_to_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    family_group = db.relationship(
        "FamilyGroup",
        back_populates="tasks",
    )

    creator = db.relationship(
        "User",
        back_populates="created_tasks",
        foreign_keys=[created_by_id],
    )

    assignee = db.relationship(
        "User",
        back_populates="assigned_tasks",
        foreign_keys=[assigned_to_id],
    )

    def __repr__(self) -> str:
        return f"<Task {self.title}>"

class ShoppingItem(db.Model):
    """An item on a family's shared shopping list."""

    __tablename__ = "shopping_items"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    quantity = db.Column(
        db.String(50),
        nullable=False,
        default="1",
    )

    category = db.Column(
        db.String(50),
        nullable=False,
        default="groceries",
    )

    notes = db.Column(
        db.Text,
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    purchased_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    family_group_id = db.Column(
        db.Integer,
        db.ForeignKey("family_groups.id"),
        nullable=False,
    )

    added_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    purchased_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
    )

    family_group = db.relationship(
        "FamilyGroup",
        back_populates="shopping_items",
    )

    added_by = db.relationship(
        "User",
        back_populates="added_shopping_items",
        foreign_keys=[added_by_id],
    )

    purchased_by = db.relationship(
        "User",
        back_populates="purchased_shopping_items",
        foreign_keys=[purchased_by_id],
    )

    def __repr__(self) -> str:
        return f"<ShoppingItem {self.name}>"

@login_manager.user_loader
def load_user(user_id: str):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None