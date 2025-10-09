from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Requirement (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)

@app.route("/")
def start_page():
    return render_template("start.html")
@app.route("/create")
def create_page():
    return render_template("create.html")

@app.route("/aiAgent")
def ai_agent_page():
    return render_template("aiAgent.html")


if  __name__ == "__main__":
    app.run(debug=True) 