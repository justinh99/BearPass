from fastapi import APIRouter, HTTPException, Request
from starlette.responses import RedirectResponse
from app.config import GOOGLE_REDIRECT_URI
from app.utils.oauth import oauth
from app.models.user import User
from app.utils.jwt import create_access_token

router = APIRouter()

@router.get("/login")
async def login(request: Request):
    # ✅ Explicitly pass redirect_uri
    return await oauth.google.authorize_redirect(request, redirect_uri=GOOGLE_REDIRECT_URI)

@router.get("/auth/google/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)

    # ✅ Use userinfo instead of parse_id_token
    user_info = await oauth.google.userinfo(token=token)

    google_id = user_info.get("sub")
    email = user_info.get("email")
    name = user_info.get("name")

    if not google_id or not email:
        raise HTTPException(status_code=400, detail="Google login failed")

    user = await User.find_one(User.google_id == google_id)
    if not user:
        user = User(email=email, name=name, google_id=google_id, role="customer")
        await user.insert()

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "user": user.dict()}

