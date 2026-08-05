from sqlalchemy.exc import SQLAlchemyError

from database import db


def salvar_alteracoes():

    try:
        db.session.commit()
        return True

    except SQLAlchemyError as erro:
        db.session.rollback()

        print(
            f"Erro ao salvar alterações no banco: {erro}"
        )

        return False