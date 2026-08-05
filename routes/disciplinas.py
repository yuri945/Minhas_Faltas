from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash
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
        flash("Faça login para continuar.", "erro")
        return redirect("/login")

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        professor = request.form.get("professor", "").strip()
        dias_semana = request.form.get("dias_semana", "").strip()
        limite_faltas = request.form.get("limite_faltas", "").strip()

        if not nome or not dias_semana or not limite_faltas:
            flash("Preencha todos os campos obrigatórios.", "erro")
            return redirect("/disciplinas/nova")

        try:
            limite_faltas = int(limite_faltas)
        except ValueError:
            flash("O limite de faltas deve ser um número inteiro.", "erro")
            return redirect("/disciplinas/nova")

        if limite_faltas <= 0:
            flash(
                "O limite de faltas deve ser maior que zero.",
                "erro"
            )
            return redirect("/disciplinas/nova")

        nova = Disciplina(
            nome=nome,
            professor=professor,
            dias_semana=dias_semana,
            limite_faltas=limite_faltas,
            usuario_id=session["usuario_id"]
        )

        db.session.add(nova)
        db.session.commit()

        flash("Disciplina cadastrada com sucesso.", "sucesso")
        return redirect("/dashboard")

    return render_template("disciplina.html")


@disciplinas.route(
    "/disciplinas/<int:disciplina_id>/editar",
    methods=["GET", "POST"]
)
def editar_disciplina(disciplina_id):

    if "usuario_id" not in session:
        flash("Faça login para continuar.", "erro")
        return redirect("/login")

    disciplina = Disciplina.query.filter_by(
        id=disciplina_id,
        usuario_id=session["usuario_id"]
    ).first_or_404()

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        professor = request.form.get("professor", "").strip()
        dias_semana = request.form.get("dias_semana", "").strip()
        limite_faltas = request.form.get("limite_faltas", "").strip()

        if not nome or not dias_semana or not limite_faltas:
            flash("Preencha todos os campos obrigatórios.", "erro")
            return redirect(
                f"/disciplinas/{disciplina.id}/editar"
            )

        try:
            limite_faltas = int(limite_faltas)
        except ValueError:
            flash("O limite de faltas deve ser um número inteiro.", "erro")
            return redirect(
                f"/disciplinas/{disciplina.id}/editar"
            )

        if limite_faltas <= 0:
            flash(
                "O limite de faltas deve ser maior que zero.",
                "erro"
            )
            return redirect(
                f"/disciplinas/{disciplina.id}/editar"
            )

        disciplina.nome = nome
        disciplina.professor = professor
        disciplina.dias_semana = dias_semana
        disciplina.limite_faltas = limite_faltas

        db.session.commit()

        flash("Disciplina atualizada com sucesso.", "sucesso")
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
        flash("Faça login para continuar.", "erro")
        return redirect("/login")

    disciplina = Disciplina.query.filter_by(
        id=disciplina_id,
        usuario_id=session["usuario_id"]
    ).first_or_404()

    db.session.delete(disciplina)
    db.session.commit()

    flash("Disciplina excluída com sucesso.", "sucesso")
    return redirect("/dashboard")