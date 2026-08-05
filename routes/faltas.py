from datetime import datetime

from flask import (
    Blueprint,
    redirect,
    render_template,
    session,
    flash
)

from database import db
from decorators import login_required
from models.disciplina import Disciplina
from models.falta import Falta
from services.database_service import salvar_alteracoes


faltas = Blueprint("faltas", __name__)


@faltas.route(
    "/disciplinas/<int:disciplina_id>/faltas/adicionar",
    methods=["POST"]
)
@login_required
def adicionar_falta(disciplina_id):

    disciplina = Disciplina.query.filter_by(
        id=disciplina_id,
        usuario_id=session["usuario_id"]
    ).first_or_404()

    nova_falta = Falta(
        data=datetime.now().date(),
        quantidade=1,
        disciplina_id=disciplina.id
    )

    db.session.add(nova_falta)

    if not salvar_alteracoes():
        flash(
            "Não foi possível adicionar a falta.",
            "erro"
        )
        return redirect("/dashboard")

    flash(
        f"Falta adicionada em {disciplina.nome}.",
        "sucesso"
    )

    return redirect("/dashboard")


@faltas.route(
    "/disciplinas/<int:disciplina_id>/faltas/remover",
    methods=["POST"]
)
@login_required
def remover_falta(disciplina_id):

    disciplina = Disciplina.query.filter_by(
        id=disciplina_id,
        usuario_id=session["usuario_id"]
    ).first_or_404()

    ultima_falta = (
        Falta.query
        .filter_by(disciplina_id=disciplina.id)
        .order_by(Falta.id.desc())
        .first()
    )

    if not ultima_falta:
        flash(
            "Essa disciplina não possui faltas para remover.",
            "erro"
        )
        return redirect("/dashboard")

    db.session.delete(ultima_falta)

    if not salvar_alteracoes():
        flash(
            "Não foi possível remover a falta.",
            "erro"
        )
        return redirect("/dashboard")

    flash(
        f"Última falta removida de {disciplina.nome}.",
        "sucesso"
    )

    return redirect("/dashboard")


@faltas.route(
    "/disciplinas/<int:disciplina_id>/faltas"
)
@login_required
def historico_faltas(disciplina_id):

    disciplina = Disciplina.query.filter_by(
        id=disciplina_id,
        usuario_id=session["usuario_id"]
    ).first_or_404()

    registros = (
        Falta.query
        .filter_by(disciplina_id=disciplina.id)
        .order_by(
            Falta.data.desc(),
            Falta.id.desc()
        )
        .all()
    )

    total_faltas = sum(
        registro.quantidade
        for registro in registros
    )

    return render_template(
        "historico_faltas.html",
        disciplina=disciplina,
        registros=registros,
        total_faltas=total_faltas
    )