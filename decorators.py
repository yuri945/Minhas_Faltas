from functools import wraps
from flask import session, flash, redirect


def login_required(funcao):

    @wraps(funcao)
    def funcao_protegida(*args, **kwargs):

        if "usuario_id" not in session:
            flash("Faça login para continuar.", "erro")
            return redirect("/login")

        return funcao(*args, **kwargs)

    return funcao_protegida