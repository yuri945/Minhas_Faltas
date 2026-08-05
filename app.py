from flask import Flask, render_template, request, redirect
from flask import Flask
from config import Config
from database import db


# Importa os modelos
from models.usuario import Usuario
from routes.auth import auth

app = Flask(__name__)
app.config.from_object(Config)

# Inicializa o banco de dados
db.init_app(app)

app.register_blueprint(auth)

@app.route("/")
def home():
    return "<h1>Controle de Faltas</h1>"

# Cria as tabelas do banco
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])

from flask import session

@app.route("/dashboard")
def dashboard():

    if "usuario_id" not in session:
        return redirect("/login")

    return f"""
    <h1>Bem-vindo, {session['usuario_nome']}!</h1>

    <p>Essa será sua página principal.</p>
    """