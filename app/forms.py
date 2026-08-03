from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


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