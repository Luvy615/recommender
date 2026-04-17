from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserProfile(BaseModel):
    gender: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    body_type: Optional[str] = None
    skin_tone: Optional[str] = None
    style: Optional[str] = None


class UserPreferences(BaseModel):
    colors: list[str] = []
    avoid_styles: list[str] = []


class UserBudget(BaseModel):
    monthly: Optional[float] = None
    max_single: Optional[float] = None


class User(BaseModel):
    id: str
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    nickname: Optional[str] = None
    profile: Optional[UserProfile] = None
    preferences: Optional[UserPreferences] = None
    budget: Optional[UserBudget] = None
    is_profile_complete: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserProfileUpdate(BaseModel):
    gender: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    body_type: Optional[str] = None
    skin_tone: Optional[str] = None
    style: Optional[str] = None


BODY_TYPE_OPTIONS = ["梨型", "苹果型", "沙漏型", "H型"]
GENDER_OPTIONS = ["男", "女", "其他"]
SKIN_TONE_OPTIONS = ["白皙", "自然", "小麦色", "偏黑"]
STYLE_OPTIONS = ["休闲", "商务", "运动", "学院", "复古", "韩系", "甜美", "性感"]
