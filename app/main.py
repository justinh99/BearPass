from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import MONGO_URI, MONGO_DATABASE
from app.models.user import User 
from fastapi import Body
from app.routes import auth
from starlette.middleware.sessions import SessionMiddleware
import os

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "dev-secret-key"))

app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "BearPass backend is up!"}

@app.on_event("startup")
async def connect_to_db():
    client = AsyncIOMotorClient(MONGO_URI)
    await init_beanie(
        database=client[MONGO_DATABASE],
        document_models=[User]  # include User model
    )

@app.post("/test-create-user")
async def test_create_user(
    email: str = Body(...),
    name: str = Body(...),
    role: str = Body(...),
    google_id: str = Body(...)
):
    user = User(email=email, name=name, role=role, google_id=google_id)
    await user.insert()
    return {"msg": "User created", "id": str(user.id)}


@app.get("/db-check")
async def check_db():
    try:
        # Try a harmless query
        users = await User.find_all().to_list(1)  # limit=1
        return {"status": "connected", "user_count_sample": len(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB connection failed: {str(e)}")
    

