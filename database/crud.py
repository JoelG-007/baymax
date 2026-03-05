from database.db_init import SessionLocal
from database.models import User, HealthEvent, Document, DocumentSummary, LoginAudit
from auth.security import hash_password
from datetime import datetime
import json


# -----------------------------
# USER FUNCTIONS
# -----------------------------

def register_user(username, email, password):
    db = SessionLocal()
    username = username.strip().lower()
    email = email.strip().lower()

    if db.query(User).filter(User.email == email).first():
        db.close()
        return "Email already registered"

    if db.query(User).filter(User.username == username).first():
        db.close()
        return "Username already taken"

    new_user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password)
    )
    db.add(new_user)
    db.commit()
    db.close()
    return "User created successfully"


def get_user_by_identifier(identifier):
    db = SessionLocal()
    identifier = identifier.strip().lower()
    user = db.query(User).filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()
    db.close()
    return user


def get_user_by_id(user_id):
    """Fetch a single user by their ID — used for mid-session suspension check."""
    db = SessionLocal()
    user = db.query(User).filter_by(id=user_id).first()
    db.close()
    return user


def update_user_password(user_id, new_hashed_password):
    db = SessionLocal()
    user = db.query(User).filter_by(id=user_id).first()
    if user:
        user.hashed_password = new_hashed_password
        db.commit()
    db.close()


def update_user_email(user_id, new_email):
    db = SessionLocal()

    # Check no other user has this email
    existing = db.query(User).filter(User.email == new_email).first()
    if existing and existing.id != user_id:
        db.close()
        return "Email already in use"

    user = db.query(User).filter_by(id=user_id).first()
    if user:
        user.email = new_email.strip().lower()
        db.commit()
    db.close()
    return "Email updated successfully"


def delete_user_account(user_id):
    db = SessionLocal()
    user = db.query(User).filter_by(id=user_id).first()
    if user:
        db.delete(user)
        db.commit()
    db.close()


# -----------------------------
# LOGIN AUDIT
# -----------------------------

def log_login_attempt(identifier, success):
    """Logs every login attempt — success or failure."""
    db = SessionLocal()
    db.add(LoginAudit(
        identifier=identifier.strip().lower(),
        success=1 if success else 0
    ))
    db.commit()
    db.close()


# -----------------------------
# HEALTH EVENTS
# -----------------------------

def save_health_event(user_id, record):
    db = SessionLocal()
    db.add(HealthEvent(
        user_id=user_id,
        symptom=record["symptom"],
        severity=record["severity"],
        body_region=record["body_region"]
    ))
    db.commit()
    db.close()


def get_health_events(user_id):
    """All events including resolved — for timeline and PDF history."""
    db = SessionLocal()
    events = db.query(HealthEvent).filter_by(user_id=user_id).all()
    db.close()
    return events


def get_active_health_events(user_id):
    """Only unresolved events — for risk scoring and analytics."""
    db = SessionLocal()
    events = db.query(HealthEvent).filter_by(user_id=user_id, is_resolved=0).all()
    db.close()
    return events


def resolve_health_event(event_id, user_id):
    db = SessionLocal()
    event = db.query(HealthEvent).filter_by(id=event_id, user_id=user_id).first()
    if event:
        event.is_resolved = 1
        event.resolved_at = datetime.utcnow()
        db.commit()
    db.close()


# -----------------------------
# DOCUMENTS
# -----------------------------

def save_document(user_id, filename):
    db = SessionLocal()
    doc = Document(
        user_id=user_id,
        file_path=filename,
        original_filename=filename
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    db.close()
    return doc.id


def get_documents_by_user(user_id):
    db = SessionLocal()
    docs = db.query(Document).filter_by(user_id=user_id).all()
    db.close()
    return docs


def save_document_summary(user_id, doc_id, structured):
    db = SessionLocal()
    db.add(DocumentSummary(
        user_id=user_id,
        document_id=doc_id,
        report_type=structured.get("report_type"),
        doctor_name=structured.get("doctor_name"),
        hospital_name=structured.get("hospital_name"),
        extracted_summary=structured.get("summary"),
        key_parameters_json=json.dumps(structured.get("parameters", {})),
        severity_flag=structured.get("risk"),
        report_date=datetime.utcnow()
    ))
    db.commit()
    db.close()


def get_document_summaries(user_id):
    db = SessionLocal()
    docs = db.query(DocumentSummary).filter_by(user_id=user_id).all()
    db.close()
    return docs