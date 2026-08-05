from flask import Flask, session, redirect, render_template
from sqlalchemy import func

from config import Config
from database import db
from decorators import login_required
from extensions import csrf

from models.usuario import Usuario
from models.disciplina import Disciplina
from models.falta import Falta

from routes.auth import auth
from routes.disciplinas import disciplinas
from routes.faltas import faltas

from extensions import csrf, migrate

from errors import registrar_erros  


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
csrf.init_app(app)
migrate.init_app(app, db)

app.register_blueprint(auth)
app.register_blueprint(disciplinas)
app.register_blueprint(faltas)

registrar_erros(app)


@app.route("/")
def home():

    if "usuario_id" in session:
        return redirect("/dashboard")

    return redirect("/login")


@app.route("/dashboard")
@login_required
def dashboard():

    disciplinas_usuario = (
        Disciplina.query
        .filter_by(usuario_id=session["usuario_id"])
        .order_by(Disciplina.nome.asc())
        .all()
    )

    disciplinas_com_faltas = []

    for disciplina in disciplinas_usuario:

        total_faltas = (
            db.session.query(
                func.coalesce(
                    func.sum(Falta.quantidade),
                    0
                )
            )
            .filter(
                Falta.disciplina_id == disciplina.id
            )
            .scalar()
        )

        total_faltas = int(total_faltas)

        if disciplina.limite_faltas > 0:
            percentual = round(
                (
                    total_faltas
                    / disciplina.limite_faltas
                ) * 100
            )
        else:
            percentual = 0

        if percentual >= 100:
            status = "Limite atingido"

        elif percentual >= 80:
            status = "Atenção"

        else:
            status = "Situação tranquila"

        disciplinas_com_faltas.append({
            "disciplina": disciplina,
            "total_faltas": total_faltas,
            "percentual": percentual,
            "status": status
        })

    return render_template(
        "dashboard.html",
        usuario_nome=session["usuario_nome"],
        disciplinas=disciplinas_com_faltas
    )


if __name__ == "__main__":
    app.run(
        debug=app.config["DEBUG"]
    )