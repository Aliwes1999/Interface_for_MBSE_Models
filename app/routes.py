from flask import render_template, request, redirect, url_for
from . import bp

# Global list to store requirements (in-memory, resets on restart)
requirements = [
    {'id': 1, 'title': 'Beispieltitle', 'beschreibung': 'Beispielbeschreibung', 'kategorie': 'Beispielkategorie', 'status': 'Offen'}
]

@bp.route("/")
def home():
    return render_template("start.html")

@bp.route("/create", methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        beschreibung = request.form.get('beschreibung')
        kategorie = request.form.get('kategorie')
        if title and beschreibung and kategorie:
            new_id = max([r['id'] for r in requirements]) + 1 if requirements else 1
            requirements.append({
                'id': new_id,
                'title': title,
                'beschreibung': beschreibung,
                'kategorie': kategorie,
                'status': 'Offen'
            })
        return redirect(url_for('main.create'))
    return render_template("create.html", requirements=requirements)

@bp.route("/mark/<int:req_id>")
def mark(req_id):
    for req in requirements:
        if req['id'] == req_id:
            req['status'] = 'Erledigt' if req['status'] == 'Offen' else 'Offen'
            break
    return redirect(url_for('main.create'))

@bp.route("/delete/<int:req_id>")
def delete(req_id):
    global requirements
    requirements = [req for req in requirements if req['id'] != req_id]
    return redirect(url_for('main.create'))

@bp.route("/hello")
def hello():
    return "Hello from Blueprint!"
