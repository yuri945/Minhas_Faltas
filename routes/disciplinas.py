from flask import Blueprint, render_template, request, redirect, session

from database import db
from models.disciplina import Disciplina


disciplinas = Blueprint("disciplinas", __name__)


@disciplinas.route("/disciplinas/nova", methods=["GET", "POST"])
def nova_disciplina():

    if "usuario_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        nome = request.form["nome"].strip()
        professor = request.form["professor"].strip()
        dias_semana = request.form["dias_semana"].strip()
        limite_faltas = request.form["limite_faltas"]

        nova_disciplina = Disciplina(
            nome=nome,
            professor=professor,
            dias_semana=dias_semana,
            limite_faltas=int(limite_faltas),
            usuario_id=session["usuario_id"]
        )

        db.session.add(nova_disciplina)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("disciplina.html")