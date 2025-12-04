# app/__init__.py
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase
from .config import Settings


# We'll fill these when we create the app
engine = None
SessionLocal = None

def create_app() -> Flask:
    """
    App factory: creates the Flask app, database engine, session, and registers routes.
    """
    global engine, SessionLocal

    settings = Settings()  # reads env vars like DATABASE_URL
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY

    # 2. Create the SQLAlchemy engine (connection pool to Postgres)
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=10,
        max_overflow=10,
        pool_pre_ping=True,
    )

    # 3. Create a scoped session (thread-safe session object per request)
    SessionLocal = scoped_session(
        sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
        )
    )

    # Attach to app so other code can reach it
    app.engine = engine
    app.session = SessionLocal

    # 4. Register your blueprints/routes
    from .api import register_blueprints
    register_blueprints(app)

    # 5. Clean up sessions after each request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        SessionLocal.remove()

    return app
