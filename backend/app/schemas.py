# from pydantic import BaseModel, EmailStr

# class UserBase(BaseModel):
#     username: str
#     email: EmailStr

# class UserCreate(UserBase):
#     password: str

# class UserOut(UserBase):
#     id: int

#     class Config:
#         orm_mode = True

# schemas.py
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str | None = None

class UserInDB(UserResponse):
    hashed_password: str