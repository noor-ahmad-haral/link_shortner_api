"""
Click tracking service for recording and analyzing link clicks
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request

from .models import LinkClick
from .parser import UserAgentParser, IPGeolocation
import models
import logging

logger = logging.getLogger(__name__)

class ClickTracker:
    """
    Service for tracking link clicks with detailed analytics
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def track_click(self, request: Request, link: models.ShortLink) -> Optional[LinkClick]:
        """
        Track a click on a short link with comprehensive analytics
        
        Args:
            request: FastAPI request object containing headers and client info
            link: ShortLink model instance that was clicked
            
        Returns:
            LinkClick instance if tracking successful, None otherwise
        """
        try:
            # Extract request information
            ip_address = self._get_client_ip(request)
            user_agent = request.headers.get('user-agent', '')
            referer = request.headers.get('referer', '')
            
            # Parse user agent for device/browser info
            device_info = UserAgentParser.parse(user_agent)
            
            # Get geographic information (async to not slow down redirect)
            location_info = self._get_location_info(ip_address)
            
            # Determine if this is a unique visitor
            is_unique = self._is_unique_visitor(link.id, ip_address, user_agent)
            
            # Create click record
            click = LinkClick(
                link_id=link.id,
                # Network information
                ip_address=IPGeolocation.mask_ip(ip_address),  # Privacy-masked IP
                user_agent=user_agent,
                referer=referer,
                
                # Geographic data
                country=location_info.get('country'),
                country_code=location_info.get('country_code'),
                city=location_info.get('city'),
                region=location_info.get('region'),
                latitude=location_info.get('latitude'),
                longitude=location_info.get('longitude'),
                timezone=location_info.get('timezone'),
                isp=location_info.get('isp'),
                
                # Browser information
                browser_name=device_info.get('browser_name'),
                browser_version=device_info.get('browser_version'),
                browser_family=device_info.get('browser_family'),
                
                # Operating System information
                os_name=device_info.get('os_name'),
                os_version=device_info.get('os_version'),
                os_family=device_info.get('os_family'),
                
                # Device information
                device_type=device_info.get('device_type'),
                device_brand=device_info.get('device_brand'),
                device_model=device_info.get('device_model'),
                device_family=device_info.get('device_family'),
                
                # Screen information (if available in enhanced detection)
                screen_resolution=device_info.get('screen_resolution'),
                
                # Behavioral tracking
                is_unique=is_unique,
                is_bot=device_info.get('is_bot', False),
                session_id=self._generate_session_id(ip_address, user_agent),
                
                # Timestamps
                clicked_at=datetime.utcnow(),
                processed_at=datetime.utcnow()
            )
            
            # Save to database
            self.db.add(click)
            
            # Update link statistics
            self._update_link_stats(link, is_unique)
            
            # Commit transaction
            self.db.commit()
            self.db.refresh(click)
            
            logger.info(f"Click tracked for link {link.id}: {device_info.get('device_type')} {device_info.get('browser_name')} from {location_info.get('country', 'Unknown')}")
            
            return click
            
        except Exception as e:
            logger.error(f"Error tracking click for link {link.id}: {e}")
            self.db.rollback()
            return None
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request, handling proxies
        """
        # Check for forwarded IP (behind proxy/load balancer)
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # Take the first IP if multiple are present
            return forwarded_for.split(',')[0].strip()
        
        # Check for real IP header (some proxies use this)
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct client IP
        client_host = getattr(request.client, 'host', '127.0.0.1')
        return client_host
    
    def _get_location_info(self, ip_address: str) -> Dict[str, Any]:
        """
        Get geographic information for IP address
        This could be made async in production for better performance
        """
        try:
            return IPGeolocation.get_location(ip_address)
        except Exception as e:
            logger.warning(f"Failed to get location for IP {ip_address}: {e}")
            return {}
    
    def _is_unique_visitor(self, link_id: int, ip_address: str, user_agent: str) -> bool:
        """
        Determine if this is a unique visitor based on IP and browser fingerprint
        """
        try:
            # Create a fingerprint from IP and user agent
            fingerprint = self._create_visitor_fingerprint(ip_address, user_agent)
            
            # Check if we've seen this fingerprint for this link in the last 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            existing_click = self.db.query(LinkClick).filter(
                LinkClick.link_id == link_id,
                LinkClick.session_id == fingerprint,
                LinkClick.clicked_at > cutoff_time
            ).first()
            
            return existing_click is None
            
        except Exception as e:
            logger.error(f"Error checking unique visitor: {e}")
            return True  # Default to unique if we can't determine
    
    def _create_visitor_fingerprint(self, ip_address: str, user_agent: str) -> str:
        """
        Create a visitor fingerprint for session tracking
        """
        # Combine IP and user agent for fingerprinting
        fingerprint_string = f"{ip_address}:{user_agent}"
        
        # Hash for privacy and consistent length
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()[:16]
    
    def _generate_session_id(self, ip_address: str, user_agent: str) -> str:
        """
        Generate a session ID for tracking multiple clicks from same visitor
        """
        return self._create_visitor_fingerprint(ip_address, user_agent)
    
    def _update_link_stats(self, link: models.ShortLink, is_unique: bool):
        """
        Update aggregate statistics on the short link
        """
        try:
            # Always increment total clicks
            if link.click_count is None:
                link.click_count = 1
            else:
                link.click_count += 1
            
            # Increment unique clicks if this is unique
            if is_unique:
                if link.unique_clicks is None:
                    link.unique_clicks = 1
                else:
                    link.unique_clicks += 1
            
            # Update last clicked timestamp
            link.last_clicked = datetime.utcnow()
            link.updated_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error updating link stats: {e}")
    
    def get_link_analytics(self, link_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a specific link
        
        Args:
            link_id: ID of the link to analyze
            days: Number of days to look back (default 30)
            
        Returns:
            Dictionary containing analytics data
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all clicks for the period
            clicks = self.db.query(LinkClick).filter(
                LinkClick.link_id == link_id,
                LinkClick.clicked_at > cutoff_date
            ).all()
            
            if not clicks:
                return self._empty_analytics()
            
            # Calculate basic statistics
            total_clicks = len(clicks)
            unique_clicks = len([c for c in clicks if c.is_unique])
            
            # Device analytics
            device_stats = self._calculate_device_stats(clicks)
            
            # Geographic analytics
            geographic_stats = self._calculate_geographic_stats(clicks)
            
            # Browser analytics
            browser_stats = self._calculate_browser_stats(clicks)
            
            # Time-based analytics
            time_stats = self._calculate_time_stats(clicks)
            
            return {
                'link_id': link_id,
                'period_days': days,
                'total_clicks': total_clicks,
                'unique_clicks': unique_clicks,
                'click_through_rate': round((unique_clicks / total_clicks * 100), 2) if total_clicks > 0 else 0,
                'devices': device_stats,
                'geography': geographic_stats,
                'browsers': browser_stats,
                'timeline': time_stats,
                'top_referrers': self._calculate_referrer_stats(clicks)
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics for link {link_id}: {e}")
            return self._empty_analytics()
    
    def _calculate_device_stats(self, clicks) -> Dict[str, Any]:
        """Calculate device type and brand statistics"""
        device_types = {}
        device_brands = {}
        
        for click in clicks:
            # Device types
            device_type = click.device_type or 'Unknown'
            device_types[device_type] = device_types.get(device_type, 0) + 1
            
            # Device brands
            device_brand = click.device_brand or 'Unknown'
            device_brands[device_brand] = device_brands.get(device_brand, 0) + 1
        
        total = len(clicks)
        return {
            'types': {k: {'count': v, 'percentage': round(v/total*100, 1)} 
                     for k, v in sorted(device_types.items(), key=lambda x: x[1], reverse=True)},
            'brands': {k: {'count': v, 'percentage': round(v/total*100, 1)} 
                      for k, v in sorted(device_brands.items(), key=lambda x: x[1], reverse=True)[:10]}
        }
    
    def _calculate_geographic_stats(self, clicks) -> Dict[str, Any]:
        """Calculate geographic distribution statistics"""
        countries = {}
        cities = {}
        
        for click in clicks:
            # Countries
            country = click.country or 'Unknown'
            countries[country] = countries.get(country, 0) + 1
            
            # Cities
            if click.city and click.country:
                city_key = f"{click.city}, {click.country}"
                cities[city_key] = cities.get(city_key, 0) + 1
        
        total = len(clicks)
        return {
            'countries': {k: {'count': v, 'percentage': round(v/total*100, 1)} 
                         for k, v in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]},
            'cities': {k: {'count': v, 'percentage': round(v/total*100, 1)} 
                      for k, v in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]}
        }
    
    def _calculate_browser_stats(self, clicks) -> Dict[str, Any]:
        """Calculate browser and OS statistics"""
        browsers = {}
        operating_systems = {}
        
        for click in clicks:
            # Browsers
            browser = click.browser_name or 'Unknown'
            browsers[browser] = browsers.get(browser, 0) + 1
            
            # Operating Systems
            os = click.os_name or 'Unknown'
            operating_systems[os] = operating_systems.get(os, 0) + 1
        
        total = len(clicks)
        return {
            'browsers': {k: {'count': v, 'percentage': round(v/total*100, 1)} 
                        for k, v in sorted(browsers.items(), key=lambda x: x[1], reverse=True)[:10]},
            'operating_systems': {k: {'count': v, 'percentage': round(v/total*100, 1)} 
                                 for k, v in sorted(operating_systems.items(), key=lambda x: x[1], reverse=True)[:10]}
        }
    
    def _calculate_time_stats(self, clicks) -> Dict[str, Any]:
        """Calculate time-based statistics"""
        daily_clicks = {}
        hourly_clicks = {}
        
        for click in clicks:
            # Daily breakdown
            date_key = click.clicked_at.strftime('%Y-%m-%d')
            daily_clicks[date_key] = daily_clicks.get(date_key, 0) + 1
            
            # Hourly breakdown
            hour_key = click.clicked_at.hour
            hourly_clicks[hour_key] = hourly_clicks.get(hour_key, 0) + 1
        
        return {
            'daily': dict(sorted(daily_clicks.items())),
            'hourly': dict(sorted(hourly_clicks.items()))
        }
    
    def _calculate_referrer_stats(self, clicks) -> Dict[str, Any]:
        """Calculate top referrer statistics"""
        referrers = {}
        
        for click in clicks:
            referer = click.referer or 'Direct'
            if referer != 'Direct':
                # Extract domain from referer URL
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(referer).netloc
                    referrers[domain] = referrers.get(domain, 0) + 1
                except:
                    referrers[referer] = referrers.get(referer, 0) + 1
            else:
                referrers['Direct'] = referrers.get('Direct', 0) + 1
        
        total = len(clicks)
        return {k: {'count': v, 'percentage': round(v/total*100, 1)} 
                for k, v in sorted(referrers.items(), key=lambda x: x[1], reverse=True)[:10]}
    
    def _empty_analytics(self) -> Dict[str, Any]:
        """Return empty analytics structure"""
        return {
            'link_id': None,
            'period_days': 0,
            'total_clicks': 0,
            'unique_clicks': 0,
            'click_through_rate': 0,
            'devices': {'types': {}, 'brands': {}},
            'geography': {'countries': {}, 'cities': {}},
            'browsers': {'browsers': {}, 'operating_systems': {}},
            'timeline': {'daily': {}, 'hourly': {}},
            'top_referrers': {}
        }
