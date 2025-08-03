from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import string, random

import models
import schemas
from auth import get_current_user, get_current_user_optional
from database import SessionLocal

router = APIRouter(
    prefix="/links",
    tags=["links"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper to generate random short code if no alias provided
def generate_short_code(length: int = 6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

# ✅ PROTECTED: Only logged-in users can see *their* links
@router.get("/my-links", response_model=list[schemas.ShortLinkResponse])
def get_my_links(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    links = db.query(models.ShortLink).filter(models.ShortLink.user_id == current_user.id).all()
    
    # Add short_url to each link
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    response_links = []
    
    for link in links:
        response_links.append({
            "id": link.id,
            "url": link.url,
            "short_code": link.short_code,
            "short_url": f"{base_url}/{link.short_code}",
            "user_id": link.user_id,
            "click_count": link.click_count or 0,
            "last_clicked": link.last_clicked,
            "created_at": link.created_at,
            "updated_at": link.updated_at
        })
    
    return response_links

# ✅ OPEN: Anyone can create a link (logged in or anonymous)
@router.post("/create", response_model=schemas.ShortLinkResponse)
def create_link(
    link: schemas.ShortLinkCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    if link.alias:
        # Check if alias is unique
        existing = db.query(models.ShortLink).filter(models.ShortLink.short_code == link.alias).first()
        if existing:
            raise HTTPException(status_code=400, detail="Alias is already in use")
        short_code = link.alias
    else:
        # Generate unique short code
        while True:
            short_code = generate_short_code()
            existing = db.query(models.ShortLink).filter(models.ShortLink.short_code == short_code).first()
            if not existing:
                break

    new_link = models.ShortLink(
        url=link.url,
        short_code=short_code,
        user_id=current_user.id if current_user else None,
        click_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    # Create the complete short URL
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    short_url = f"{base_url}/{short_code}"
    
    # Create response with short_url
    response_data = {
        "id": new_link.id,
        "url": new_link.url,
        "short_code": new_link.short_code,
        "short_url": short_url,
        "user_id": new_link.user_id,
        "click_count": new_link.click_count,
        "last_clicked": new_link.last_clicked,
        "created_at": new_link.created_at,
        "updated_at": new_link.updated_at
    }

    return response_data

# 🗑️ DELETE LINK - Only link owner can delete
@router.delete("/{link_id}")
def delete_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Find the link
    link = db.query(models.ShortLink).filter(models.ShortLink.id == link_id).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Check if user owns this link
    if link.user_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="You can only delete your own links"
        )
    
    # Delete the link
    db.delete(link)
    db.commit()
    
    return {"message": f"Link '{link.short_code}' deleted successfully"}

# ✏️ UPDATE LINK - Only link owner can update
@router.put("/{link_id}", response_model=schemas.ShortLinkResponse)
def update_link(
    link_id: int,
    link_update: schemas.ShortLinkUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Find the link
    link = db.query(models.ShortLink).filter(models.ShortLink.id == link_id).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Check if user owns this link
    if link.user_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="You can only update your own links"
        )
    
    # Validate if new alias is provided and check if it's unique
    if link_update.alias and link_update.alias != link.short_code:
        existing = db.query(models.ShortLink).filter(
            models.ShortLink.short_code == link_update.alias,
            models.ShortLink.id != link_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Alias is already in use")
    
    # Update fields if provided
    update_data = link_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "alias":
            setattr(link, "short_code", value)
        else:
            setattr(link, field, value)
    
    # Update the updated_at timestamp
    link.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(link)
    
    # Create the complete short URL
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    short_url = f"{base_url}/{link.short_code}"
    
    # Create response with short_url
    response_data = {
        "id": link.id,
        "url": link.url,
        "short_code": link.short_code,
        "short_url": short_url,
        "user_id": link.user_id,
        "click_count": link.click_count or 0,
        "last_clicked": link.last_clicked,
        "created_at": link.created_at,
        "updated_at": link.updated_at
    }

    return response_data

# 📊 GET SINGLE LINK - Only link owner can view details
@router.get("/{link_id}", response_model=schemas.ShortLinkResponse)
def get_link(
    link_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Find the link
    link = db.query(models.ShortLink).filter(models.ShortLink.id == link_id).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Check if user owns this link
    if link.user_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="You can only view your own links"
        )
    
    # Create the complete short URL
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    short_url = f"{base_url}/{link.short_code}"
    
    # Create response with short_url
    response_data = {
        "id": link.id,
        "url": link.url,
        "short_code": link.short_code,
        "short_url": short_url,
        "user_id": link.user_id,
        "click_count": link.click_count or 0,
        "last_clicked": link.last_clicked,
        "created_at": link.created_at,
        "updated_at": link.updated_at
    }

    return response_data


# 🗑️ BULK DELETE LINKS - Delete multiple links at once
@router.delete("/bulk-delete")
def bulk_delete_links(
    link_ids: List[int],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not link_ids:
        raise HTTPException(status_code=400, detail="No link IDs provided")
    
    # Find all links
    links = db.query(models.ShortLink).filter(
        models.ShortLink.id.in_(link_ids),
        models.ShortLink.user_id == current_user.id
    ).all()
    
    if not links:
        raise HTTPException(status_code=404, detail="No links found or you don't own these links")
    
    # Check if user owns all requested links
    found_ids = [link.id for link in links]
    not_found_ids = [link_id for link_id in link_ids if link_id not in found_ids]
    
    if not_found_ids:
        raise HTTPException(
            status_code=403, 
            detail=f"You don't own or these links don't exist: {not_found_ids}"
        )
    
    # Delete all links
    deleted_count = len(links)
    for link in links:
        db.delete(link)
    
    db.commit()
    
    return {
        "message": f"Successfully deleted {deleted_count} links",
        "deleted_count": deleted_count,
        "deleted_ids": found_ids
    }
