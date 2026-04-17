from fastapi import APIRouter, HTTPException

from backend.services.user_service import UserService
from backend.models.user import UserRegister, UserLogin, UserProfileUpdate

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
async def register(request: UserRegister):
    service = UserService()
    try:
        result = service.register(
            username=request.username,
            password=request.password,
            email=request.email,
            phone=request.phone
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result["user"]
    finally:
        service.close()


@router.post("/login")
async def login(request: UserLogin):
    service = UserService()
    try:
        result = service.login(
            username=request.username,
            password=request.password
        )
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result["error"])
        return result["user"]
    finally:
        service.close()


@router.get("/user/{user_id}")
async def get_user(user_id: str):
    service = UserService()
    try:
        user = service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return user
    finally:
        service.close()


@router.put("/profile/{user_id}")
async def update_profile(user_id: str, profile: UserProfileUpdate):
    service = UserService()
    try:
        user = service.update_profile(user_id, profile)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return user
    finally:
        service.close()
