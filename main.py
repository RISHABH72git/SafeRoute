from contextlib import asynccontextmanager
from fastapi import FastAPI
from models import global_model
from config.mysql_database import engine
from routes.account import router as account_router
from routes.proxy import router as proxy_router

app = FastAPI()
from fastapi import FastAPI, Request


# @app.middleware("http")
# async def firewall_middleware(request: Request, call_next):
    # IP Firewall
    # client_ip = request.client.host
    # if client_ip not in ALLOWED_IPS:
    #     raise HTTPException(status_code=403, detail=f"Access denied for IP: {client_ip}")
    #
    # # API Key Check
    # api_key = request.headers.get("X-API-Key")
    # if api_key not in VALID_API_KEYS:
    #     raise HTTPException(status_code=401, detail="Invalid or missing API key")
    # return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")
    # Create tables
    global_model.Base.metadata.create_all(bind=engine)
    yield  # control passes to FastAPI app
    print("Shutting down application...")


# Create app with lifespan
app = FastAPI(lifespan=lifespan)
app.include_router(proxy_router)
app.include_router(account_router)
