# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from app.database import SessionLocal
# from app.schemas import UserCreate
# from app.models import User
# from app.utils import hash_password, create_access_token

# router = APIRouter(prefix="/auth", tags=["auth"])

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.post("/register")
# def register(user: UserCreate, db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.email == user.email).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     hashed_pw = hash_password(user.password)
#     new_user = User(username=user.username, email=user.email, hashed_password=hashed_pw)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user

# @router.post("/login")
# def login(email: str, password: str, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == email).first()
#     if not user or not verify_password(password, user.hashed_password):
#         raise HTTPException(status_code=400, detail="Invalid credentials")
    
#     token = create_access_token({"sub": user.email})
#     return {"access_token": token, "token_type": "bearer"}

from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session


from ..auth.auth_handler import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_user, get_password_hash
from ..database import get_db
from ..schemas import Token, UserCreate, UserResponse
from ..models import User

router = APIRouter()



@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered.")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    response = JSONResponse(
        content={"message": "Registration successful"},
        status_code=201
    )
    response.headers["HX-Redirect"] = "/"
    return response
    # return db_user


@router.post("/token")
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")