from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[schemas.UserOut])
def list_users(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return db.query(models.User).order_by(models.User.name).all()


@router.post("", response_model=schemas.UserOut, status_code=201)
def create_user(
    payload: schemas.UserCreate,
    current_user: models.User = Depends(auth.require_roles(*auth.ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Ya existe un usuario con ese email")
    user = models.User(
        name=payload.name,
        email=payload.email,
        role=payload.role,
        department=payload.department,
        hashed_password=auth.hash_password(payload.password),
        is_active=True,
        is_demo=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    current_user: models.User = Depends(auth.require_roles(*auth.ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    updates = payload.model_dump(exclude_unset=True, exclude={"password"})
    for field, value in updates.items():
        setattr(user, field, value)
    if payload.password:
        user.hashed_password = auth.hash_password(payload.password)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}/projects", response_model=list[schemas.ProjectOut])
def user_projects(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    memberships = db.query(models.ProjectMembership).filter(models.ProjectMembership.user_id == user_id).all()
    return [m.project for m in memberships]
