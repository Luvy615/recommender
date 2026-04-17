from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid
import hashlib

from backend.services.database import UserModel, SessionLocal
from backend.models.user import (
    UserRegister, UserLogin, UserProfileUpdate, User, UserProfile
)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class UserService:
    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def register(self, username: str, password: str, email: str = None, phone: str = None) -> dict:
        if self.db.query(UserModel).filter(UserModel.username == username).first():
            return {"success": False, "error": "用户名已存在"}

        user = UserModel(
            id=str(uuid.uuid4()),
            username=username,
            password_hash=hash_password(password),
            email=email,
            phone=phone,
            profile={},
            preferences={},
            budget={},
            is_profile_complete=False
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return {
            "success": True,
            "user": self._to_user(user)
        }

    def login(self, username: str, password: str) -> dict:
        user = self.db.query(UserModel).filter(
            UserModel.username == username,
            UserModel.password_hash == hash_password(password)
        ).first()

        if not user:
            return {"success": False, "error": "用户名或密码错误"}

        return {
            "success": True,
            "user": self._to_user(user)
        }

    def get_user(self, user_id: str) -> Optional[User]:
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return None
        return self._to_user(user)

    def get_user_by_username(self, username: str) -> Optional[User]:
        user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            return None
        return self._to_user(user)

    def update_profile(self, user_id: str, profile_data: UserProfileUpdate) -> Optional[User]:
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return None

        profile = user.profile or {}
        update_data = profile_data.model_dump(exclude_unset=True)
        profile.update({k: v for k, v in update_data.items() if v is not None})
        user.profile = profile

        required_fields = ['gender', 'age', 'height', 'weight', 'body_type']
        user.is_profile_complete = all(profile.get(f) for f in required_fields)

        self.db.commit()
        self.db.refresh(user)
        return self._to_user(user)

    def _to_user(self, user_model: UserModel) -> User:
        return User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            phone=user_model.phone,
            nickname=user_model.nickname,
            profile=UserProfile(**user_model.profile) if user_model.profile else None,
            preferences=user_model.preferences,
            budget=user_model.budget,
            is_profile_complete=user_model.is_profile_complete,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at
        )
