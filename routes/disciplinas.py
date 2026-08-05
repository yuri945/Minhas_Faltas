from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
)

from database import db
from models.disciplina import Disciplina


disciplinas = Blueprint("disciplinas", __name__)


@disciplinas.route(
    "/disciplinas/nova",
    methods=["GET", "POST"]
)
def nova_disciplina():

    if "usuario_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        nome = request.form["nome"].strip()
        professor = request.form["professor"].strip()
        dias_semana = request.form["dias_semana"].strip()
        limite_faltas = request.form["limite_faltas"]

        nova = Disciplina(
            nome=nome,
            professor=professor,
            dias_semana=dias_semana,
            limite_faltas=int(limite_faltas),
            usuario_id=session["usuario_id"]
        )

        db.session.add(nova)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("disciplina.html")


@disciplinas.route(
    "/disciplinas/<int:disciplina_id>/editar",
    methods=["GET", "POST"]
)
def editar_disciplina(disciplina_id):

    if "usuario_id" not in session:
        return redirect("/login")

    disciplina = Disciplina.query.filter_by(
        id=disciplina_id,
        usuario_id=session["usuario_id"]
    ).first_or_404()

    if request.method == "POST":
        disciplina.nome = request.form["nome"].strip()
        disciplina.professor = request.form["professor"].strip()
        disciplina.dias_semana = request.form["dias_semana"].strip()
        disciplina.limite_faltas = int(
            request.form["limite_faltas"]
        )

        db.session.commit()

        return redirect("/dashboard")

    return render_template(
        "editar_disciplina.html",
        disciplina=disciplina
    )


@disciplinas.route(
    "/disciplinas/<int:disciplina_id>/excluir",
    methods=["POST"]
)
def excluir_disciplina(disciplina_id):

    if "usuario_id" not in session:
        return redirect("/login")

    disciplina = Disciplina.query.filter_by(
        id=disciplina_id,
        usuario_id=session["usuario_id"]
    ).first_or_404()

    db.session.delete(disciplina)
    db.session.commit()

    return redirect("/dashboard")