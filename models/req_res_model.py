from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str


class LoginRequest(BaseModel):
    email: str
    password: str

class ProxyCreate(BaseModel):
    host: str
    paths: list
