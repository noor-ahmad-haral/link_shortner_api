"""
Analytics API routes for link statistics and reporting
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

import models
import schemas
from auth import get_current_user
from database import SessionLocal
from .tracker import ClickTracker
from .models import LinkClick

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    dependencies=[Depends(get_current_user)]  # All analytics endpoints require authentication
)

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{link_id}/overview")
def get_link_analytics_overview(
    link_id: int,
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get comprehensive analytics overview for a specific link
    
    - **link_id**: ID of the link to analyze
    - **days**: Number of days to look back (1-365)
    """
    # Verify link ownership
    link = db.query(models.ShortLink).filter(
        models.ShortLink.id == link_id,
        models.ShortLink.user_id == current_user.id
    ).first()
    
    if not link:
        raise HTTPException(
            status_code=404,
            detail="Link not found or you don't have permission to view its analytics"
        )
    
    # Get analytics using tracker service
    tracker = ClickTracker(db)
    analytics = tracker.get_link_analytics(link_id, days)
    
    # Add link information
    analytics['link_info'] = {
        'id': link.id,
        'url': link.url,
        'short_code': link.short_code,
        'created_at': link.created_at,
        'total_clicks_lifetime': link.click_count or 0,
        'unique_clicks_lifetime': getattr(link, 'unique_clicks', 0) or 0
    }
    
    return analytics

@router.get("/{link_id}/devices")
def get_device_analytics(
    link_id: int,
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get detailed device and browser analytics for a link
    
    Returns breakdown by:
    - Device types (Desktop, Mobile, Tablet)
    - Device brands (Apple, Samsung, Google, etc.)
    - Browsers (Chrome, Firefox, Safari, etc.)
    - Operating Systems (Windows, iOS, Android, etc.)
    """
    # Verify link ownership
    link = db.query(models.ShortLink).filter(
        models.ShortLink.id == link_id,
        models.ShortLink.user_id == current_user.id
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Get device analytics
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    clicks = db.query(LinkClick).filter(
        LinkClick.link_id == link_id,
        LinkClick.clicked_at > cutoff_date
    ).all()
    
    if not clicks:
        return {
            'link_id': link_id,
            'period_days': days,
            'total_clicks': 0,
            'device_breakdown': {},
            'browser_breakdown': {},
            'os_breakdown': {}
        }
    
    # Calculate detailed breakdowns
    tracker = ClickTracker(db)
    device_stats = tracker._calculate_device_stats(clicks)
    browser_stats = tracker._calculate_browser_stats(clicks)
    
    return {
        'link_id': link_id,
        'period_days': days,
        'total_clicks': len(clicks),
        'device_breakdown': device_stats,
        'browser_breakdown': browser_stats,
        'detailed_devices': [
            {
                'device_info': click.device_info,
                'browser_info': click.browser_info,
                'os_info': click.os_info,
                'clicked_at': click.clicked_at,
                'is_unique': click.is_unique
            }
            for click in clicks[-50:]  # Last 50 clicks for detailed view
        ]
    }

@router.get("/{link_id}/geography")
def get_geographic_analytics(
    link_id: int,
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get geographic analytics for a link
    
    Returns breakdown by:
    - Countries
    - Cities/Regions
    - Timezone distribution
    - ISP information
    """
    # Verify link ownership
    link = db.query(models.ShortLink).filter(
        models.ShortLink.id == link_id,
        models.ShortLink.user_id == current_user.id
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Get geographic data
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    clicks = db.query(LinkClick).filter(
        LinkClick.link_id == link_id,
        LinkClick.clicked_at > cutoff_date
    ).all()
    
    if not clicks:
        return {
            'link_id': link_id,
            'period_days': days,
            'total_clicks': 0,
            'geographic_breakdown': {}
        }
    
    # Calculate geographic statistics
    tracker = ClickTracker(db)
    geographic_stats = tracker._calculate_geographic_stats(clicks)
    
    # Add timezone and ISP breakdown
    timezones = {}
    isps = {}
    
    for click in clicks:
        if click.timezone:
            timezones[click.timezone] = timezones.get(click.timezone, 0) + 1
        if click.isp:
            isps[click.isp] = isps.get(click.isp, 0) + 1
    
    total = len(clicks)
    
    return {
        'link_id': link_id,
        'period_days': days,
        'total_clicks': total,
        'geographic_breakdown': geographic_stats,
        'timezone_breakdown': {
            k: {'count': v, 'percentage': round(v/total*100, 1)} 
            for k, v in sorted(timezones.items(), key=lambda x: x[1], reverse=True)[:10]
        },
        'isp_breakdown': {
            k: {'count': v, 'percentage': round(v/total*100, 1)} 
            for k, v in sorted(isps.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    }

@router.get("/{link_id}/timeline")
def get_timeline_analytics(
    link_id: int,
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    granularity: str = Query("daily", description="Time granularity: hourly, daily, weekly"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get time-based analytics for a link
    
    Returns click timeline with specified granularity:
    - **hourly**: Clicks per hour (last 7 days max)
    - **daily**: Clicks per day
    - **weekly**: Clicks per week
    """
    # Verify link ownership
    link = db.query(models.ShortLink).filter(
        models.ShortLink.id == link_id,
        models.ShortLink.user_id == current_user.id
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Adjust days for hourly granularity
    if granularity == "hourly" and days > 7:
        days = 7
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    clicks = db.query(LinkClick).filter(
        LinkClick.link_id == link_id,
        LinkClick.clicked_at > cutoff_date
    ).order_by(LinkClick.clicked_at).all()
    
    # Calculate timeline based on granularity
    timeline = {}
    
    for click in clicks:
        if granularity == "hourly":
            key = click.clicked_at.strftime('%Y-%m-%d %H:00')
        elif granularity == "daily":
            key = click.clicked_at.strftime('%Y-%m-%d')
        elif granularity == "weekly":
            # Get week start (Monday)
            week_start = click.clicked_at - timedelta(days=click.clicked_at.weekday())
            key = week_start.strftime('%Y-%m-%d')
        else:
            key = click.clicked_at.strftime('%Y-%m-%d')
        
        if key not in timeline:
            timeline[key] = {'total': 0, 'unique': 0}
        
        timeline[key]['total'] += 1
        if click.is_unique:
            timeline[key]['unique'] += 1
    
    return {
        'link_id': link_id,
        'period_days': days,
        'granularity': granularity,
        'total_clicks': len(clicks),
        'timeline': dict(sorted(timeline.items()))
    }

@router.get("/{link_id}/clicks")
def get_raw_clicks(
    link_id: int,
    limit: int = Query(100, description="Number of recent clicks to return", ge=1, le=1000),
    offset: int = Query(0, description="Offset for pagination", ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get raw click data for detailed analysis
    
    Returns individual click records with full details
    """
    # Verify link ownership
    link = db.query(models.ShortLink).filter(
        models.ShortLink.id == link_id,
        models.ShortLink.user_id == current_user.id
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Get raw clicks with pagination
    clicks = db.query(LinkClick).filter(
        LinkClick.link_id == link_id
    ).order_by(LinkClick.clicked_at.desc()).offset(offset).limit(limit).all()
    
    # Get total count for pagination
    total_clicks = db.query(LinkClick).filter(LinkClick.link_id == link_id).count()
    
    return {
        'link_id': link_id,
        'total_clicks': total_clicks,
        'returned_clicks': len(clicks),
        'offset': offset,
        'limit': limit,
        'clicks': [
            {
                'id': click.id,
                'clicked_at': click.clicked_at,
                'location': click.location_info,
                'device': click.device_info,
                'browser': click.browser_info,
                'os': click.os_info,
                'referer': click.referer or 'Direct',
                'is_unique': click.is_unique,
                'is_bot': click.is_bot,
                'country_code': click.country_code,
                'timezone': click.timezone
            }
            for click in clicks
        ]
    }

@router.get("/{link_id}/export")
def export_analytics(
    link_id: int,
    format: str = Query("json", description="Export format: json or csv"),
    days: int = Query(30, description="Number of days to export", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Export analytics data in JSON or CSV format
    """
    # Verify link ownership
    link = db.query(models.ShortLink).filter(
        models.ShortLink.id == link_id,
        models.ShortLink.user_id == current_user.id
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Get comprehensive analytics
    tracker = ClickTracker(db)
    analytics = tracker.get_link_analytics(link_id, days)
    
    if format.lower() == "csv":
        # Convert to CSV format
        from fastapi.responses import StreamingResponse
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            'Date', 'Total Clicks', 'Unique Clicks', 'Top Country', 
            'Top Device Type', 'Top Browser', 'Top OS'
        ])
        
        # Write summary data
        top_country = list(analytics['geography']['countries'].keys())[0] if analytics['geography']['countries'] else 'N/A'
        top_device = list(analytics['devices']['types'].keys())[0] if analytics['devices']['types'] else 'N/A'
        top_browser = list(analytics['browsers']['browsers'].keys())[0] if analytics['browsers']['browsers'] else 'N/A'
        top_os = list(analytics['browsers']['operating_systems'].keys())[0] if analytics['browsers']['operating_systems'] else 'N/A'
        
        writer.writerow([
            datetime.utcnow().strftime('%Y-%m-%d'),
            analytics['total_clicks'],
            analytics['unique_clicks'],
            top_country,
            top_device,
            top_browser,
            top_os
        ])
        
        output.seek(0)
        
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=link_{link_id}_analytics.csv"}
        )
    
    else:
        # Return JSON format
        return {
            'export_format': 'json',
            'exported_at': datetime.utcnow(),
            'link_info': {
                'id': link.id,
                'url': link.url,
                'short_code': link.short_code,
                'created_at': link.created_at
            },
            'analytics': analytics
        }

# Dashboard endpoint for user's all links overview
@router.get("/dashboard")
def get_analytics_dashboard(
    days: int = Query(7, description="Number of days for dashboard stats", ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get analytics dashboard for all user's links
    
    Returns overview statistics for all links owned by the user
    """
    # Get user's links
    user_links = db.query(models.ShortLink).filter(
        models.ShortLink.user_id == current_user.id
    ).all()
    
    if not user_links:
        return {
            'total_links': 0,
            'total_clicks': 0,
            'total_unique_clicks': 0,
            'top_performing_links': [],
            'recent_activity': []
        }
    
    # Calculate aggregate statistics
    total_links = len(user_links)
    total_clicks = sum(link.click_count or 0 for link in user_links)
    total_unique_clicks = sum(getattr(link, 'unique_clicks', 0) or 0 for link in user_links)
    
    # Get top performing links
    top_links = sorted(user_links, key=lambda x: x.click_count or 0, reverse=True)[:5]
    
    # Get recent activity across all links
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    recent_clicks = db.query(LinkClick).join(models.ShortLink).filter(
        models.ShortLink.user_id == current_user.id,
        LinkClick.clicked_at > cutoff_date
    ).order_by(LinkClick.clicked_at.desc()).limit(20).all()
    
    return {
        'user_id': current_user.id,
        'period_days': days,
        'total_links': total_links,
        'total_clicks': total_clicks,
        'total_unique_clicks': total_unique_clicks,
        'average_clicks_per_link': round(total_clicks / total_links, 1) if total_links > 0 else 0,
        'top_performing_links': [
            {
                'id': link.id,
                'short_code': link.short_code,
                'url': link.url[:50] + '...' if len(link.url) > 50 else link.url,
                'total_clicks': link.click_count or 0,
                'unique_clicks': getattr(link, 'unique_clicks', 0) or 0,
                'created_at': link.created_at
            }
            for link in top_links
        ],
        'recent_activity': [
            {
                'link_short_code': click.link.short_code,
                'clicked_at': click.clicked_at,
                'location': click.location_info,
                'device': click.device_type,
                'browser': click.browser_name
            }
            for click in recent_clicks
        ]
    }
