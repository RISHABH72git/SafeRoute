from contextlib import asynccontextmanager
from fastapi import FastAPI

from middlewares.rate_limiter import RateLimiterMiddleware
from models import global_model
from config.mysql_database import engine
from routes.account import router as account_router
from routes.proxy import router as proxy_router

app = FastAPI()
from fastapi import FastAPI, Request


@app.middleware("http")
async def firewall_middleware(request: Request, call_next):
    return await call_next(request)


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
app.add_middleware(RateLimiterMiddleware)
