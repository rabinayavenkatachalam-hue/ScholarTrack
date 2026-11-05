"""
Mock Portals for ScholarTrack Demonstration & Mentor Challenge Evaluation.
Provides compliant HTML test fixtures representing:
1. University Scholarship Portal Layout (Alpha)
2. International Research Fellowship Table Layout (Beta)
3. Revised Deadlines Layout (Alpha Revised) - Proves Revision Tracking & Alert Triggering
4. Edge Case Test: Unknown/Rolling Deadlines (Never arbitrary date)
5. Edge Case Test: Malformed HTML & Missing Fields
6. Edge Case Test: Inaccessible 403 Forbidden Source
"""
from flask import Blueprint, render_template_string, Response

mock_bp = Blueprint('mock', __name__, url_prefix='/mock')

PORTAL_ALPHA_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Global University Scholarship Portal - Approved Source #1</title>
    <style>
        body { font-family: sans-serif; background: #f4f6f9; padding: 20px; }
        .scholarship-card { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .card-title { font-size: 1.4rem; color: #1e3a8a; margin-top: 0; }
        .provider-name { font-weight: bold; color: #4b5563; }
        .meta-tag { display: inline-block; background: #e0e7ff; color: #3730a3; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem; margin-right: 5px; }
        .deadline { font-weight: bold; color: #dc2626; }
    </style>
</head>
<body>
    <h1>Official University Scholarship & Fellowship Notices (Portal Alpha)</h1>
    <p>Last verified by Academic Board. Public notice feed for eligible international students.</p>

    <!-- Notice 1 -->
    <div class="scholarship-card" data-layout="university-portal">
        <h2 class="card-title">Turing Postgraduate Fellowship in Artificial Intelligence</h2>
        <div class="provider-name">Alan Turing Institute & Cambridge Academic Trust</div>
        <p>
            <span class="meta-tag education-level">Postgraduate/Master</span>
            <span class="meta-tag discipline">Computer Science & AI</span>
            <span class="meta-tag timezone">UTC</span>
        </p>
        <p class="benefit">Full Tuition Waiver + £24,000 Annual Living Stipend + Cloud Compute Credits</p>
        <p class="eligibility">First-class honours degree or equivalent in Computing, Mathematics or relevant quantitative discipline.</p>
        <p>Application Deadline: <span class="deadline">2026-11-30</span> (<span class="timezone">UTC</span>)</p>
        <a class="official-link" href="https://www.turing.ac.uk/">Official Announcement & Syllabus</a>
    </div>

    <!-- Notice 2 -->
    <div class="scholarship-card" data-layout="university-portal">
        <h2 class="card-title">Marie Curie Clean Energy & Climate Transition Grant</h2>
        <div class="provider-name">European Research Council & Horizon Europe</div>
        <p>
            <span class="meta-tag education-level">PhD / Doctoral</span>
            <span class="meta-tag discipline">Environmental Sciences</span>
            <span class="meta-tag timezone">CET</span>
        </p>
        <p class="benefit">€38,500 / year Research Fellowship + €6,000 Laboratory Bench Fees</p>
        <p class="eligibility">Open to transnational doctoral candidates researching renewable energy, carbon capture, or green hydrogen.</p>
        <p>Application Deadline: <span class="deadline">2026-12-15</span> (<span class="timezone">CET</span>)</p>
        <a class="official-link" href="https://marie-sklowdowska-curie-actions.ec.europa.eu/">Official Announcement & Syllabus</a>
    </div>

    <!-- Notice 3 -->
    <div class="scholarship-card" data-layout="university-portal">
        <h2 class="card-title">Ada Lovelace Women in Quantum Computing Scholarship</h2>
        <div class="provider-name">Oxford Quantum Computing Lab</div>
        <p>
            <span class="meta-tag education-level">Undergraduate</span>
            <span class="meta-tag discipline">Computer Science & AI</span>
            <span class="meta-tag timezone">GMT</span>
        </p>
        <p class="benefit">£15,000 Merit Award + Mentorship with Senior Quantum Engineers</p>
        <p class="eligibility">Women and non-binary students entering their penultimate or final year in Physics or Computer Science.</p>
        <p>Application Deadline: <span class="deadline">2026-10-31</span> (<span class="timezone">GMT</span>)</p>
        <a class="official-link" href="https://www.ox.ac.uk/admissions/graduate/fees-and-funding/graduate-scholarships">Official Announcement & Syllabus</a>
    </div>

    <!-- Notice 4: Unknown / Rolling Deadline Test (CyberNaut Mentor Checkpoint) -->
    <div class="scholarship-card" data-layout="university-portal">
        <h2 class="card-title">Global Health & Tropical Disease Innovation Grant</h2>
        <div class="provider-name">World Health Studies Institute</div>
        <p>
            <span class="meta-tag education-level">Postdoctoral</span>
            <span class="meta-tag discipline">Health & Medicine</span>
            <span class="meta-tag timezone">UTC</span>
        </p>
        <p class="benefit">$60,000 Seed Grant for Field Trials + Open Access Publication Subsidy</p>
        <p class="eligibility">Postdoctoral researchers with ongoing projects targeting neglected tropical diseases.</p>
        <p>Application Deadline: <span class="deadline">Unknown / Rolling</span> (<span class="timezone">UTC</span>)</p>
        <a class="official-link" href="https://www.who.int/careers/internship-programme">Official Announcement & Syllabus</a>
    </div>
</body>
</html>
"""

PORTAL_ALPHA_REVISED_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Global University Scholarship Portal - REVISED NOTICE FEED</title>
</head>
<body>
    <h1>Official University Scholarship & Fellowship Notices (Portal Alpha - REVISION SIMULATOR)</h1>
    <p>Notice: Deadlines updated by Academic Committee on October 2026.</p>

    <!-- Notice 1: Deadline Extended by 15 days -->
    <div class="scholarship-card" data-layout="university-portal">
        <h2 class="card-title">Turing Postgraduate Fellowship in Artificial Intelligence</h2>
        <div class="provider-name">Alan Turing Institute & Cambridge Academic Trust</div>
        <p>
            <span class="meta-tag education-level">Postgraduate/Master</span>
            <span class="meta-tag discipline">Computer Science & AI</span>
            <span class="meta-tag timezone">UTC</span>
        </p>
        <p class="benefit">Full Tuition Waiver + £24,000 Annual Living Stipend + Cloud Compute Credits</p>
        <p class="eligibility">First-class honours degree or equivalent in Computing, Mathematics or relevant quantitative discipline.</p>
        <!-- REVISED FROM 2026-11-30 TO 2026-12-15 -->
        <p>Application Deadline: <span class="deadline">2026-12-15</span> (<span class="timezone">UTC</span>)</p>
        <a class="official-link" href="https://www.turing.ac.uk/">Official Announcement & Syllabus</a>
    </div>

    <!-- Notice 2: Deadline Extended -->
    <div class="scholarship-card" data-layout="university-portal">
        <h2 class="card-title">Marie Curie Clean Energy & Climate Transition Grant</h2>
        <div class="provider-name">European Research Council & Horizon Europe</div>
        <p>
            <span class="meta-tag education-level">PhD / Doctoral</span>
            <span class="meta-tag discipline">Environmental Sciences</span>
            <span class="meta-tag timezone">CET</span>
        </p>
        <p class="benefit">€38,500 / year Research Fellowship + €6,000 Laboratory Bench Fees</p>
        <p class="eligibility">Open to transnational doctoral candidates researching renewable energy, carbon capture, or green hydrogen.</p>
        <!-- REVISED FROM 2026-12-15 TO 2027-01-10 -->
        <p>Application Deadline: <span class="deadline">2027-01-10</span> (<span class="timezone">CET</span>)</p>
        <a class="official-link" href="https://marie-sklowdowska-curie-actions.ec.europa.eu/">Official Announcement & Syllabus</a>
    </div>

    <!-- Notice 3: Unchanged -->
    <div class="scholarship-card" data-layout="university-portal">
        <h2 class="card-title">Ada Lovelace Women in Quantum Computing Scholarship</h2>
        <div class="provider-name">Oxford Quantum Computing Lab</div>
        <p>
            <span class="meta-tag education-level">Undergraduate</span>
            <span class="meta-tag discipline">Computer Science & AI</span>
            <span class="meta-tag timezone">GMT</span>
        </p>
        <p class="benefit">£15,000 Merit Award + Mentorship with Senior Quantum Engineers</p>
        <p class="eligibility">Women and non-binary students entering their penultimate or final year in Physics or Computer Science.</p>
        <p>Application Deadline: <span class="deadline">2026-10-31</span> (<span class="timezone">GMT</span>)</p>
        <a class="official-link" href="https://www.ox.ac.uk/admissions/graduate/fees-and-funding/graduate-scholarships">Official Announcement & Syllabus</a>
    </div>
</body>
</html>
"""

PORTAL_BETA_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>International Research Grants Board - Approved Source #2</title>
</head>
<body>
    <h1>International STEM & Fellowship Grants Board (Portal Beta - Table Layout)</h1>
    <table class="grants-table" border="1" cellpadding="8" data-layout="fellowship-portal">
        <thead>
            <tr>
                <th>Title</th>
                <th>Sponsor / Grantor</th>
                <th>Level</th>
                <th>Discipline</th>
                <th>Benefit / Funding</th>
                <th>Eligibility Summary</th>
                <th>Deadline</th>
                <th>Timezone</th>
                <th>Link</th>
            </tr>
        </thead>
        <tbody>
            <tr class="fellowship-row">
                <td class="title">Next-Gen Autonomous Robotics Research Fellowship</td>
                <td class="sponsor">DARPA & Robotics Innovation Alliance</td>
                <td class="level">Postdoctoral</td>
                <td class="discipline">Engineering</td>
                <td class="benefit">$75,000 / year + Hardware Lab Stipend</td>
                <td class="eligibility">PhD in Robotics, Mechatronics, or Autonomous Control Systems.</td>
                <td class="deadline">2026-12-01</td>
                <td class="timezone">EST</td>
                <td><a href="https://www.darpa.mil/">View Official Notice</a></td>
            </tr>
            <tr class="fellowship-row">
                <td class="title">Genomics & CRISPR Precision Therapeutics Grant</td>
                <td class="sponsor">Broad Institute & BioMed Consortium</td>
                <td class="level">PhD / Doctoral</td>
                <td class="discipline">Health & Medicine</td>
                <td class="benefit">$52,000 / year + Full Medical Coverage</td>
                <td class="eligibility">Candidates with accepted doctoral proposals in cellular genome editing.</td>
                <td class="deadline">2027-01-15</td>
                <td class="timezone">EST</td>
                <td><a href="https://www.broadinstitute.org/">View Official Notice</a></td>
            </tr>
            <tr class="fellowship-row">
                <td class="title">Digital Humanities & Ethical AI Dissertation Fellowship</td>
                <td class="sponsor">Mellon Foundation</td>
                <td class="level">Postgraduate/Master</td>
                <td class="discipline">Humanities & Social Sciences</td>
                <td class="benefit">$35,000 Fellowship + Archival Travel Grant</td>
                <td class="eligibility">Master's or terminal dissertation students researching the ethical impact of AI on culture.</td>
                <td class="deadline">2026-11-15</td>
                <td class="timezone">PST</td>
                <td><a href="https://www.mellon.org/">View Official Notice</a></td>
            </tr>
            <tr class="fellowship-row">
                <td class="title">Space Science & Satellite Remote Sensing Bursary</td>
                <td class="sponsor">Aerospace Exploration Council</td>
                <td class="level">Undergraduate</td>
                <td class="discipline">Engineering</td>
                <td class="benefit">$18,000 Tuition Credit + Summer Flight Centre Internship</td>
                <td class="eligibility">Undergraduate students in Aerospace, Applied Physics or Geospatial Sciences.</td>
                <td class="deadline">2027-02-28</td>
                <td class="timezone">PST</td>
                <td><a href="https://www.nasa.gov/learning-resources/internship-programs/">View Official Notice</a></td>
            </tr>
        </tbody>
    </table>
</body>
</html>
"""

PORTAL_MALFORMED_HTML = """
<html><body>
<h1>Malformed Portal Test Fixture</h1>
<div class="scholarship-card" data-layout="university-portal">
    <h2 class="card-title">Incomplete Scholarship Notice</h2>
    <!-- Intentionally missing provider, level, and due date -->
    <p class="benefit">$5,000 Emergency Grant</p>
    <a href="/apply">Apply</a>
</div>
</body></html>
"""

@mock_bp.route('/portal-alpha')
def portal_alpha():
    return render_template_string(PORTAL_ALPHA_HTML)

@mock_bp.route('/portal-alpha-revised')
def portal_alpha_revised():
    return render_template_string(PORTAL_ALPHA_REVISED_HTML)

@mock_bp.route('/portal-beta')
def portal_beta():
    return render_template_string(PORTAL_BETA_HTML)

@mock_bp.route('/portal-malformed')
def portal_malformed():
    return render_template_string(PORTAL_MALFORMED_HTML)

@mock_bp.route('/portal-forbidden')
def portal_forbidden():
    return Response("<h1>403 Forbidden: Crawling Blocked by Site Administrator</h1>", status=403, mimetype='text/html')
