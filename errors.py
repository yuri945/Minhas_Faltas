from flask import render_template
from database import db


def registrar_erros(app):

    @app.errorhandler(404)
    def pagina_nao_encontrada(erro):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def erro_interno(erro):
        db.session.rollback()
        return render_template("500.html"), 500