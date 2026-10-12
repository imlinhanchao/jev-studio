from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.security import verify_admin_credentials, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse, UserInfoResponse
from app.api.deps import get_current_admin

router = APIRouter(prefix="/auth", tags=["Admin Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    """
    Admin login endpoint.
    Validates username and password configured in backend .env.
    """
    if not verify_admin_credentials(payload.username, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误，请检查后端 .env 配置",
        )

    access_token = create_access_token({
        "sub": settings.ADMIN_USERNAME,
        "role": "admin",
    })

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        username=settings.ADMIN_USERNAME,
        role="admin",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
    )

@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_profile(
    current_admin: dict = Depends(get_current_admin),
):
    """
    Returns current authenticated administrator profile.
    """
    return UserInfoResponse(
        username=current_admin["username"],
        role=current_admin.get("role", "admin"),
    )

@router.post("/logout")
async def logout(
    current_admin: dict = Depends(get_current_admin),
):
    """
    Admin logout endpoint.
    """
    return {"message": "已安全退出登录"}
