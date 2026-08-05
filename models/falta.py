from datetime import datetime
from database import db


class Falta(db.Model):
    __tablename__ = "faltas"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    quantidade = db.Column(db.Integer, nullable=False, default=1)

    disciplina_id = db.Column(
        db.Integer,
        db.ForeignKey("disciplinas.id"),
        nullable=False
    )

    disciplina = db.relationship(
        "Disciplina",
        backref="faltas"
    )

    def __repr__(self):
        return f"<Falta {self.disciplina_id} - {self.data}>"