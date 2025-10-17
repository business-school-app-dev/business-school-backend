import os
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase
from .config import Settings

class Base(DeclarativeBase):
    pass

engine = None
SessionLocal = None


def create_app() -> Flask:
    global engine, SessionLocal

    settings = Settings()  # reads env
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY

    # DB engine + session
    engine = create_engine(
        settings.DATABASE_URL, pool_size=10, max_overflow=10, pool_pre_ping=True
    )
    SessionLocal = scoped_session(
        sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    )

    app.session = SessionLocal
    app.engine = engine

    from .api import register_blueprints
    register_blueprints(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        SessionLocal.remove()

    return app