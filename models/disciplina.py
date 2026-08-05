from database import db


class Disciplina(db.Model):
    __tablename__ = "disciplinas"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    professor = db.Column(db.String(100))
    dias_semana = db.Column(db.String(100), nullable=False)
    limite_faltas = db.Column(db.Integer, nullable=False)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    usuario = db.relationship(
        "Usuario",
        backref="disciplinas"
    )

    def __repr__(self):
        return f"<Disciplina {self.nome}>"