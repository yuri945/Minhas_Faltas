from flask import Blueprint, render_template, request, redirect
from database import db
from models.usuario import Usuario
from flask import session

auth = Blueprint("auth", __name__)

@auth.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            return "Este e-mail já está cadastrado."

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=senha
        )

        db.session.add(novo_usuario)
        db.session.commit()

        return redirect("/")

    return render_template("cadastro.html")

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        usuario = Usuario.query.filter_by(
            email=email,
            senha=senha
        ).first()

        if usuario:

            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.nome

            return redirect("/dashboard")

        return "Email ou senha incorretos."

    return render_template("login.html")