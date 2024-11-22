# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from app.database import SessionLocal
# from app.models import User
# from app.schemas import UserOut
# from app.utils import verify_password

# router = APIRouter(prefix="/users", tags=["users"])

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.get("/{user_id}", response_model=UserOut)
# def get_user(user_id: int, db: Session = Depends(get_db)):
#     """Fetch a user by ID."""
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found",
#         )
#     return user

# @router.get("/")
# def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     """Fetch a list of users with pagination."""
#     users = db.query(User).offset(skip).limit(limit).all()
#     return users

# @router.put("/{user_id}")
# def update_user(user_id: int, updated_data: UserOut, db: Session = Depends(get_db)):
#     """Update a user's details."""
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found",
#         )

#     user.username = updated_data.username
#     user.email = updated_data.email
#     db.commit()
#     db.refresh(user)
#     return user

# @router.delete("/{user_id}")
# def delete_user(user_id: int, db: Session = Depends(get_db)):
#     """Delete a user by ID."""
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found",
#         )

#     db.delete(user)
#     db.commit()
#     return {"message": "User deleted successfully"}

from fastapi import APIRouter, Depends

from ..auth.auth_handler import get_current_active_user
from ..schemas import UserResponse
from ..models import User

router = APIRouter()

@router.get("/users/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user