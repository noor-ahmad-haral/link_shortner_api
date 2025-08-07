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

# Import analytics modules
from analytics.tracker import ClickTracker
from analytics import analytics_router

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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
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

# Redirect endpoint for short URLs with advanced analytics tracking
@app.get("/{short_code}")
def redirect_to_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    # Find the link by short_code
    link = db.query(models.ShortLink).filter(models.ShortLink.short_code == short_code).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    # Track the click with comprehensive analytics
    try:
        tracker = ClickTracker(db)
        click_record = tracker.track_click(request, link)
        
        # If tracking failed, fall back to basic tracking
        if not click_record:
            # Basic fallback tracking
            link.click_count = (link.click_count or 0) + 1
            link.last_clicked = datetime.utcnow()
            link.updated_at = datetime.utcnow()
            db.commit()
    
    except Exception as e:
        # If tracking fails completely, still redirect (don't break user experience)
        try:
            # Minimal tracking fallback
            link.click_count = (link.click_count or 0) + 1
            link.last_clicked = datetime.utcnow()
            db.commit()
        except:
            # If even basic tracking fails, just redirect
            pass
    
    # Redirect to the original URL
    return RedirectResponse(url=link.url, status_code=301)

app.include_router(auth.router)
app.include_router(links.router)
app.include_router(profile.router)
app.include_router(analytics_router)  # Add analytics routes

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)