from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
)


class RegistrationForm(FlaskForm):
    """Form used to create a new user account."""

    full_name = StringField(
        "Full name",
        validators=[
            DataRequired(),
            Length(min=2, max=120),
        ],
    )

    email = StringField(
        "Email address",
        validators=[
            DataRequired(),
            Email(),
            Length(max=120),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(
                min=8,
                message="Password must contain at least 8 characters.",
            ),
        ],
    )

    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo(
                "password",
                message="The passwords must match.",
            ),
        ],
    )

    submit = SubmitField("Create account")


class LoginForm(FlaskForm):
    """Form used to authenticate an existing user."""

    email = StringField(
        "Email address",
        validators=[
            DataRequired(),
            Email(),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
        ],
    )

    remember_me = BooleanField("Remember me")

    submit = SubmitField("Log in")


class CreateFamilyGroupForm(FlaskForm):
    """Form used to create a new family group."""

    name = StringField(
        "Family group name",
        validators=[
            DataRequired(),
            Length(min=2, max=100),
        ],
    )

    submit = SubmitField("Create family group")


class JoinFamilyGroupForm(FlaskForm):
    """Form used to join an existing family group."""

    invite_code = StringField(
        "Invitation code",
        validators=[
            DataRequired(),
            Length(min=6, max=20),
        ],
    )

    submit = SubmitField("Join family group")


class EventForm(FlaskForm):
    """Form used to create or edit a family event."""

    title = StringField(
        "Event title",
        validators=[
            DataRequired(),
            Length(min=2, max=150),
        ],
    )

    event_date = DateField(
        "Date",
        validators=[
            DataRequired(),
        ],
        format="%Y-%m-%d",
    )

    start_time = TimeField(
        "Start time",
        validators=[
            DataRequired(),
        ],
        format="%H:%M",
    )

    location = StringField(
        "Location",
        validators=[
            Optional(),
            Length(max=200),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=1000),
        ],
    )

    submit = SubmitField("Create event")


class TaskForm(FlaskForm):
    """Form used to create or edit a household task."""

    title = StringField(
        "Task title",
        validators=[
            DataRequired(),
            Length(min=2, max=150),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=1000),
        ],
    )

    due_date = DateField(
        "Due date",
        validators=[
            DataRequired(),
        ],
        format="%Y-%m-%d",
    )

    priority = SelectField(
        "Priority",
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
        validators=[
            DataRequired(),
        ],
    )

    assigned_to = SelectField(
        "Assign to",
        coerce=int,
        validators=[
            DataRequired(),
        ],
    )

    submit = SubmitField("Create task")


class ShoppingItemForm(FlaskForm):
    """Form used to create or edit a shopping item."""

    name = StringField(
        "Item",
        validators=[
            DataRequired(),
            Length(min=1, max=150),
        ],
    )

    quantity = StringField(
        "Quantity",
        validators=[
            DataRequired(),
            Length(max=50),
        ],
        default="1",
    )

    category = SelectField(
        "Category",
        choices=[
            ("groceries", "Groceries"),
            ("household", "Household"),
            ("pharmacy", "Pharmacy"),
            ("electronics", "Electronics"),
            ("other", "Other"),
        ],
        validators=[
            DataRequired(),
        ],
    )

    notes = TextAreaField(
        "Notes",
        validators=[
            Optional(),
            Length(max=1000),
        ],
    )

    submit = SubmitField("Save item")