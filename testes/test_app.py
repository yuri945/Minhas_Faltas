import pytest

from app import app
from database import db
from models.usuario import Usuario


@pytest.fixture
def cliente():

    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.drop_all()
        db.create_all()

        with app.test_client() as cliente:
            yield cliente

        db.session.remove()
        db.drop_all()


def cadastrar_usuario(
    cliente,
    nome="Yuri",
    email="yuri@email.com",
    senha="123456"
):
    return cliente.post(
        "/cadastro",
        data={
            "nome": nome,
            "email": email,
            "senha": senha
        },
        follow_redirects=True
    )


def fazer_login(
    cliente,
    email="yuri@email.com",
    senha="123456"
):
    return cliente.post(
        "/login",
        data={
            "email": email,
            "senha": senha
        },
        follow_redirects=True
    )


def test_pagina_inicial_redireciona_para_login(cliente):

    resposta = cliente.get("/")

    assert resposta.status_code == 302
    assert "/login" in resposta.location


def test_login_abre_normalmente(cliente):

    resposta = cliente.get("/login")

    assert resposta.status_code == 200
    assert "Entrar" in resposta.get_data(as_text=True)


def test_cadastro_abre_normalmente(cliente):

    resposta = cliente.get("/cadastro")

    assert resposta.status_code == 200
    assert "Criar conta" in resposta.get_data(as_text=True)


def test_dashboard_exige_login(cliente):

    resposta = cliente.get("/dashboard")

    assert resposta.status_code == 302
    assert "/login" in resposta.location


def test_pagina_inexistente_retorna_404(cliente):

    resposta = cliente.get("/pagina-inexistente")

    assert resposta.status_code == 404
    assert "Erro 404" in resposta.get_data(as_text=True)


def test_cadastro_cria_usuario_e_faz_login_automatico(cliente):

    resposta = cadastrar_usuario(cliente)

    conteudo = resposta.get_data(as_text=True)

    assert resposta.status_code == 200
    assert "Cadastro realizado com sucesso." in conteudo
    assert "Bem-vindo, Yuri!" in conteudo

    usuario = Usuario.query.filter_by(
        email="yuri@email.com"
    ).first()

    assert usuario is not None
    assert usuario.nome == "Yuri"
    assert usuario.senha != "123456"


def test_cadastro_impede_email_duplicado(cliente):

    cadastrar_usuario(cliente)

    cliente.get("/logout", follow_redirects=True)

    resposta = cadastrar_usuario(cliente)

    conteudo = resposta.get_data(as_text=True)

    assert "Este e-mail já está cadastrado." in conteudo

    quantidade = Usuario.query.filter_by(
        email="yuri@email.com"
    ).count()

    assert quantidade == 1


def test_cadastro_impede_senha_curta(cliente):

    resposta = cadastrar_usuario(
        cliente,
        email="curta@email.com",
        senha="123"
    )

    conteudo = resposta.get_data(as_text=True)

    assert "A senha deve ter pelo menos 6 caracteres." in conteudo

    usuario = Usuario.query.filter_by(
        email="curta@email.com"
    ).first()

    assert usuario is None


def test_logout_encerra_sessao(cliente):

    cadastrar_usuario(cliente)

    resposta = cliente.get(
        "/logout",
        follow_redirects=True
    )

    conteudo = resposta.get_data(as_text=True)

    assert resposta.status_code == 200
    assert "Você saiu da sua conta." in conteudo
    assert "Entrar" in conteudo

    dashboard = cliente.get("/dashboard")

    assert dashboard.status_code == 302
    assert "/login" in dashboard.location


def test_login_com_dados_corretos(cliente):

    cadastrar_usuario(cliente)
    cliente.get("/logout", follow_redirects=True)

    resposta = fazer_login(cliente)

    conteudo = resposta.get_data(as_text=True)

    assert resposta.status_code == 200
    assert "Login realizado com sucesso." in conteudo
    assert "Bem-vindo, Yuri!" in conteudo


def test_login_com_senha_incorreta(cliente):

    cadastrar_usuario(cliente)
    cliente.get("/logout", follow_redirects=True)

    resposta = fazer_login(
        cliente,
        senha="senha-errada"
    )

    conteudo = resposta.get_data(as_text=True)

    assert "E-mail ou senha incorretos." in conteudo
    assert "Bem-vindo, Yuri!" not in conteudo