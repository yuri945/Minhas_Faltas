from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash
)

from database import db
from decorators import login_required
from models.disciplina import Disciplina
from services.database_service import salvar_alteracoes


disciplinas = Blueprint("disciplinas", __name__)


@disciplinas.route(
    "/disciplinas/nova",
    methods=["GET", "POST"]
)
@login_required
def nova_disciplina():

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        professor = request.form.get("professor", "").strip()
        dias_semana = request.form.get("dias_semana", "").strip()
        limite_faltas = request.form.get(
            "limite_faltas",
            ""
        ).strip()

        if not nome or not dias_semana or not limite_faltas:
            flash(
                "Preencha todos os campos obrigatórios.",
                "erro"
            )
            return redirect("/disciplinas/nova")

        try:
            limite_faltas = int(limite_faltas)

        except ValueError:
            flash(
                "O limite de faltas deve ser um número inteiro.",
                "erro"
            )
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

        if not salvar_alteracoes():
            flash(
                "Não foi possível cadastrar a disciplina.",
                "erro"
            )
            return redirect("/disciplinas/nova")

        flash(
            "Disciplina cadastrada com sucesso.",
            "sucesso"
        )

        return redirect("/dashboard")

    return render_template("disciplina.html")


@disciplinas.route(
    "/disciplinas/<int:disciplina_id>/editar",
    methods=["GET", "POST"]
)
@login_required
def editar_disciplina(disciplina_id):

    disciplina = Disciplina.query.filter_by(
        id=disciplina_id,
        usuario_id=session["usuario_id"]
    ).first_or_404()

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        professor = request.form.get("professor", "").strip()
        dias_semana = request.form.get("dias_semana", "").strip()
        limite_faltas = request.form.get(
            "limite_faltas",
            ""
        ).strip()

        if not nome or not dias_semana or not limite_faltas:
            flash(
                "Preencha todos os campos obrigatórios.",
                "erro"
            )
            return redirect(
                f"/disciplinas/{disciplina.id}/editar"
            )

        try:
            limite_faltas = int(limite_faltas)

        except ValueError:
            flash(
                "O limite de faltas deve ser um número inteiro.",
                "erro"
            )
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

        if not salvar_alteracoes():
            flash(
                "Não foi possível atualizar a disciplina.",
                "erro"
            )
            return redirect(
                f"/disciplinas/{disciplina.id}/editar"
            )

        flash(
            "Disciplina atualizada com sucesso.",
            "sucesso"
        )

        return redirect("/dashboard")

    return render_template(
        "editar_disciplina.html",
        disciplina=disciplina
    )


@disciplinas.route(
    "/disciplinas/<int:disciplina_id>/excluir",
    methods=["POST"]
)
@login_required
def excluir_disciplina(disciplina_id):

    disciplina = Disciplina.query.filter_by(
        id=disciplina_id,
        usuario_id=session["usuario_id"]
    ).first_or_404()

    db.session.delete(disciplina)

    if not salvar_alteracoes():
        flash(
            "Não foi possível excluir a disciplina.",
            "erro"
        )
        return redirect("/dashboard")

    flash(
        "Disciplina excluída com sucesso.",
        "sucesso"
    )

    return redirect("/dashboard")