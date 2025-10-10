from flask import render_template
from . import bp

@bp.route("/")
def home():
    return render_template("start.html")

@bp.route("/create")
def create():
    return render_template("create.html")

@bp.route("/hello")
def hello():
    return "Hello from Blueprint!"
