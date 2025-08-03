from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for Google users
    provider = Column(String, default="local")  # 'local' or 'google'
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=True)  # Will be set in the route
    updated_at = Column(DateTime, nullable=True)  # Will be set in the route

    # Relationship to ShortLink
    links = relationship("ShortLink", back_populates="owner")


class ShortLink(Base):
    __tablename__ = "short_links"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Click tracking fields
    click_count = Column(Integer, default=0, nullable=False)
    last_clicked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)  # Will be set in the route
    updated_at = Column(DateTime, nullable=True)  # Will be set in the route

    owner = relationship("User", back_populates="links")
