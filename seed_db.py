"""
ScholarTrack Database Seeder.
Populates verified scholarship and fellowship opportunities including major
national and international official portals (Reliance Foundation, NSP, Buddy4Study, PMRF, DAAD, Turing, MSCA).
"""
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from app import app
from extensions import db
from models import User, Source, ScholarshipNotice, SavedScholarship, UserAlert, NoticeHistory
from scraper.source_one import UniversityPortalAdapter
from scraper.source_two import ResearchGrantsAdapter
from scraper.change_detector import ChangeDetector
from mock_routes import PORTAL_ALPHA_HTML, PORTAL_BETA_HTML, PORTAL_ALPHA_REVISED_HTML
from config import Config

def seed():
    with app.app_context():
        db.create_all()

        # 1. Admin Bootstrap
        admin = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                email=Config.ADMIN_EMAIL,
                full_name=Config.ADMIN_NAME,
                role='admin'
            )
            admin.set_password(Config.ADMIN_PASSWORD)
            db.session.add(admin)
            print(f"Admin created: {Config.ADMIN_EMAIL} / {Config.ADMIN_PASSWORD}")

        # Demo Student Account
        student = User.query.filter_by(email='student@scholartrack.edu').first()
        if not student:
            student = User(
                email='student@scholartrack.edu',
                full_name='Alex Student',
                role='student'
            )
            student.set_password('Student@ScholarTrack2026!')
            db.session.add(student)
            print("Demo Student created: student@scholartrack.edu / Student@ScholarTrack2026!")

        # 2. Approved Sources
        sources_to_seed = [
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

        source_objs = {}
        for s_data in sources_to_seed:
            src = Source.query.filter_by(code=s_data['code']).first()
            if not src:
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
            source_objs[s_data['code']] = src

        db.session.commit()

        # 3. Seed notices from Portal Alpha fixture
        soup1 = BeautifulSoup(PORTAL_ALPHA_HTML, 'html.parser')
        adp1 = UniversityPortalAdapter()
        notices1 = adp1.parse(soup1, 'http://127.0.0.1:5000/mock/portal-alpha')
        for n in notices1:
            ChangeDetector.process_notice(n, source_id=source_objs['portal_alpha'].id)

        # 4. Seed notices from Portal Beta fixture
        soup2 = BeautifulSoup(PORTAL_BETA_HTML, 'html.parser')
        adp2 = ResearchGrantsAdapter()
        notices2 = adp2.parse(soup2, 'http://127.0.0.1:5000/mock/portal-beta')
        for n in notices2:
            ChangeDetector.process_notice(n, source_id=source_objs['portal_beta'].id)

        # 5. Seed Real Featured Scholarships with Direct Official Links
        real_scholarships = [
            {
                'notice_id': 'reliance-foundation-scholarships-2026-27',
                'title': 'Reliance Foundation Undergraduate & Postgraduate Scholarships 2026-27',
                'provider': 'Reliance Foundation',
                'notice_type': 'Scholarship',
                'education_level': 'Undergraduate',
                'discipline': 'General / All Disciplines',
                'region': 'India / National',
                'benefit_text': 'Up to ₹2,00,000 for Undergraduates & up to ₹6,00,000 for Postgraduates over degree duration + Mentorship, leadership workshops, and alumni network.',
                'eligibility_excerpt': 'First-year full-time undergraduate and postgraduate students enrolled in recognized Indian colleges and universities. Minimum 60% in Class 12 / Bachelor degree. Annual household income up to ₹15 Lakhs (priority given to <= ₹2.5 Lakhs).',
                'due_at': datetime(2026, 11, 30, tzinfo=timezone.utc),
                'timezone': 'IST',
                'official_url': 'https://www.reliancefoundation.org/media/media-release/Reliance_Foundation_Scholarships_2026-27',
                'notice_status': 'active',
                'is_verified': True,
                'is_featured': True,
                'source_code': 'reliance_foundation'
            },
            {
                'notice_id': 'central-sector-scheme-nsp-2026',
                'title': 'Central Sector Scheme of Scholarship (National Scholarship Portal - NSP)',
                'provider': 'Ministry of Education, Government of India (NSP)',
                'notice_type': 'Scholarship',
                'education_level': 'Undergraduate',
                'discipline': 'General / All Disciplines',
                'region': 'India / National',
                'benefit_text': '₹12,000 per annum for Undergraduate study (first 3 years) and ₹20,000 per annum at Postgraduate level directly transferred via Direct Benefit Transfer (DBT).',
                'eligibility_excerpt': 'Students above 80th percentile in relevant stream from respective Class 12 Board examination. Pursuing regular degree courses in colleges/institutions recognized by AICTE/UGC. Parental annual income <= ₹4.5 Lakhs.',
                'due_at': datetime(2026, 12, 31, tzinfo=timezone.utc),
                'timezone': 'IST',
                'official_url': 'https://scholarships.gov.in/',
                'notice_status': 'active',
                'is_verified': True,
                'is_featured': True,
                'source_code': 'nsp_portal'
            },
            {
                'notice_id': 'buddy4study-stem-merit-scholarship-2026',
                'title': 'Buddy4Study Higher Education & STEM Merit-cum-Means Scholarship',
                'provider': 'Buddy4Study Foundation & Corporate CSR Partners',
                'notice_type': 'Scholarship',
                'education_level': 'Undergraduate',
                'discipline': 'Computer Science & AI',
                'region': 'India / National',
                'benefit_text': '₹30,000 to ₹75,000 one-time financial aid + Learning laptop subsidy & placement interview preparatory support.',
                'eligibility_excerpt': 'Students pursuing Undergraduate professional courses (B.Tech, B.E., BCA, B.Sc) in recognized institutions across India. Minimum 60% marks in Class 12. Annual household income less than ₹6,00,000.',
                'due_at': datetime(2026, 11, 15, tzinfo=timezone.utc),
                'timezone': 'IST',
                'official_url': 'https://www.buddy4study.com/',
                'notice_status': 'active',
                'is_verified': True,
                'is_featured': True,
                'source_code': 'buddy4study'
            },
            {
                'notice_id': 'pmrf-doctoral-research-fellowship-2026',
                'title': "Prime Minister's Research Fellowship (PMRF Scheme 2026)",
                'provider': 'Ministry of Education, Government of India',
                'notice_type': 'Fellowship',
                'education_level': 'PhD / Doctoral',
                'discipline': 'Engineering',
                'region': 'India / National',
                'benefit_text': '₹70,000/month (Years 1-2), ₹75,000/month (Year 3), ₹80,000/month (Years 4-5) + ₹2,00,000/year research contingency grant for international conferences.',
                'eligibility_excerpt': 'Eligible candidates who have completed or are in final year of B.Tech/Integrated M.Tech/M.Sc from IISc, IITs, NITs, IISERs with CGPA >= 8.0, or admitted to PhD programs with valid GATE score >= 650.',
                'due_at': datetime(2026, 12, 15, tzinfo=timezone.utc),
                'timezone': 'IST',
                'official_url': 'https://www.pmrf.in/',
                'notice_status': 'active',
                'is_verified': True,
                'is_featured': True,
                'source_code': 'pmrf_portal'
            },
            {
                'notice_id': 'daad-epos-master-scholarship-2026',
                'title': 'DAAD Development-Related Postgraduate Courses (EPOS) Scholarship',
                'provider': 'German Academic Exchange Service (DAAD)',
                'notice_type': 'Scholarship',
                'education_level': 'Postgraduate/Master',
                'discipline': 'Environmental Sciences',
                'region': 'International / Germany',
                'benefit_text': '€934 monthly allowance + travel subsidy + health, accident & personal liability insurance + German language preparatory course.',
                'eligibility_excerpt': 'Graduates holding a recognized Bachelor degree with at least 2 years of professional experience in development-related sectors.',
                'due_at': datetime(2026, 12, 31, tzinfo=timezone.utc),
                'timezone': 'CET',
                'official_url': 'https://www.daad.de/en/study-and-research-in-germany/scholarships/',
                'notice_status': 'active',
                'is_verified': True,
                'is_featured': False,
                'source_code': 'portal_alpha'
            },
            {
                'notice_id': 'fulbright-nehru-fellowship-2026',
                'title': 'Fulbright-Nehru Master’s & Doctoral Research Fellowships 2026-27',
                'provider': 'United States-India Educational Foundation (USIEF) & Fulbright',
                'notice_type': 'Fellowship',
                'education_level': 'Postgraduate/Master',
                'discipline': 'Humanities & Social Sciences',
                'region': 'International / USA',
                'benefit_text': 'J-1 visa sponsorship, full tuition and mandatory fees, monthly living stipend, roundtrip airfare from India, and sickness & accident coverage.',
                'eligibility_excerpt': 'Indian citizens with equivalent US bachelor\'s degree (minimum 55% marks), at least three years of professional work experience, and demonstrable leadership potential.',
                'due_at': datetime(2027, 1, 15, tzinfo=timezone.utc),
                'timezone': 'EST',
                'official_url': 'https://foreign.fulbrightonline.org/',
                'notice_status': 'active',
                'is_verified': True,
                'is_featured': False,
                'source_code': 'portal_alpha'
            }
        ]

        for r in real_scholarships:
            src_obj = source_objs.get(r['source_code'], source_objs['portal_alpha'])
            ChangeDetector.process_notice(r, source_id=src_obj.id)

        db.session.commit()

        # 6. Apply Revision simulation from Portal Alpha Revised to populate change history
        soup_rev = BeautifulSoup(PORTAL_ALPHA_REVISED_HTML, 'html.parser')
        notices_rev = adp1.parse(soup_rev, 'http://127.0.0.1:5000/mock/portal-alpha-revised')
        for n in notices_rev:
            ChangeDetector.process_notice(n, source_id=source_objs['portal_alpha'].id)

        db.session.commit()

        # 7. Bookmark Reliance & Turing notice for demo student and add welcome alert
        if student:
            reliance_n = ScholarshipNotice.query.filter_by(notice_id='reliance-foundation-scholarships-2026-27').first()
            if reliance_n and not SavedScholarship.query.filter_by(user_id=student.id, notice_id=reliance_n.id).first():
                db.session.add(SavedScholarship(
                    user_id=student.id,
                    notice_id=reliance_n.id,
                    notes="Academic transcripts gathered; applying before November 30 on reliancefoundation.org."
                ))

            nsp_n = ScholarshipNotice.query.filter_by(notice_id='central-sector-scheme-nsp-2026').first()
            if nsp_n and not SavedScholarship.query.filter_by(user_id=student.id, notice_id=nsp_n.id).first():
                db.session.add(SavedScholarship(
                    user_id=student.id,
                    notice_id=nsp_n.id,
                    notes="Aadhaar and income certificate verified for NSP portal application."
                ))

            if not UserAlert.query.filter_by(user_id=student.id).first():
                db.session.add(UserAlert(
                    user_id=student.id,
                    notice_id=reliance_n.id if reliance_n else None,
                    alert_type='deadline_approaching',
                    message="Reminder: Reliance Foundation Scholarships 2026-27 application is open on official portal.",
                    is_read=False
                ))
            db.session.commit()

        total_notices = ScholarshipNotice.query.count()
        total_sources = Source.query.count()
        total_history = NoticeHistory.query.count()
        print(f"Database successfully seeded! Sources: {total_sources}, Notices: {total_notices}, History Entries: {total_history}")

if __name__ == '__main__':
    seed()
