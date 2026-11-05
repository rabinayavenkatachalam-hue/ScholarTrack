"""
ScholarTrack SQLAlchemy Database Models.
Implements relational models for Users, Scholarship Notices, Sources,
Scrape Jobs, Change History, Bookmarks, and Alerts.
"""
from datetime import datetime, timezone
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """User account model for Students and Administrators."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student' or 'admin'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    saved_scholarships = db.relationship('SavedScholarship', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    alerts = db.relationship('UserAlert', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hashes password using secure PBKDF2/scrypt."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies plain text password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Returns True if user has the administrative role."""
        return self.role == 'admin'

    def has_saved(self, notice_id):
        """Check if user has bookmarked a given scholarship notice."""
        return self.saved_scholarships.filter_by(notice_id=notice_id).first() is not None

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'

class Source(db.Model):
    """Configured public announcement source or portal."""
    __tablename__ = 'sources'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    base_url = db.Column(db.String(255), nullable=False)
    listing_url = db.Column(db.String(255), nullable=False)
    adapter_name = db.Column(db.String(50), nullable=False)  # e.g., 'university_portal', 'research_grants'
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)
    request_interval_minutes = db.Column(db.Integer, default=60, nullable=False)
    last_checked_at = db.Column(db.DateTime, nullable=True)
    last_success_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active', nullable=False)  # 'active', 'degraded', 'failing', 'disabled'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    notices = db.relationship('ScholarshipNotice', backref='source', lazy='dynamic')
    jobs = db.relationship('ScrapeJob', backref='source', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Source {self.code}: {self.name}>'

class ScholarshipNotice(db.Model):
    """Scholarship or Fellowship opportunity notice record."""
    __tablename__ = 'scholarship_notices'

    id = db.Column(db.Integer, primary_key=True)
    notice_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=True)
    url = db.Column(db.String(500), nullable=False)
    notice_type = db.Column(db.String(50), default='Scholarship', nullable=False)
    title = db.Column(db.String(255), nullable=False)
    provider = db.Column(db.String(255), nullable=False)
    education_level = db.Column(db.String(50), default='All Levels', nullable=False)
    discipline = db.Column(db.String(100), default='General / All Disciplines', nullable=False)
    region = db.Column(db.String(100), default='International / Global', nullable=False)
    benefit_text = db.Column(db.Text, nullable=True)
    eligibility_excerpt = db.Column(db.Text, nullable=True)
    due_at = db.Column(db.DateTime, nullable=True)  # Strictly None for rolling/unknown deadlines
    timezone = db.Column(db.String(20), default='UTC', nullable=False)
    captured_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_checked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    verified_at = db.Column(db.DateTime, nullable=True)
    content_hash = db.Column(db.String(64), nullable=True)
    notice_status = db.Column(db.String(30), default='active', nullable=False)  # 'active', 'updated', 'withdrawn', 'manual_review'
    previous_deadline = db.Column(db.DateTime, nullable=True)
    updated_deadline = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=True, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    history = db.relationship('NoticeHistory', backref='notice', lazy='dynamic', cascade='all, delete-orphan', order_by='NoticeHistory.detected_at.desc()')
    saved_by = db.relationship('SavedScholarship', backref='notice', lazy='dynamic', cascade='all, delete-orphan')
    alerts = db.relationship('UserAlert', backref='notice', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def days_remaining(self):
        """Calculates days remaining until deadline. Returns None if due_at is None."""
        if not self.due_at:
            return None
        now = datetime.now(timezone.utc)
        target = self.due_at
        if target.tzinfo is None:
            target = target.replace(tzinfo=timezone.utc)
        delta = target - now
        return delta.days

    @property
    def deadline_status(self):
        """
        Classifies deadline status strictly without arbitrary dates:
        - 'unknown': when due_at is None
        - 'expired': when target < now
        - 'closing_soon_7d': between 0 and 7 days
        - 'closing_soon_30d': between 8 and 30 days
        - 'upcoming': more than 30 days
        """
        if not self.due_at:
            return 'unknown'
        now = datetime.now(timezone.utc)
        target = self.due_at
        if target.tzinfo is None:
            target = target.replace(tzinfo=timezone.utc)
        if target < now:
            return 'expired'
        delta = target - now
        if delta.days <= 7:
            return 'closing_soon_7d'
        elif delta.days <= 30:
            return 'closing_soon_30d'
        return 'upcoming'

    @property
    def is_expired(self):
        """Returns True if due_at is in the past."""
        if not self.due_at:
            return False
        now = datetime.now(timezone.utc)
        target = self.due_at
        if target.tzinfo is None:
            target = target.replace(tzinfo=timezone.utc)
        return target < now

    @staticmethod
    def calculate_content_hash(title, provider, due_at_iso, eligibility, benefit, status):
        """Calculates stable SHA256 content hash of normalized announcement fields."""
        data = f"{title.strip().lower()}|{provider.strip().lower()}|{str(due_at_iso)}|{(eligibility or '').strip().lower()}|{(benefit or '').strip().lower()}|{status.strip().lower()}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def __repr__(self):
        return f'<ScholarshipNotice {self.notice_id}: {self.title}>'

class NoticeHistory(db.Model):
    """Historical audit trail of detected changes to an announcement."""
    __tablename__ = 'notice_history'

    id = db.Column(db.Integer, primary_key=True)
    notice_id = db.Column(db.Integer, db.ForeignKey('scholarship_notices.id'), nullable=False)
    change_type = db.Column(db.String(50), nullable=False)  # 'deadline_extension', 'deadline_shortened', 'eligibility_modified', 'benefit_updated', 'status_changed', 'notice_withdrawn'
    field_changed = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    detected_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    source_evidence_url = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f'<NoticeHistory notice_id={self.notice_id} {self.change_type}>'

class ScrapeJob(db.Model):
    """Audit log of individual scraping job runs."""
    __tablename__ = 'scrape_jobs'

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=True)
    status = db.Column(db.String(20), default='running', nullable=False)  # 'running', 'completed', 'failed'
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    finished_at = db.Column(db.DateTime, nullable=True)
    records_found = db.Column(db.Integer, default=0)
    records_added = db.Column(db.Integer, default=0)
    records_updated = db.Column(db.Integer, default=0)
    revisions_detected = db.Column(db.Integer, default=0)
    http_status = db.Column(db.Integer, nullable=True)
    execution_time_ms = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text, nullable=True)
    log_excerpt = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<ScrapeJob {self.id} status={self.status}>'

class SavedScholarship(db.Model):
    """Student bookmark record linking User to ScholarshipNotice."""
    __tablename__ = 'saved_scholarships'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notice_id = db.Column(db.Integer, db.ForeignKey('scholarship_notices.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    notes = db.Column(db.Text, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'notice_id', name='uq_user_notice_bookmark'),
    )

    def __repr__(self):
        return f'<SavedScholarship user={self.user_id} notice={self.notice_id}>'

class UserAlert(db.Model):
    """In-app alert notification delivered to students."""
    __tablename__ = 'user_alerts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notice_id = db.Column(db.Integer, db.ForeignKey('scholarship_notices.id'), nullable=True)
    alert_type = db.Column(db.String(50), nullable=False)  # 'deadline_changed', 'eligibility_updated', 'status_withdrawn', 'deadline_approaching'
    message = db.Column(db.Text, nullable=False)
    previous_deadline = db.Column(db.DateTime, nullable=True)
    updated_deadline = db.Column(db.DateTime, nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<UserAlert user={self.user_id} type={self.alert_type} read={self.is_read}>'
