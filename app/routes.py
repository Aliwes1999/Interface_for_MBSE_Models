from flask import current_app as app, render_template

@app.route("/")
def home():
    return render_template("start.html")

@app.route("/create")
def create():
    return render_template("create.html")
