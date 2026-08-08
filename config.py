import os
from dotenv import load_dotenv


load_dotenv()


BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY"
    )

    DATABASE_URL = os.getenv(
        "DATABASE_URL"
    )

    if DATABASE_URL:

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    else:

        DATABASE_NAME = os.getenv(
            "DATABASE_NAME",
            "banco.db"
        )

        DATABASE_FOLDER = os.path.join(
            BASE_DIR,
            "database"
        )

        os.makedirs(
            DATABASE_FOLDER,
            exist_ok=True
        )

        SQLALCHEMY_DATABASE_URI = (
            "sqlite:///"
            + os.path.join(
                DATABASE_FOLDER,
                DATABASE_NAME
            )
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = (
        os.getenv(
            "DEBUG",
            "False"
        ).lower()
        == "true"
    )