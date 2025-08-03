from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import schemas, models, auth
from database import SessionLocal

# Create router
router = APIRouter(
    prefix="/profile",
    tags=["User Profile"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stats")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get user statistics including total links, clicks, etc."""
    total_links = db.query(models.ShortLink).filter(
        models.ShortLink.user_id == current_user.id
    ).count()
    
    # TODO: Add click counting when analytics is implemented
    # total_clicks = db.query(func.sum(models.LinkClick.count)).filter(...).scalar() or 0
    
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "total_links": total_links,
        "total_clicks": 0,  # Placeholder until analytics is implemented
        "account_created": current_user.created_at,
        "last_updated": current_user.updated_at,
        "account_status": "Active" if current_user.is_active else "Inactive"
    }

@router.get("/activity")
def get_user_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get recent user activity"""
    recent_links = db.query(models.ShortLink).filter(
        models.ShortLink.user_id == current_user.id
    ).order_by(models.ShortLink.id.desc()).limit(limit).all()
    
    return {
        "recent_links": [
            {
                "id": link.id,
                "url": link.url,
                "short_code": link.short_code,
                "created_at": link.id  # Using ID as proxy for creation time until we add timestamps
            }
            for link in recent_links
        ]
    }
