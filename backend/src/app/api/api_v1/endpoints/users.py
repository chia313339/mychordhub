"""
User management endpoints.
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api.deps import get_current_active_user, get_current_admin_user, get_db
from app.services.user import user_service

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_admin_user),
) -> Any:
    """
    Retrieve users. (Admin only)
    """
    users = user_service.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(get_current_admin_user),
) -> Any:
    """
    Create new user. (Admin only)
    """
    user = user_service.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = user_service.create(db, obj_in=user_in)
    return user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    password: str = None,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = user_in.dict(exclude_unset=True)
    if password is not None:
        current_user_data["password"] = password
    current_user = user_service.update(db, db_obj=current_user, obj_in=current_user_data)
    return current_user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = user_service.get(db, id=user_id)
    if user == current_user:
        return user
    if not user_service.is_admin(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_admin_user),
) -> Any:
    """
    Update a user. (Admin only)
    """
    user = user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user = user_service.update(db, db_obj=user, obj_in=user_in)
    return user