from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.services.auth_service import AuthService


def bootstrap_application() -> None:
    db: Session = SessionLocal()
    try:
        AuthService(db).bootstrap_demo_admin()
    finally:
        db.close()