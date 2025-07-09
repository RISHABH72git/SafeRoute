from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request

from models.global_model import User, ApiKey, ProxyPath, Proxy
from models.req_res_model import UserCreate, LoginRequest, ProxyCreate
from utils.common import hash_password, generate_random_ids, get_api_key
from utils.db import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", )
def get_apikey_info(request: Request, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    api_key = db.query(ApiKey).filter(ApiKey.apikey == api_key).first()
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


@router.post("/proxy/add")
def add_proxy(proxy: ProxyCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    apikey = db.query(ApiKey).filter(ApiKey.apikey == api_key).first()
    proxy_data = db.query(Proxy).filter(Proxy.host == proxy.host, Proxy.user_id == apikey.user_id).first()
    if proxy_data:
        raise HTTPException(status_code=409, detail="Proxy already registered")
    new_proxy = Proxy(host=proxy.host, user_id=apikey.user_id)
    db.add(new_proxy)
    db.commit()
    db.refresh(new_proxy)
    for path in proxy.paths:
        proxy_path = ProxyPath(path=path, proxy_id=new_proxy.id)
        db.add(proxy_path)
        db.commit()
        db.refresh(proxy_path)
    return {"message": "Proxy added successfully",
            "data": {"id": new_proxy.id, "host": new_proxy.host, "paths": new_proxy.paths}}


@router.get("/proxy")
def add_proxy(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    apikey = db.query(ApiKey).filter(ApiKey.apikey == api_key).first()
    proxy_data = db.query(Proxy).filter(Proxy.user_id == apikey.user_id).all()
    if not proxy_data:
        raise HTTPException(status_code=404, detail="Proxies not Found")
    proxies_data = []
    for proxy in proxy_data:
        proxies_data.append({
            "id": proxy.id,
            "host": proxy.host,
            "paths": proxy.paths
        })
    return {"message": "Proxy list", "data": proxies_data}
