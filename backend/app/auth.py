"""Password hashing, JWT issuing/verification, and FastAPI auth dependencies.

Lab-only authentication: local email+password login issuing a short-lived
JWT. NOT production-grade SSO. See docs/SECURITY.md. The architecture keeps
this module isolated so a future OIDC/SSO integration can replace
`create_access_token`/`get_current_user` without touching business routers.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

# Lab-only secret. Must be overridden via env var for any non-local use.
JWT_SECRET = os.getenv("JWT_SECRET", "sound-x-post-lab-secret-not-for-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8

bearer_scheme = HTTPBearer(auto_error=False)

# Roles that may manage users, project rosters, and global configuration.
ADMIN_ROLES = {"ADMIN"}
# Roles that coordinate a project's day-to-day operation.
MANAGEMENT_ROLES = {"ADMIN", "SUPERVISOR", "COORDINATOR"}
# All roles that can operate on project content (everyone except VIEWER).
OPERATIONAL_ROLES = {"ADMIN", "SUPERVISOR", "COORDINATOR", "EDITOR", "MIXER", "QC", "ARCHIVE"}
ALL_ROLES = OPERATIONAL_ROLES | {"VIEWER"}


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o caducado")
    user = db.get(models.User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inactivo o inexistente")
    return user


def require_roles(*roles: str):
    allowed = set(roles)

    def dependency(current_user: models.User = Depends(get_current_user)) -> models.User:
        if current_user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para esta acción")
        return current_user

    return dependency


def ensure_project_access(db: Session, user: models.User, project_id: int) -> None:
    """Raise 403 unless the user is ADMIN or an active member of the project."""
    if user.role in ADMIN_ROLES:
        return
    membership = (
        db.query(models.ProjectMembership)
        .filter(models.ProjectMembership.project_id == project_id, models.ProjectMembership.user_id == user.id)
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No perteneces a este proyecto")
