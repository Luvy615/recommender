from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

from backend.config import config

Base = declarative_base()
engine = create_engine(config.DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(20), unique=True, nullable=True)
    nickname = Column(String(100), nullable=True)
    profile = Column(JSON, nullable=True)
    preferences = Column(JSON, nullable=True)
    budget = Column(JSON, nullable=True)
    is_profile_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    outfits = relationship("SavedOutfitModel", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("ConversationModel", back_populates="user", cascade="all, delete-orphan")


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(50), nullable=True)
    source_id = Column(String(100), nullable=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=True)
    sub_category = Column(String(50), nullable=True)
    color = Column(String(50), nullable=True)
    style = Column(String(50), nullable=True)
    season = Column(String(20), nullable=True)
    price = Column(Float, nullable=True)
    image_url = Column(String(1000), nullable=True)
    product_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_category', 'category'),
        Index('idx_style', 'style'),
        Index('idx_color', 'color'),
        Index('idx_source', 'source'),
    )


class SavedOutfitModel(Base):
    __tablename__ = "saved_outfits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=True)
    occasion = Column(String(50), nullable=True)
    weather = Column(String(50), nullable=True)
    style = Column(String(50), nullable=True)
    rating = Column(Integer, default=0)
    is_favorite = Column(Boolean, default=False)
    outfit_image = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserModel", back_populates="outfits")
    items = relationship("SavedOutfitItemModel", back_populates="outfit", cascade="all, delete-orphan")


class SavedOutfitItemModel(Base):
    __tablename__ = "saved_outfit_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    outfit_id = Column(String(36), ForeignKey("saved_outfits.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String(36), nullable=True)
    product_name = Column(String(255), nullable=False)
    product_price = Column(Float, nullable=True)
    product_image_url = Column(String(500), nullable=True)
    product_url = Column(String(500), nullable=True)
    sort_order = Column(Integer, default=0)

    outfit = relationship("SavedOutfitModel", back_populates="items")


class ConversationModel(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(100), nullable=True)
    messages = Column(JSON, nullable=True)
    context = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserModel", back_populates="conversations")
