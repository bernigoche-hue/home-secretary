from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Display the application landing page."""
    return render_template("index.html")