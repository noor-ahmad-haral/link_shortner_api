from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi import HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from routes import auth, links, profile
import models
from database import SessionLocal
from config import settings
import time
from datetime import datetime

app = FastAPI(
    title="URL Shortener API",
    description="""
    ## A secure and fast API for shortening URLs and managing links
    
    ### Features:
    - 🔐 **User Authentication** - Register, login, profile management
    - 🔗 **Link Management** - Create, update, delete short links
    - 📊 **Analytics Ready** - Track clicks and usage
    - 🛡️ **Security** - Rate limiting, input validation, CORS protection
    
    """,
)

# Security Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add the title and description for the API documentation
# (Already set in FastAPI constructor above)

@app.get("/", tags=["Root"])
def read_root():
    return {
        "title": app.title,
        "description": app.description,
        "version": app.version,
        "environment": settings.ENVIRONMENT,
        "message": "Welcome to URL Shortener API",
        "endpoints": {
            "create_link": "/links/create",
            "my_links": "/links/my-links",
            "redirect": "/{short_code}",
            "auth": "/auth/*",
            "profile": "/profile/*",
            "docs": "/docs",
            "health": "/health"
        }
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.ENVIRONMENT,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )

# Redirect endpoint for short URLs
@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    # Find the link by short_code
    link = db.query(models.ShortLink).filter(models.ShortLink.short_code == short_code).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    # Track the click
    try:
        # Increment click count
        link.click_count += 1
        # Update last clicked timestamp
        link.last_clicked = datetime.utcnow()
        # Update the updated_at timestamp
        link.updated_at = datetime.utcnow()
        
        # Save changes to database
        db.commit()
        db.refresh(link)
    except Exception as e:
        # If tracking fails, still redirect (don't break user experience)
        db.rollback()
    
    # Redirect to the original URL
    return RedirectResponse(url=link.url, status_code=301)

app.include_router(auth.router)
app.include_router(links.router)
app.include_router(profile.router)
