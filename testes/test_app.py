import pytest

from app import app
from database import db
from models.usuario import Usuario
from models.disciplina import Disciplina
from models.falta import Falta


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

def test_usuario_consegue_cadastrar_disciplina(cliente):

    cadastrar_usuario(cliente)

    resposta = cliente.post(
        "/disciplinas/nova",
        data={
            "nome": "Banco de Dados",
            "professor": "Luciano",
            "dias_semana": "Segunda-feira",
            "limite_faltas": "10"
        },
        follow_redirects=True
    )

    conteudo = resposta.get_data(as_text=True)

    assert resposta.status_code == 200
    assert "Disciplina cadastrada com sucesso." in conteudo
    assert "Banco de Dados" in conteudo

    disciplina = Disciplina.query.filter_by(
        nome="Banco de Dados"
    ).first()

    assert disciplina is not None
    assert disciplina.professor == "Luciano"
    assert disciplina.limite_faltas == 10
    assert disciplina.usuario_id is not None


def test_usuario_consegue_editar_disciplina(cliente):

    cadastrar_usuario(cliente)

    cliente.post(
        "/disciplinas/nova",
        data={
            "nome": "Banco de Dados",
            "professor": "Luciano",
            "dias_semana": "Segunda-feira",
            "limite_faltas": "10"
        },
        follow_redirects=True
    )

    disciplina = Disciplina.query.filter_by(
        nome="Banco de Dados"
    ).first()

    resposta = cliente.post(
        f"/disciplinas/{disciplina.id}/editar",
        data={
            "nome": "Banco de Dados II",
            "professor": "Carlos",
            "dias_semana": "Quarta-feira",
            "limite_faltas": "12"
        },
        follow_redirects=True
    )

    conteudo = resposta.get_data(as_text=True)

    assert resposta.status_code == 200
    assert "Disciplina atualizada com sucesso." in conteudo

    disciplina_atualizada = db.session.get(
        Disciplina,
        disciplina.id
    )

    assert disciplina_atualizada.nome == "Banco de Dados II"
    assert disciplina_atualizada.professor == "Carlos"
    assert disciplina_atualizada.dias_semana == "Quarta-feira"
    assert disciplina_atualizada.limite_faltas == 12


def test_usuario_consegue_adicionar_e_remover_falta(cliente):

    cadastrar_usuario(cliente)

    cliente.post(
        "/disciplinas/nova",
        data={
            "nome": "Engenharia de Software",
            "professor": "João",
            "dias_semana": "Terça-feira",
            "limite_faltas": "8"
        },
        follow_redirects=True
    )

    disciplina = Disciplina.query.filter_by(
        nome="Engenharia de Software"
    ).first()

    resposta_adicionar = cliente.post(
        f"/disciplinas/{disciplina.id}/faltas/adicionar",
        follow_redirects=True
    )

    conteudo_adicionar = resposta_adicionar.get_data(
        as_text=True
    )

    assert "Falta adicionada" in conteudo_adicionar

    quantidade_faltas = Falta.query.filter_by(
        disciplina_id=disciplina.id
    ).count()

    assert quantidade_faltas == 1

    resposta_remover = cliente.post(
        f"/disciplinas/{disciplina.id}/faltas/remover",
        follow_redirects=True
    )

    conteudo_remover = resposta_remover.get_data(
        as_text=True
    )

    assert "Última falta removida" in conteudo_remover

    quantidade_faltas = Falta.query.filter_by(
        disciplina_id=disciplina.id
    ).count()

    assert quantidade_faltas == 0


def test_excluir_disciplina_remove_suas_faltas(cliente):

    cadastrar_usuario(cliente)

    cliente.post(
        "/disciplinas/nova",
        data={
            "nome": "Estrutura de Dados",
            "professor": "Marcos",
            "dias_semana": "Quinta-feira",
            "limite_faltas": "10"
        },
        follow_redirects=True
    )

    disciplina = Disciplina.query.filter_by(
        nome="Estrutura de Dados"
    ).first()

    cliente.post(
        f"/disciplinas/{disciplina.id}/faltas/adicionar",
        follow_redirects=True
    )

    disciplina_id = disciplina.id

    resposta = cliente.post(
        f"/disciplinas/{disciplina_id}/excluir",
        follow_redirects=True
    )

    conteudo = resposta.get_data(as_text=True)

    assert "Disciplina excluída com sucesso." in conteudo

    disciplina_excluida = db.session.get(
        Disciplina,
        disciplina_id
    )

    faltas_restantes = Falta.query.filter_by(
        disciplina_id=disciplina_id
    ).count()

    assert disciplina_excluida is None
    assert faltas_restantes == 0


def test_usuario_nao_acessa_disciplina_de_outro_usuario(cliente):

    cadastrar_usuario(
        cliente,
        nome="Yuri",
        email="yuri@email.com",
        senha="123456"
    )

    cliente.post(
        "/disciplinas/nova",
        data={
            "nome": "Disciplina do Yuri",
            "professor": "Professor A",
            "dias_semana": "Segunda-feira",
            "limite_faltas": "10"
        },
        follow_redirects=True
    )

    disciplina_yuri = Disciplina.query.filter_by(
        nome="Disciplina do Yuri"
    ).first()

    disciplina_id = disciplina_yuri.id

    cliente.get(
        "/logout",
        follow_redirects=True
    )

    cadastrar_usuario(
        cliente,
        nome="João",
        email="joao@email.com",
        senha="654321"
    )

    resposta_editar = cliente.get(
        f"/disciplinas/{disciplina_id}/editar"
    )

    resposta_adicionar_falta = cliente.post(
        f"/disciplinas/{disciplina_id}/faltas/adicionar"
    )

    resposta_excluir = cliente.post(
        f"/disciplinas/{disciplina_id}/excluir"
    )

    assert resposta_editar.status_code == 404
    assert resposta_adicionar_falta.status_code == 404
    assert resposta_excluir.status_code == 404

    disciplina_ainda_existe = db.session.get(
        Disciplina,
        disciplina_id
    )

    assert disciplina_ainda_existe is not None

    faltas = Falta.query.filter_by(
        disciplina_id=disciplina_id
    ).count()

    assert faltas == 0