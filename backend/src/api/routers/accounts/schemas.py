from pydantic import BaseModel, Field, EmailStr

from src.api.validators.username import Username


class RegisterSchema(BaseModel):
    username: Username
    email: EmailStr
    password: str = Field(min_length=8)


class RegisterResponse(BaseModel):
    user_id: int = -1
    message: str


class LoginSchema(BaseModel):
    login: EmailStr | Username
    password: str


class LoginResponse(BaseModel):
    token: str


class LogoutResponse(BaseModel):
    message: str


class VerifyResponse(BaseModel):
    message: str


class ActivateResponse(BaseModel):
    user_id: int
    message: str
