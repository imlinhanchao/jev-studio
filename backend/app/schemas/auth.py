from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str = Field(..., description="管理员用户名")
    password: str = Field(..., description="管理员密码")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str = "admin"
    expires_in: int

class UserInfoResponse(BaseModel):
    username: str
    role: str = "admin"
