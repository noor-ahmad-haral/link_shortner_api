"""
Database models for advanced click tracking analytics
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class LinkClick(Base):
    """
    Detailed click tracking model for comprehensive analytics
    Stores information about each individual click on a short link
    """
    __tablename__ = "link_clicks"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(Integer, ForeignKey("short_links.id", ondelete="CASCADE"), nullable=False)
    
    # Network information
    ip_address = Column(String(45), nullable=True)  # Supports IPv4 and IPv6, can be masked
    user_agent = Column(Text, nullable=True)        # Full user agent string
    referer = Column(String(500), nullable=True)    # Source website
    
    # Geographic data
    country = Column(String(100), nullable=True)    # Country name
    country_code = Column(String(2), nullable=True) # ISO country code (US, IN, etc.)
    city = Column(String(100), nullable=True)       # City name
    region = Column(String(100), nullable=True)     # State/Province
    latitude = Column(Float, nullable=True)         # Geographic coordinates
    longitude = Column(Float, nullable=True)        # Geographic coordinates
    timezone = Column(String(50), nullable=True)    # Timezone (UTC+5:30, etc.)
    isp = Column(String(200), nullable=True)        # Internet Service Provider
    
    # Browser information
    browser_name = Column(String(100), nullable=True)    # Chrome, Firefox, Safari, Edge
    browser_version = Column(String(50), nullable=True)  # Version number
    browser_family = Column(String(50), nullable=True)   # Webkit, Gecko, etc.
    
    # Operating System information
    os_name = Column(String(100), nullable=True)         # Windows, macOS, iOS, Android, Linux
    os_version = Column(String(50), nullable=True)       # Version number
    os_family = Column(String(50), nullable=True)        # Windows NT, Unix, etc.
    
    # Device information
    device_type = Column(String(50), nullable=True)      # Desktop, Mobile, Tablet, Bot
    device_brand = Column(String(100), nullable=True)    # Apple, Samsung, Google, etc.
    device_model = Column(String(100), nullable=True)    # iPhone 14, Galaxy S23, etc.
    device_family = Column(String(100), nullable=True)   # iPhone, Galaxy, Pixel, etc.
    
    # Screen and technical details
    screen_resolution = Column(String(20), nullable=True) # 1920x1080, 414x896, etc.
    color_depth = Column(Integer, nullable=True)          # 24, 32 bit color
    pixel_ratio = Column(Float, nullable=True)            # Device pixel ratio
    
    # Behavioral tracking
    is_unique = Column(Boolean, default=False, nullable=False)  # First time visitor from this IP/browser
    is_bot = Column(Boolean, default=False, nullable=False)     # Detected bot/crawler
    session_id = Column(String(100), nullable=True)            # Session identifier for same visitor
    
    # Timestamps
    clicked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)  # When analytics were processed
    
    # Relationship back to the short link
    link = relationship("ShortLink", back_populates="clicks")
    
    def __repr__(self):
        return f"<LinkClick(id={self.id}, link_id={self.link_id}, device={self.device_type}, browser={self.browser_name})>"
    
    @property
    def device_info(self):
        """Combined device information string"""
        parts = []
        if self.device_brand:
            parts.append(self.device_brand)
        if self.device_model:
            parts.append(self.device_model)
        if self.device_type:
            parts.append(f"({self.device_type})")
        return " ".join(parts) if parts else "Unknown Device"
    
    @property
    def browser_info(self):
        """Combined browser information string"""
        if self.browser_name and self.browser_version:
            return f"{self.browser_name} {self.browser_version}"
        elif self.browser_name:
            return self.browser_name
        return "Unknown Browser"
    
    @property
    def os_info(self):
        """Combined operating system information string"""
        if self.os_name and self.os_version:
            return f"{self.os_name} {self.os_version}"
        elif self.os_name:
            return self.os_name
        return "Unknown OS"
    
    @property
    def location_info(self):
        """Combined location information string"""
        parts = []
        if self.city:
            parts.append(self.city)
        if self.region:
            parts.append(self.region)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts) if parts else "Unknown Location"
