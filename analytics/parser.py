"""
User Agent Parser and IP Geolocation utilities for analytics
"""

import re
import requests
from typing import Dict, Optional, Tuple
from user_agents import parse as parse_user_agent
import logging

logger = logging.getLogger(__name__)

class UserAgentParser:
    """
    Parse user agent strings to extract browser, OS, and device information
    """
    
    @staticmethod
    def parse(user_agent_string: str) -> Dict[str, Optional[str]]:
        """
        Parse user agent string and return detailed device information
        
        Args:
            user_agent_string: Raw user agent string from request headers
            
        Returns:
            Dictionary containing parsed device information
        """
        if not user_agent_string:
            return UserAgentParser._empty_result()
        
        try:
            # Use user-agents library for main parsing
            user_agent = parse_user_agent(user_agent_string)
            
            # Extract basic information
            result = {
                # Browser information
                'browser_name': user_agent.browser.family,
                'browser_version': user_agent.browser.version_string,
                'browser_family': user_agent.browser.family,
                
                # Operating System information
                'os_name': user_agent.os.family,
                'os_version': user_agent.os.version_string,
                'os_family': user_agent.os.family,
                
                # Device information
                'device_type': UserAgentParser._determine_device_type(user_agent),
                'device_brand': user_agent.device.brand or None,
                'device_model': user_agent.device.model or None,
                'device_family': user_agent.device.family or None,
                
                # Additional detection
                'is_mobile': user_agent.is_mobile,
                'is_tablet': user_agent.is_tablet,
                'is_pc': user_agent.is_pc,
                'is_bot': user_agent.is_bot,
            }
            
            # Enhanced device detection
            result.update(UserAgentParser._enhanced_device_detection(user_agent_string, result))
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing user agent: {e}")
            return UserAgentParser._empty_result()
    
    @staticmethod
    def _determine_device_type(user_agent) -> str:
        """Determine device type from user agent"""
        if user_agent.is_bot:
            return "Bot"
        elif user_agent.is_mobile:
            return "Mobile"
        elif user_agent.is_tablet:
            return "Tablet"
        elif user_agent.is_pc:
            return "Desktop"
        else:
            return "Unknown"
    
    @staticmethod
    def _enhanced_device_detection(user_agent_string: str, base_result: Dict) -> Dict:
        """Enhanced device detection using regex patterns"""
        enhanced = {}
        ua_lower = user_agent_string.lower()
        
        # Screen resolution detection
        screen_match = re.search(r'(\d{3,4})x(\d{3,4})', user_agent_string)
        if screen_match:
            enhanced['screen_resolution'] = f"{screen_match.group(1)}x{screen_match.group(2)}"
        
        # Enhanced mobile device detection
        if 'iphone' in ua_lower:
            enhanced['device_brand'] = 'Apple'
            enhanced['device_family'] = 'iPhone'
            # Extract iPhone model
            iphone_match = re.search(r'iphone\s*os\s*(\d+)_(\d+)', ua_lower)
            if iphone_match:
                enhanced['os_version'] = f"{iphone_match.group(1)}.{iphone_match.group(2)}"
        
        elif 'ipad' in ua_lower:
            enhanced['device_brand'] = 'Apple'
            enhanced['device_family'] = 'iPad'
            enhanced['device_type'] = 'Tablet'
        
        elif 'android' in ua_lower:
            enhanced['os_name'] = 'Android'
            # Extract Android version
            android_match = re.search(r'android\s+(\d+\.?\d*)', ua_lower)
            if android_match:
                enhanced['os_version'] = android_match.group(1)
            
            # Samsung detection
            if 'samsung' in ua_lower or 'sm-' in ua_lower:
                enhanced['device_brand'] = 'Samsung'
                samsung_match = re.search(r'sm-([a-z0-9]+)', ua_lower)
                if samsung_match:
                    enhanced['device_model'] = f"SM-{samsung_match.group(1).upper()}"
            
            # Google Pixel detection
            elif 'pixel' in ua_lower:
                enhanced['device_brand'] = 'Google'
                pixel_match = re.search(r'pixel\s*(\d+[a-z]*)', ua_lower)
                if pixel_match:
                    enhanced['device_model'] = f"Pixel {pixel_match.group(1)}"
        
        # Windows detection
        if 'windows' in ua_lower:
            if 'windows nt 10' in ua_lower:
                enhanced['os_name'] = 'Windows'
                enhanced['os_version'] = '10/11'
            elif 'windows nt 6.3' in ua_lower:
                enhanced['os_name'] = 'Windows'
                enhanced['os_version'] = '8.1'
            elif 'windows nt 6.1' in ua_lower:
                enhanced['os_name'] = 'Windows'
                enhanced['os_version'] = '7'
        
        return enhanced
    
    @staticmethod
    def _empty_result() -> Dict[str, Optional[str]]:
        """Return empty result structure"""
        return {
            'browser_name': None,
            'browser_version': None,
            'browser_family': None,
            'os_name': None,
            'os_version': None,
            'os_family': None,
            'device_type': 'Unknown',
            'device_brand': None,
            'device_model': None,
            'device_family': None,
            'is_mobile': False,
            'is_tablet': False,
            'is_pc': False,
            'is_bot': False,
        }


class IPGeolocation:
    """
    IP Geolocation service to determine visitor location
    """
    
    # Free geolocation APIs (with rate limits)
    FREE_APIS = [
        "http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,regionName,city,lat,lon,timezone,isp",
        "https://ipapi.co/{ip}/json/",
        "https://ipinfo.io/{ip}/json"
    ]
    
    @staticmethod
    def get_location(ip_address: str) -> Dict[str, Optional[str]]:
        """
        Get geographic information from IP address
        
        Args:
            ip_address: IP address to geolocate
            
        Returns:
            Dictionary containing location information
        """
        if not ip_address or ip_address in ['127.0.0.1', 'localhost', '::1']:
            return IPGeolocation._local_result()
        
        # Try each API until one works
        for api_url in IPGeolocation.FREE_APIS:
            try:
                result = IPGeolocation._try_api(api_url.format(ip=ip_address))
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Geolocation API failed: {e}")
                continue
        
        # If all APIs fail, return empty result
        logger.error(f"All geolocation APIs failed for IP: {ip_address}")
        return IPGeolocation._empty_location_result()
    
    @staticmethod
    def _try_api(url: str) -> Optional[Dict]:
        """Try a single geolocation API"""
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Normalize response based on API provider
            if 'ip-api.com' in url:
                return IPGeolocation._normalize_ip_api(data)
            elif 'ipapi.co' in url:
                return IPGeolocation._normalize_ipapi_co(data)
            elif 'ipinfo.io' in url:
                return IPGeolocation._normalize_ipinfo(data)
        
        return None
    
    @staticmethod
    def _normalize_ip_api(data: Dict) -> Dict:
        """Normalize ip-api.com response"""
        if data.get('status') == 'success':
            return {
                'country': data.get('country'),
                'country_code': data.get('countryCode'),
                'region': data.get('regionName'),
                'city': data.get('city'),
                'latitude': data.get('lat'),
                'longitude': data.get('lon'),
                'timezone': data.get('timezone'),
                'isp': data.get('isp'),
            }
        return {}
    
    @staticmethod
    def _normalize_ipapi_co(data: Dict) -> Dict:
        """Normalize ipapi.co response"""
        if not data.get('error'):
            return {
                'country': data.get('country_name'),
                'country_code': data.get('country_code'),
                'region': data.get('region'),
                'city': data.get('city'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'timezone': data.get('timezone'),
                'isp': data.get('org'),
            }
        return {}
    
    @staticmethod
    def _normalize_ipinfo(data: Dict) -> Dict:
        """Normalize ipinfo.io response"""
        if not data.get('error'):
            loc = data.get('loc', '').split(',')
            return {
                'country': data.get('country'),
                'country_code': data.get('country'),
                'region': data.get('region'),
                'city': data.get('city'),
                'latitude': float(loc[0]) if len(loc) > 0 and loc[0] else None,
                'longitude': float(loc[1]) if len(loc) > 1 and loc[1] else None,
                'timezone': data.get('timezone'),
                'isp': data.get('org'),
            }
        return {}
    
    @staticmethod
    def _local_result() -> Dict:
        """Return result for local/private IP addresses"""
        return {
            'country': 'Local',
            'country_code': 'LO',
            'region': 'Local',
            'city': 'Local',
            'latitude': None,
            'longitude': None,
            'timezone': None,
            'isp': 'Local Network',
        }
    
    @staticmethod
    def _empty_location_result() -> Dict:
        """Return empty location result"""
        return {
            'country': None,
            'country_code': None,
            'region': None,
            'city': None,
            'latitude': None,
            'longitude': None,
            'timezone': None,
            'isp': None,
        }
    
    @staticmethod
    def mask_ip(ip_address: str) -> str:
        """
        Mask IP address for privacy compliance
        Keeps network portion, masks host portion
        """
        if not ip_address:
            return None
        
        parts = ip_address.split('.')
        if len(parts) == 4:  # IPv4
            return f"{parts[0]}.{parts[1]}.{parts[2]}.xxx"
        elif ':' in ip_address:  # IPv6
            parts = ip_address.split(':')
            return ':'.join(parts[:4]) + ':xxxx:xxxx:xxxx:xxxx'
        
        return ip_address
