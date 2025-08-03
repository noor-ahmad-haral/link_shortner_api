"""
Analytics module for advanced click tracking and device analytics
"""

from .models import LinkClick
from .parser import UserAgentParser, IPGeolocation
from .tracker import ClickTracker
from .routes import router as analytics_router

__all__ = [
    'LinkClick',
    'UserAgentParser', 
    'IPGeolocation',
    'ClickTracker',
    'analytics_router'
]
