from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import bcrypt
import jwt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Secret
JWT_SECRET = os.environ.get('JWT_SECRET', 'wfps_secret_key_change_in_production')
JWT_ALGORITHM = "HS256"

# Create the main app
app = FastAPI(title="wFPS API")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# ========== MODELS ==========

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class GameProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    process_names: List[str] = []
    priority_level: str = "high"  # low, below_normal, normal, above_normal, high, realtime
    kill_background_apps: bool = True
    clear_memory: bool = True
    background_apps_whitelist: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GameProfileCreate(BaseModel):
    name: str
    process_names: List[str] = []
    priority_level: str = "high"
    kill_background_apps: bool = True
    clear_memory: bool = True
    background_apps_whitelist: List[str] = []

class GameProfileUpdate(BaseModel):
    name: Optional[str] = None
    process_names: Optional[List[str]] = None
    priority_level: Optional[str] = None
    kill_background_apps: Optional[bool] = None
    clear_memory: Optional[bool] = None
    background_apps_whitelist: Optional[List[str]] = None

class AgentTelemetry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    agent_id: str
    cpu_usage: float
    ram_usage: float
    ram_available: float
    temperature: Optional[float] = None
    active_game: Optional[str] = None
    fps: Optional[int] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AgentTelemetryCreate(BaseModel):
    agent_id: str
    cpu_usage: float
    ram_usage: float
    ram_available: float
    temperature: Optional[float] = None
    active_game: Optional[str] = None
    fps: Optional[int] = None

class BoostCommand(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    profile_id: Optional[str] = None
    action: str  # "start_boost", "stop_boost", "apply_profile"
    status: str = "pending"  # pending, executing, completed, failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BoostCommandCreate(BaseModel):
    profile_id: Optional[str] = None
    action: str

# ========== AUTH HELPERS ==========

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    payload = {"user_id": user_id, "exp": datetime.now(timezone.utc).timestamp() + 86400 * 30}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["user_id"]
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ========== AUTH ROUTES ==========

@api_router.post("/auth/register", response_model=Dict[str, Any])
async def register(user_data: UserCreate):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user = User(username=user_data.username, email=user_data.email)
    user_dict = user.model_dump()
    user_dict['password'] = hash_password(user_data.password)
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    
    await db.users.insert_one(user_dict)
    token = create_token(user.id)
    
    return {"token": token, "user": {"id": user.id, "username": user.username, "email": user.email}}

@api_router.post("/auth/login", response_model=Dict[str, Any])
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user['id'])
    return {"token": token, "user": {"id": user['id'], "username": user['username'], "email": user['email']}}

# ========== PROFILE ROUTES ==========

@api_router.post("/profiles", response_model=GameProfile)
async def create_profile(profile: GameProfileCreate, user_id: str = Depends(get_current_user)):
    profile_obj = GameProfile(**profile.model_dump(), user_id=user_id)
    profile_dict = profile_obj.model_dump()
    profile_dict['created_at'] = profile_dict['created_at'].isoformat()
    profile_dict['updated_at'] = profile_dict['updated_at'].isoformat()
    
    await db.profiles.insert_one(profile_dict)
    return profile_obj

@api_router.get("/profiles", response_model=List[GameProfile])
async def get_profiles(user_id: str = Depends(get_current_user)):
    profiles = await db.profiles.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    for p in profiles:
        if isinstance(p['created_at'], str):
            p['created_at'] = datetime.fromisoformat(p['created_at'])
        if isinstance(p['updated_at'], str):
            p['updated_at'] = datetime.fromisoformat(p['updated_at'])
    return profiles

@api_router.get("/profiles/{profile_id}", response_model=GameProfile)
async def get_profile(profile_id: str, user_id: str = Depends(get_current_user)):
    profile = await db.profiles.find_one({"id": profile_id, "user_id": user_id}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if isinstance(profile['created_at'], str):
        profile['created_at'] = datetime.fromisoformat(profile['created_at'])
    if isinstance(profile['updated_at'], str):
        profile['updated_at'] = datetime.fromisoformat(profile['updated_at'])
    return profile

@api_router.put("/profiles/{profile_id}", response_model=GameProfile)
async def update_profile(profile_id: str, updates: GameProfileUpdate, user_id: str = Depends(get_current_user)):
    profile = await db.profiles.find_one({"id": profile_id, "user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.profiles.update_one({"id": profile_id}, {"$set": update_data})
    updated = await db.profiles.find_one({"id": profile_id}, {"_id": 0})
    
    if isinstance(updated['created_at'], str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    if isinstance(updated['updated_at'], str):
        updated['updated_at'] = datetime.fromisoformat(updated['updated_at'])
    return updated

@api_router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: str, user_id: str = Depends(get_current_user)):
    result = await db.profiles.delete_one({"id": profile_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Profile deleted"}

# ========== TELEMETRY ROUTES ==========

@api_router.post("/telemetry", response_model=AgentTelemetry)
async def submit_telemetry(telemetry: AgentTelemetryCreate, user_id: str = Depends(get_current_user)):
    telemetry_obj = AgentTelemetry(**telemetry.model_dump(), user_id=user_id)
    telemetry_dict = telemetry_obj.model_dump()
    telemetry_dict['timestamp'] = telemetry_dict['timestamp'].isoformat()
    
    await db.telemetry.insert_one(telemetry_dict)
    return telemetry_obj

@api_router.get("/telemetry/latest", response_model=AgentTelemetry)
async def get_latest_telemetry(user_id: str = Depends(get_current_user)):
    telemetry = await db.telemetry.find_one(
        {"user_id": user_id},
        {"_id": 0},
        sort=[("timestamp", -1)]
    )
    if not telemetry:
        raise HTTPException(status_code=404, detail="No telemetry data found")
    
    if isinstance(telemetry['timestamp'], str):
        telemetry['timestamp'] = datetime.fromisoformat(telemetry['timestamp'])
    return telemetry

@api_router.get("/telemetry/history", response_model=List[AgentTelemetry])
async def get_telemetry_history(limit: int = 100, user_id: str = Depends(get_current_user)):
    telemetry_list = await db.telemetry.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    for t in telemetry_list:
        if isinstance(t['timestamp'], str):
            t['timestamp'] = datetime.fromisoformat(t['timestamp'])
    return telemetry_list

# ========== BOOST COMMAND ROUTES ==========

@api_router.post("/boost/command", response_model=BoostCommand)
async def create_boost_command(command: BoostCommandCreate, user_id: str = Depends(get_current_user)):
    command_obj = BoostCommand(**command.model_dump(), user_id=user_id)
    command_dict = command_obj.model_dump()
    command_dict['created_at'] = command_dict['created_at'].isoformat()
    
    await db.boost_commands.insert_one(command_dict)
    return command_obj

@api_router.get("/boost/commands/pending", response_model=List[BoostCommand])
async def get_pending_commands(user_id: str = Depends(get_current_user)):
    commands = await db.boost_commands.find(
        {"user_id": user_id, "status": "pending"},
        {"_id": 0}
    ).to_list(100)
    
    for c in commands:
        if isinstance(c['created_at'], str):
            c['created_at'] = datetime.fromisoformat(c['created_at'])
    return commands

@api_router.put("/boost/command/{command_id}/status")
async def update_command_status(command_id: str, status: str, user_id: str = Depends(get_current_user)):
    result = await db.boost_commands.update_one(
        {"id": command_id, "user_id": user_id},
        {"$set": {"status": status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Command not found")
    return {"message": "Command status updated"}

# ========== SYSTEM ROUTES ==========

@api_router.get("/")
async def root():
    return {"message": "wFPS API v1.0", "status": "running"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()