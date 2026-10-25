"""Comprehensive automated test suite for Phase 2 Multi-Tenant SaaS Architecture & RBAC.

Verifies:
1. Database schema initialization and enterprise tenant seeding (Acme Corp).
2. Tenant registration and conflict handling (slug/email collision detection).
3. Secure user authentication (bcrypt) and cryptographic JWT token issuance.
4. Token verification and protected endpoint gatekeeping (/api/auth/me).
5. Strict Role-Based Access Control (RBAC):
   - Admin vs Recruiter vs Hiring Manager permission enforcement.
   - Hiring manager restricted from job creation (403 Forbidden).
   - Non-admins restricted from team invitation/management (403 Forbidden).
6. Enterprise multi-tenant data isolation:
   - Zero data leakage between discrete tenant organizations.
"""

import uuid
import pytest
from app import app
from saas_auth import (
    init_saas_database,
    SessionLocal,
    Organization,
    User,
    JobPosting,
    decode_jwt_token,
    hash_password,
)


@pytest.fixture(scope="session", autouse=True)
def setup_saas_environment():
    """Ensure SaaS tables and default seed data are initialized."""
    init_saas_database()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_saas_default_seed():
    """Verify Acme Corp default enterprise tenant and role accounts are seeded."""
    session = SessionLocal()
    try:
        org = session.query(Organization).filter_by(slug="acme-corp").first()
        assert org is not None
        assert org.name == "Acme Corporation Enterprise"
        assert org.plan == "enterprise"

        admin = session.query(User).filter_by(email="admin@acmecorp.com").first()
        assert admin is not None
        assert admin.role == "admin"
        assert admin.verify_password("EnterpriseAdmin2026!") is True

        recruiter = session.query(User).filter_by(email="recruiter@acmecorp.com").first()
        assert recruiter is not None
        assert recruiter.role == "recruiter"

        hm = session.query(User).filter_by(email="hiring.manager@acmecorp.com").first()
        assert hm is not None
        assert hm.role == "hiring_manager"
    finally:
        session.close()


def test_auth_registration_and_validation(client):
    """Test tenant registration flow, input validation, and uniqueness constraints."""
    unique_suffix = str(uuid.uuid4())[:8]
    org_slug = f"tenant-{unique_suffix}"
    admin_email = f"lead@{org_slug}.io"

    # 1. Successful registration
    reg_payload = {
        "org_name": f"Tenant Org {unique_suffix}",
        "org_slug": org_slug,
        "email": admin_email,
        "password": "SecurePassword2026!",
        "full_name": "Chief Talent Officer"
    }
    resp = client.post("/api/auth/register", json=reg_payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert "access_token" in data
    assert data["user"]["email"] == admin_email
    assert data["user"]["role"] == "admin"
    assert data["organization"]["slug"] == org_slug

    # 2. Duplicate slug rejection (409)
    resp_dup = client.post("/api/auth/register", json=reg_payload)
    assert resp_dup.status_code == 409
    assert "already in use" in resp_dup.get_json()["error"]

    # 3. Missing fields rejection (400)
    resp_bad = client.post("/api/auth/register", json={"org_name": "Incomplete"})
    assert resp_bad.status_code == 400


def test_auth_login_and_jwt_verification(client):
    """Test login credentials verification and cryptographic JWT payload claims."""
    # 1. Valid login for seeded admin
    login_resp = client.post("/api/auth/login", json={
        "email": "admin@acmecorp.com",
        "password": "EnterpriseAdmin2026!"
    })
    assert login_resp.status_code == 200
    data = login_resp.get_json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"

    # Verify JWT claims
    claims = decode_jwt_token(data["access_token"])
    assert claims is not None
    assert claims["email"] == "admin@acmecorp.com"
    assert claims["role"] == "admin"
    assert "org_id" in claims
    assert "exp" in claims

    # 2. Invalid credentials (401)
    bad_resp = client.post("/api/auth/login", json={
        "email": "admin@acmecorp.com",
        "password": "WrongPassword!"
    })
    assert bad_resp.status_code == 401

    # 3. Non-existent user (401)
    ghost_resp = client.post("/api/auth/login", json={
        "email": "does.not.exist@company.org",
        "password": "SomePassword"
    })
    assert ghost_resp.status_code == 401


def test_protected_me_endpoint(client):
    """Test access control on /api/auth/me with Bearer token authentication."""
    # 1. No token -> 401 Unauthorized
    resp_anon = client.get("/api/auth/me")
    assert resp_anon.status_code == 401

    # 2. Invalid token -> 401 Unauthorized
    resp_invalid = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.payload"})
    assert resp_invalid.status_code == 401

    # 3. Valid token -> 200 OK
    login_resp = client.post("/api/auth/login", json={
        "email": "recruiter@acmecorp.com",
        "password": "RecruiterPass2026!"
    })
    token = login_resp.get_json()["access_token"]

    resp_auth = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp_auth.status_code == 200
    user_info = resp_auth.get_json()
    assert user_info["user"]["email"] == "recruiter@acmecorp.com"
    assert user_info["user"]["role"] == "recruiter"
    assert user_info["organization"]["slug"] == "acme-corp"


def test_rbac_team_management_and_invitation(client):
    """Verify that only Admin accounts can view team members and invite new users."""
    # Login Admin
    admin_token = client.post("/api/auth/login", json={
        "email": "admin@acmecorp.com",
        "password": "EnterpriseAdmin2026!"
    }).get_json()["access_token"]

    # Login Recruiter
    recruiter_token = client.post("/api/auth/login", json={
        "email": "recruiter@acmecorp.com",
        "password": "RecruiterPass2026!"
    }).get_json()["access_token"]

    # Login Hiring Manager
    hm_token = client.post("/api/auth/login", json={
        "email": "hiring.manager@acmecorp.com",
        "password": "HiringManager2026!"
    }).get_json()["access_token"]

    # 1. Admin views team -> 200 OK
    resp_admin = client.get("/api/org/team", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp_admin.status_code == 200
    team = resp_admin.get_json()["team"]
    assert len(team) >= 3

    # 2. Recruiter views team -> 403 Forbidden
    resp_recruiter = client.get("/api/org/team", headers={"Authorization": f"Bearer {recruiter_token}"})
    assert resp_recruiter.status_code == 403

    # 3. Hiring Manager views team -> 403 Forbidden
    resp_hm = client.get("/api/org/team", headers={"Authorization": f"Bearer {hm_token}"})
    assert resp_hm.status_code == 403

    # 4. Admin invites new team member -> 201 Created
    unique_email = f"junior.recruiter.{uuid.uuid4().hex[:6]}@acmecorp.com"
    invite_resp = client.post("/api/org/invite", json={
        "email": unique_email,
        "full_name": "Junior Recruiter Alex",
        "role": "recruiter",
        "password": "NewRecruiter2026!"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert invite_resp.status_code == 201

    # 5. Recruiter attempts to invite new team member -> 403 Forbidden
    unauth_invite = client.post("/api/org/invite", json={
        "email": "malicious@acmecorp.com",
        "full_name": "Malicious Attempter",
        "role": "admin"
    }, headers={"Authorization": f"Bearer {recruiter_token}"})
    assert unauth_invite.status_code == 403


def test_rbac_job_requisition_permissions(client):
    """Verify that Admins and Recruiters can post jobs, but Hiring Managers cannot."""
    admin_token = client.post("/api/auth/login", json={
        "email": "admin@acmecorp.com",
        "password": "EnterpriseAdmin2026!"
    }).get_json()["access_token"]

    recruiter_token = client.post("/api/auth/login", json={
        "email": "recruiter@acmecorp.com",
        "password": "RecruiterPass2026!"
    }).get_json()["access_token"]

    hm_token = client.post("/api/auth/login", json={
        "email": "hiring.manager@acmecorp.com",
        "password": "HiringManager2026!"
    }).get_json()["access_token"]

    # 1. Admin creates job -> 201
    resp_admin_job = client.post("/api/org/jobs", json={
        "title": "Principal AI Architect",
        "department": "Artificial Intelligence",
        "location": "San Francisco, CA / Remote",
        "target_seniority": "Staff / Principal",
        "job_description": "Architect end-to-end vector embeddings pipelines and multimodal LLM agents."
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp_admin_job.status_code == 201

    # 2. Recruiter creates job -> 201
    resp_recruiter_job = client.post("/api/org/jobs", json={
        "title": "Senior React Frontend Engineer",
        "department": "Frontend Engineering",
        "location": "Remote",
        "target_seniority": "Senior",
        "job_description": "Build high-performance interactive talent visualization dashboards."
    }, headers={"Authorization": f"Bearer {recruiter_token}"})
    assert resp_recruiter_job.status_code == 201

    # 3. Hiring Manager attempts job creation -> 403 Forbidden
    resp_hm_job = client.post("/api/org/jobs", json={
        "title": "Unauthorized Job Post",
        "job_description": "Should fail with forbidden."
    }, headers={"Authorization": f"Bearer {hm_token}"})
    assert resp_hm_job.status_code == 403
    assert "Forbidden" in resp_hm_job.get_json()["error"]


def test_multi_tenant_data_isolation(client):
    """Verify strict tenant isolation: Organization A cannot see jobs created by Organization B."""
    u1 = str(uuid.uuid4())[:6]
    u2 = str(uuid.uuid4())[:6]

    # Create Org Alpha
    resp_alpha = client.post("/api/auth/register", json={
        "org_name": f"Alpha Corp {u1}",
        "org_slug": f"alpha-{u1}",
        "email": f"admin@alpha-{u1}.com",
        "password": "AlphaPassword2026!",
        "full_name": "Alpha Admin"
    })
    token_alpha = resp_alpha.get_json()["access_token"]

    # Create Org Beta
    resp_beta = client.post("/api/auth/register", json={
        "org_name": f"Beta Solutions {u2}",
        "org_slug": f"beta-{u2}",
        "email": f"admin@beta-{u2}.com",
        "password": "BetaPassword2026!",
        "full_name": "Beta Admin"
    })
    token_beta = resp_beta.get_json()["access_token"]

    # Post unique job in Org Alpha
    client.post("/api/org/jobs", json={
        "title": f"ALPHA-CONFIDENTIAL-JOB-{u1}",
        "department": "Defense & Security",
        "location": "Washington, D.C.",
        "job_description": "Classified autonomous flight systems engineer."
    }, headers={"Authorization": f"Bearer {token_alpha}"})

    # Post unique job in Org Beta
    client.post("/api/org/jobs", json={
        "title": f"BETA-HEALTHCARE-JOB-{u2}",
        "department": "Biotech",
        "location": "Boston, MA",
        "job_description": "Computational genomics pipeline developer."
    }, headers={"Authorization": f"Bearer {token_beta}"})

    # Query Alpha's jobs with Alpha's token
    alpha_jobs_resp = client.get("/api/org/jobs", headers={"Authorization": f"Bearer {token_alpha}"})
    alpha_titles = [j["title"] for j in alpha_jobs_resp.get_json()["jobs"]]
    assert f"ALPHA-CONFIDENTIAL-JOB-{u1}" in alpha_titles
    assert f"BETA-HEALTHCARE-JOB-{u2}" not in alpha_titles

    # Query Beta's jobs with Beta's token
    beta_jobs_resp = client.get("/api/org/jobs", headers={"Authorization": f"Bearer {token_beta}"})
    beta_titles = [j["title"] for j in beta_jobs_resp.get_json()["jobs"]]
    assert f"BETA-HEALTHCARE-JOB-{u2}" in beta_titles
    assert f"ALPHA-CONFIDENTIAL-JOB-{u1}" not in beta_titles
