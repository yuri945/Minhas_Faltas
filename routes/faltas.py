from datetime import datetime

from flask import Blueprint, redirect, session

from database import db
from models.disciplina import Disciplina
from models.falta import Falta


faltas = Blueprint("faltas", __name__)


@faltas.route(
    "/disciplinas/<int:disciplina_id>/faltas/adicionar",
    methods=["POST"]
)
def adicionar_falta(disciplina_id):

    if "usuario_id" not in session:
        return redirect("/login")

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
    db.session.commit()

    return redirect("/dashboard")


@faltas.route(
    "/disciplinas/<int:disciplina_id>/faltas/remover",
    methods=["POST"]
)
def remover_falta(disciplina_id):

    if "usuario_id" not in session:
        return redirect("/login")

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

    if ultima_falta:
        db.session.delete(ultima_falta)
        db.session.commit()

    return redirect("/dashboard")