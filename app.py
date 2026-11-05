"""
ScholarTrack — Scholarship & Fellowship Deadline Tracker.
Main Flask Application Factory and Entry Point.
"""
import os
import click
from datetime import datetime, timezone
from flask import Flask, render_template, Response
from config import config_by_name, Config
from extensions import db, login_manager, csrf
from models import User, Source, ScholarshipNotice
from routes.public import public_bp
from routes.auth import auth_bp
from routes.student import student_bp
from routes.admin import admin_bp
from mock_routes import mock_bp
from services.scheduler import init_scheduler, shutdown_scheduler
from services.alert_service import AlertService

def create_app(config_name=None):
    """Application factory for ScholarTrack."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, Config))

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Exclude mock portal endpoints from CSRF if testing
    csrf.exempt(mock_bp)

    # Register blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(mock_bp)

    # Global template context processors
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        unread_count = 0
        if current_user.is_authenticated and not current_user.is_admin():
            unread_count = AlertService.get_unread_count(current_user.id)
        return {
            'now': datetime.now(timezone.utc),
            'unread_alerts_count': unread_count,
            'app_name': 'ScholarTrack'
        }

    @app.route('/favicon.ico')
    def favicon():
        return Response(status=204)

    # Custom Error Pages (Section 16 requirement)
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # CLI Management Commands
    @app.cli.command('create-admin')
    @click.option('--email', prompt=True, help="Admin email address")
    @click.option('--name', prompt=True, help="Admin full name")
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help="Secure password")
    def create_admin_cmd(email, name, password):
        """CLI command to safely create or reset an Administrator account."""
        email = email.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            user.full_name = name
            user.role = 'admin'
            user.set_password(password)
            click.echo(f"Updated existing user '{email}' as Administrator.")
        else:
            user = User(
                email=email,
                full_name=name,
                role='admin'
            )
            user.set_password(password)
            db.session.add(user)
            click.echo(f"Created new Administrator: '{email}'.")
        db.session.commit()

    @app.cli.command('init-db')
    def init_db_cmd():
        """Creates database schema and default records."""
        with app.app_context():
            db.create_all()
            bootstrap_defaults()
            click.echo("Database initialized and bootstrapped successfully.")

    return app

def bootstrap_defaults():
    """Seeds default admin and approved scraping sources if not present."""
    # 1. Default Admin Account
    admin = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            email=Config.ADMIN_EMAIL,
            full_name=Config.ADMIN_NAME,
            role='admin'
        )
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)

    # 2. Approved Sources (At least two distinct layouts + official portals)
    default_sources = [
        {
            'name': 'Global University Scholarship Portal (Portal Alpha)',
            'code': 'portal_alpha',
            'base_url': 'http://127.0.0.1:5000',
            'listing_url': 'http://127.0.0.1:5000/mock/portal-alpha',
            'adapter_name': 'university_portal',
            'request_interval_minutes': 60
        },
        {
            'name': 'International Research Grants Board (Portal Beta)',
            'code': 'portal_beta',
            'base_url': 'http://127.0.0.1:5000',
            'listing_url': 'http://127.0.0.1:5000/mock/portal-beta',
            'adapter_name': 'research_grants',
            'request_interval_minutes': 60
        },
        {
            'name': 'Reliance Foundation Scholarships Official Portal',
            'code': 'reliance_foundation',
            'base_url': 'https://www.reliancefoundation.org',
            'listing_url': 'https://www.reliancefoundation.org/media/media-release/Reliance_Foundation_Scholarships_2026-27',
            'adapter_name': 'university_portal',
            'request_interval_minutes': 60
        },
        {
            'name': 'National Scholarship Portal (NSP - Govt of India)',
            'code': 'nsp_portal',
            'base_url': 'https://scholarships.gov.in',
            'listing_url': 'https://scholarships.gov.in/',
            'adapter_name': 'university_portal',
            'request_interval_minutes': 60
        },
        {
            'name': 'Buddy4Study Academic Scholarships Portal',
            'code': 'buddy4study',
            'base_url': 'https://www.buddy4study.com',
            'listing_url': 'https://www.buddy4study.com/',
            'adapter_name': 'university_portal',
            'request_interval_minutes': 60
        },
        {
            'name': "Prime Minister's Research Fellowship (PMRF)",
            'code': 'pmrf_portal',
            'base_url': 'https://www.pmrf.in',
            'listing_url': 'https://www.pmrf.in/',
            'adapter_name': 'research_grants',
            'request_interval_minutes': 60
        }
    ]

    for s_data in default_sources:
        if not Source.query.filter_by(code=s_data['code']).first():
            src = Source(
                name=s_data['name'],
                code=s_data['code'],
                base_url=s_data['base_url'],
                listing_url=s_data['listing_url'],
                adapter_name=s_data['adapter_name'],
                request_interval_minutes=s_data['request_interval_minutes'],
                is_enabled=True,
                status='active'
            )
            db.session.add(src)

    db.session.commit()

def setup_database_and_sources(application):
    """Initializes tables, seeds defaults, and starts background scheduler."""
    with application.app_context():
        db.create_all()
        bootstrap_defaults()

        if ScholarshipNotice.query.count() == 0:
            from scraper import ScraperEngine
            sources = Source.query.filter_by(is_enabled=True).all()
            for s in sources:
                try:
                    ScraperEngine.scrape_source(s.id)
                except Exception:
                    pass

    # Initialize scheduler in production or non-reloader mode
    if not application.config.get('TESTING'):
        init_scheduler(application)

# Create application instance for WSGI / CLI
app = create_app()

if __name__ == '__main__':
    setup_database_and_sources(app)
    try:
        app.run(host='127.0.0.1', port=5000, debug=True)
    finally:
        shutdown_scheduler()
