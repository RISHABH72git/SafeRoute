from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request

from models.global_model import User, ApiKey
from models.req_res_model import UserCreate, LoginRequest
from utils.common import hash_password, generate_random_ids
from utils.db import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", )
def get_apikey_info(request: Request, db: Session = Depends(get_db)):
    api_key_header = request.headers.get("X-API-Key")
    if not api_key_header:
        raise HTTPException(status_code=400, detail="Missing API key in headers")

    api_key = db.query(ApiKey).filter(ApiKey.apikey == api_key_header).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="Invalid API key")

    user = db.query(User).filter(User.id == api_key.user_id).first()
    return {"message": "you are authorized", "user_id": user.id, "email": user.email, "name": user.name}


# CREATE a user
@router.post("/add")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(name=user.name, email=user.email, password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    new_api_key = ApiKey(apikey=generate_random_ids(), user_id=new_user.id)
    db.add(new_api_key)
    db.commit()
    return {"message": "User created successfully",
            "data": {"id": new_user.id, "name": new_user.name, "email": new_user.email}}


# READ all users
@router.post("/login")
def get_users(login: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == login.email).first()
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    if db_user.password != hash_password(login.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    return {"message": "User logged in",
            "data": {"id": db_user.id, "name": db_user.name, "email": db_user.email, "apikeys": db_user.apikeys}}

