from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db_init import Base


# -----------------------------
# USER MODEL
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", index=True)
    is_active = Column(Integer, default=1, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    health_events = relationship(
        "HealthEvent", back_populates="user", cascade="all, delete-orphan"
    )
    documents = relationship(
        "Document", back_populates="user", cascade="all, delete-orphan"
    )
    summaries = relationship(
        "DocumentSummary", back_populates="user", cascade="all, delete-orphan"
    )


# -----------------------------
# HEALTH EVENTS
# -----------------------------
class HealthEvent(Base):
    __tablename__ = "health_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    symptom = Column(String)
    severity = Column(String)
    body_region = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # --- Resolved tracking ---
    is_resolved = Column(Integer, default=0)       # 0 = active, 1 = resolved
    resolved_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="health_events")


# -----------------------------
# DOCUMENT STORAGE
# -----------------------------
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    file_path = Column(String)
    original_filename = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="documents")
    summaries = relationship(
        "DocumentSummary", back_populates="document", cascade="all, delete-orphan"
    )


# -----------------------------
# DOCUMENT SUMMARIES
# -----------------------------
class DocumentSummary(Base):
    __tablename__ = "document_summaries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), index=True)

    report_type = Column(String)
    doctor_name = Column(String)
    hospital_name = Column(String)

    extracted_summary = Column(Text)
    key_parameters_json = Column(Text)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    severity_flag = Column(String, index=True)
    report_date = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="summaries")
    document = relationship("Document", back_populates="summaries")


# -----------------------------
# ROLE AUDIT
# -----------------------------
class RoleAudit(Base):
    __tablename__ = "role_audit"

    id = Column(Integer, primary_key=True)
    changed_user_id = Column(Integer)
    changed_by = Column(Integer)
    new_role = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


# -----------------------------
# ADMIN DATA AUDIT
# -----------------------------
class AdminAudit(Base):
    __tablename__ = "admin_audit"

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer)
    target_table = Column(String)
    target_id = Column(Integer)
    field_changed = Column(String)
    old_value = Column(String)
    new_value = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# -----------------------------
# LOGIN AUDIT
# -----------------------------
class LoginAudit(Base):
    __tablename__ = "login_audit"

    id = Column(Integer, primary_key=True)
    identifier = Column(String)
    success = Column(Integer)       # 1 = success, 0 = failure
    timestamp = Column(DateTime, default=datetime.utcnow)