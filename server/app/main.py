from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.api.routes import auth, devices, settings, updates, users
from app.core.config import get_settings
from app.database.mongo import close_mongo_connection, get_collection, verify_mongo_connection

load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    settings.validate_runtime_configuration()
    verify_mongo_connection()
    get_collection("users").create_index("username", unique=True)
    get_collection("users").create_index("email", unique=True)
    get_collection("settings").create_index("user_id", unique=True)
    get_collection("sessions").create_index("expires_at", expireAfterSeconds=0)
    get_collection("pairing_codes").create_index("expires_at", expireAfterSeconds=0)
    get_collection("pairing_codes").create_index("pairing_code_hash", unique=True)
    yield
    close_mongo_connection()


app = FastAPI(title="Intentra API", version="1.0.0", lifespan=lifespan)
runtime_settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in runtime_settings.allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if runtime_settings.force_https:
    app.add_middleware(HTTPSRedirectMiddleware)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(settings.router, prefix="/api", tags=["settings"])
app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
app.include_router(updates.router, prefix="/api/updates", tags=["updates"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "intentra-server"}
