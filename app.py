from flask import Flask, session, redirect, render_template, send_from_directory
from sqlalchemy import func

from config import Config
from database import db
from decorators import login_required

from models.usuario import Usuario
from models.disciplina import Disciplina
from models.falta import Falta

from routes.auth import auth
from routes.disciplinas import disciplinas
from routes.faltas import faltas

from extensions import csrf, migrate, limiter

from errors import registrar_erros  

from werkzeug.middleware.proxy_fix import ProxyFix



app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
csrf.init_app(app)
migrate.init_app(app, db)
registrar_erros(app)
limiter.init_app(app)
app.register_blueprint(auth)
app.register_blueprint(disciplinas)
app.register_blueprint(faltas)

app = Flask(__name__)
app.config.from_object(Config)

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1
)


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


@app.route("/service-worker.js")
def service_worker():
    return send_from_directory(
        app.static_folder,
        "service-worker.js",
        mimetype="application/javascript"
    )


if __name__ == "__main__":
    app.run(
        debug=app.config["DEBUG"]
    )


