# app/api/__init__.py
from flask import Blueprint

# Import blueprints from route modules
# (Ensure each module defines a Blueprint variable with the exact names below)
from .routes.health import health_bp
from .routes.auth import auth_bp
from .routes.me import me_bp
from .routes.simulations import simulation_bp
# add others as they're created:
# from .routes.assets import assets_bp
# from .routes.liabilities import liabilities_bp
from .routes.simulations import simulation_bp
from .routes.challenges import challenges_bp
from .routes.courses import courses_bp
from .routes.scraping_events import scraping_events_bp
from .routes.jobs import jobs_bp
# from .routes.advising import advising_bp

def register_blueprints(app):
    """Attach all API blueprints to the Flask app with a common prefix."""
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1")
    app.register_blueprint(me_bp, url_prefix="/api/v1")
    app.register_blueprint(simulation_bp, url_prefix="/api/v1")
    app.register_blueprint(courses_bp, url_prefix="/api/v1")
    app.register_blueprint(challenges_bp, url_prefix="/api/v1")
    app.register_blueprint(scraping_events_bp, url_prefix="/api/v1")
    app.register_blueprint(jobs_bp, url_prefix="/api/v1")
    # register others as you implement them
