from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import db
from decorators import login_required
from models.usuario import Usuario
from services.database_service import salvar_alteracoes


auth = Blueprint("auth", __name__)


@auth.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if "usuario_id" in session:
        return redirect("/dashboard")

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not nome or not email or not senha:
            flash("Preencha todos os campos.", "erro")
            return redirect("/cadastro")

        if len(nome) < 2:
            flash(
                "O nome deve ter pelo menos 2 caracteres.",
                "erro"
            )
            return redirect("/cadastro")

        if len(senha) < 6:
            flash(
                "A senha deve ter pelo menos 6 caracteres.",
                "erro"
            )
            return redirect("/cadastro")

        usuario_existente = Usuario.query.filter_by(
            email=email
        ).first()

        if usuario_existente:
            flash(
                "Este e-mail já está cadastrado.",
                "erro"
            )
            return redirect("/cadastro")

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha)
        )

        db.session.add(novo_usuario)

        if not salvar_alteracoes():
            flash(
                "Não foi possível concluir o cadastro. Tente novamente.",
                "erro"
            )
            return redirect("/cadastro")

        session.clear()
        session["usuario_id"] = novo_usuario.id
        session["usuario_nome"] = novo_usuario.nome

        flash(
            "Cadastro realizado com sucesso.",
            "sucesso"
        )

        return redirect("/dashboard")

    return render_template("cadastro.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if "usuario_id" in session:
        return redirect("/dashboard")

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not email or not senha:
            flash(
                "Informe o e-mail e a senha.",
                "erro"
            )
            return redirect("/login")

        usuario = Usuario.query.filter_by(
            email=email
        ).first()

        if not usuario or not check_password_hash(
            usuario.senha,
            senha
        ):
            flash(
                "E-mail ou senha incorretos.",
                "erro"
            )
            return redirect("/login")

        session.clear()
        session["usuario_id"] = usuario.id
        session["usuario_nome"] = usuario.nome

        flash(
            "Login realizado com sucesso.",
            "sucesso"
        )

        return redirect("/dashboard")

    return render_template("login.html")


@auth.route("/alterar-senha", methods=["GET", "POST"])
@login_required
def alterar_senha():

    usuario = Usuario.query.get_or_404(
        session["usuario_id"]
    )

    if request.method == "POST":
        senha_atual = request.form.get(
            "senha_atual",
            ""
        )

        nova_senha = request.form.get(
            "nova_senha",
            ""
        )

        confirmar_senha = request.form.get(
            "confirmar_senha",
            ""
        )

        if not senha_atual or not nova_senha or not confirmar_senha:
            flash(
                "Preencha todos os campos.",
                "erro"
            )
            return redirect("/alterar-senha")

        if not check_password_hash(
            usuario.senha,
            senha_atual
        ):
            flash(
                "A senha atual está incorreta.",
                "erro"
            )
            return redirect("/alterar-senha")

        if len(nova_senha) < 6:
            flash(
                "A nova senha deve ter pelo menos 6 caracteres.",
                "erro"
            )
            return redirect("/alterar-senha")

        if nova_senha != confirmar_senha:
            flash(
                "A confirmação da senha não corresponde.",
                "erro"
            )
            return redirect("/alterar-senha")

        if check_password_hash(
            usuario.senha,
            nova_senha
        ):
            flash(
                "A nova senha deve ser diferente da senha atual.",
                "erro"
            )
            return redirect("/alterar-senha")

        usuario.senha = generate_password_hash(
            nova_senha
        )

        if not salvar_alteracoes():
            flash(
                "Não foi possível alterar a senha. Tente novamente.",
                "erro"
            )
            return redirect("/alterar-senha")

        flash(
            "Senha alterada com sucesso.",
            "sucesso"
        )

        return redirect("/dashboard")

    return render_template("alterar_senha.html")


@auth.route("/logout")
@login_required
def logout():

    session.clear()

    flash(
        "Você saiu da sua conta.",
        "sucesso"
    )

    return redirect("/login")