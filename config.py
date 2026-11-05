"""
ScholarTrack Configuration Module.
Loads environment variables and sets application configuration parameters.
"""
import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Load .env file if it exists
load_dotenv(os.path.join(BASE_DIR, '.env'))

INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
os.makedirs(INSTANCE_DIR, exist_ok=True)
DEFAULT_DB_PATH = os.path.join(INSTANCE_DIR, 'scholartrack.db')

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'scholartrack-super-secret-key-2026-prod-fallback')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DEFAULT_DB_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    # Scheduler configuration
    SCHEDULER_API_ENABLED = False
    SCRAPING_INTERVAL_MINUTES = int(os.environ.get('SCRAPING_INTERVAL_MINUTES', 60))

    # Web Scraping Ethics & Reliability Controls
    CRAWLER_USER_AGENT = os.environ.get(
        'CRAWLER_USER_AGENT',
        'ScholarTrackBot/2.0 (+https://scholartrack.edu/bot; academic research deadline tracker)'
    )
    REQUEST_TIMEOUT_SECONDS = int(os.environ.get('REQUEST_TIMEOUT_SECONDS', 10))
    MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 3))
    BACKOFF_FACTOR = float(os.environ.get('BACKOFF_FACTOR', 1.5))
    RESPECT_ROBOTS_TXT = os.environ.get('RESPECT_ROBOTS_TXT', 'True').lower() in ('true', '1', 'yes')

    # SSRF Protection: Approved Hosts Allowlists
    APPROVED_HOSTS = [
        h.strip().lower() for h in os.environ.get(
            'APPROVED_HOSTS',
            'localhost,127.0.0.1,example.edu,example.org,grants.gov,nsf.gov,fulbrightonline.org,daad.de,reliancefoundation.org,buddy4study.com,scholarships.gov.in,gov.in,nic.in,pmrf.in,turing.ac.uk,ox.ac.uk,europa.eu,who.int,usief.org.in'
        ).split(',') if h.strip()
    ]

    # Admin bootstrap credentials
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@scholartrack.edu')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@ScholarTrack2026!')
    ADMIN_NAME = os.environ.get('ADMIN_NAME', 'ScholarTrack Lead Admin')

class TestingConfig(Config):
    """Configuration for automated test execution."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key-for-pytest'
    RESPECT_ROBOTS_TXT = False
    REQUEST_TIMEOUT_SECONDS = 3
    MAX_RETRIES = 1

config_by_name = {
    'development': Config,
    'testing': TestingConfig,
    'production': Config,
    'default': Config
}
