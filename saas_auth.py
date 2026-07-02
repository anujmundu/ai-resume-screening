"""Multi-Tenant SaaS Architecture & Role-Based Access Control (RBAC) Engine.

Provides enterprise data modeling with SQLAlchemy:
- Organization (Tenancy boundary)
- User (RBAC: super_admin, admin, recruiter, hiring_manager)
- JobPosting (Organization-scoped target jobs)
- CandidateApplication (Organization-scoped candidate pipeline)

Features:
- bcrypt password hashing
- Cryptographic JWT authentication & authorization
- Tenant isolation and role-gated access decorators

100% self-contained, SQLite/PostgreSQL compliant.
"""

from typing import Optional, List, Dict, Any, Callable
from functools import wraps
import os
import uuid
import datetime
import bcrypt
import jwt
from flask import request, jsonify, g
from sqlalchemy import (
    create_engine, Column, String, Integer, DateTime, Boolean, ForeignKey, Text, Enum
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session

DATABASE_URL = os.getenv("SAAS_DATABASE_URL", "sqlite:///saas_platform.db")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "talent-ai-enterprise-jwt-secret-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def get_utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


class Organization(Base):
    """Represents a discrete enterprise tenant with strict data isolation."""
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(120), nullable=False)
    slug = Column(String(80), unique=True, nullable=False, index=True)
    plan = Column(String(50), default="enterprise")  # starter, growth, enterprise
    max_active_jobs = Column(Integer, default=50)
    created_at = Column(DateTime, default=get_utc_now)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    jobs = relationship("JobPosting", back_populates="organization", cascade="all, delete-orphan")
    applications = relationship("CandidateApplication", back_populates="organization", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "plan": self.plan,
            "max_active_jobs": self.max_active_jobs,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class User(Base):
    """User account within an Organization with strictly assigned RBAC permissions."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(180), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(String(50), default="recruiter")  # super_admin, admin, recruiter, hiring_manager
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)

    organization = relationship("Organization", back_populates="users")

    def verify_password(self, password: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "org_id": self.org_id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class JobPosting(Base):
    """Target job requisition scoped to a single tenant organization."""
    __tablename__ = "job_postings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    department = Column(String(100), default="Engineering")
    location = Column(String(100), default="Remote")
    job_description = Column(Text, nullable=False)
    target_seniority = Column(String(50), default="Senior")
    status = Column(String(30), default="open")  # open, closed, draft
    created_at = Column(DateTime, default=get_utc_now)

    organization = relationship("Organization", back_populates="jobs")
    applications = relationship("CandidateApplication", back_populates="job", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "org_id": self.org_id,
            "title": self.title,
            "department": self.department,
            "location": self.location,
            "target_seniority": self.target_seniority,
            "status": self.status,
            "job_description_snippet": self.job_description[:200] + "...",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class CandidateApplication(Base):
    """Association tracking a candidate screened for an organization's job."""
    __tablename__ = "candidate_applications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("job_postings.id", ondelete="SET NULL"), nullable=True, index=True)
    candidate_id = Column(String(80), nullable=False, index=True)  # References resume storage ID
    candidate_name = Column(String(120), nullable=False)
    score = Column(Integer, default=0)
    decision = Column(String(30), default="review")
    stage = Column(String(30), default="screened")
    created_at = Column(DateTime, default=get_utc_now)

    organization = relationship("Organization", back_populates="applications")
    job = relationship("JobPosting", back_populates="applications")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "org_id": self.org_id,
            "job_id": self.job_id,
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "score": self.score,
            "decision": self.decision,
            "stage": self.stage,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


def hash_password(password: str) -> str:
    """Generate bcrypt password hash."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def generate_jwt_token(user: User) -> str:
    """Issue a cryptographically signed JWT authorization token with 24h expiration."""
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": user.id,
        "org_id": user.org_id,
        "email": user.email,
        "role": user.role,
        "name": user.full_name,
        "exp": exp,
        "iat": datetime.datetime.now(datetime.timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and cryptographically verify JWT token signature."""
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def init_saas_database():
    """Create all schema tables and seed default enterprise tenant if non-existent."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        # Check if default org exists
        default_org = session.query(Organization).filter_by(slug="acme-corp").first()
        if not default_org:
            default_org = Organization(
                name="Acme Corporation Enterprise",
                slug="acme-corp",
                plan="enterprise",
                max_active_jobs=100
            )
            session.add(default_org)
            session.commit()
            session.refresh(default_org)

            # Seed Admin User
            admin_user = User(
                org_id=default_org.id,
                email="admin@acmecorp.com",
                password_hash=hash_password("EnterpriseAdmin2026!"),
                full_name="Alex Mercer (VP Talent)",
                role="admin"
            )
            recruiter_user = User(
                org_id=default_org.id,
                email="recruiter@acmecorp.com",
                password_hash=hash_password("RecruiterPass2026!"),
                full_name="Sarah Jenkins (Senior Technical Recruiter)",
                role="recruiter"
            )
            hiring_mgr = User(
                org_id=default_org.id,
                email="hiring.manager@acmecorp.com",
                password_hash=hash_password("HiringManager2026!"),
                full_name="David Chen (Director of Cloud Infrastructure)",
                role="hiring_manager"
            )
            session.add_all([admin_user, recruiter_user, hiring_mgr])
            session.commit()

            # Seed Default Job Postings
            sample_job = JobPosting(
                org_id=default_org.id,
                title="Lead Cloud Data Platform Engineer",
                department="Data & Machine Learning",
                location="Remote (Global)",
                target_seniority="Senior / Lead",
                status="open",
                job_description="Seeking a Lead Cloud Data Platform Engineer with deep expertise in Python, Apache Spark, Kafka, Airflow, and Cloud Storage to scale analytics pipelines."
            )
            session.add(sample_job)
            session.commit()
    finally:
        session.close()


# ---------------- RBAC Security Decorators ----------------

def require_auth(f: Callable) -> Callable:
    """Ensure incoming request carries a valid Bearer JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        elif request.cookies.get("access_token"):
            token = request.cookies.get("access_token")

        if not token:
            return jsonify({"error": "Unauthorized: Missing authentication token"}), 401

        payload = decode_jwt_token(token)
        if not payload:
            return jsonify({"error": "Unauthorized: Invalid or expired token"}), 401

        g.current_user = payload
        return f(*args, **kwargs)
    return decorated


def require_roles(allowed_roles: List[str]) -> Callable:
    """Enforce strict Role-Based Access Control on endpoint."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            token = None
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
            elif request.cookies.get("access_token"):
                token = request.cookies.get("access_token")

            if not token:
                return jsonify({"error": "Unauthorized: Missing authentication token"}), 401

            payload = decode_jwt_token(token)
            if not payload:
                return jsonify({"error": "Unauthorized: Invalid or expired token"}), 401

            user_role = payload.get("role", "recruiter")
            if user_role not in allowed_roles and user_role != "super_admin":
                return jsonify({
                    "error": "Forbidden: Insufficient privileges",
                    "user_role": user_role,
                    "required_roles": allowed_roles
                }), 403

            g.current_user = payload
            return f(*args, **kwargs)
        return decorated
    return decorator
