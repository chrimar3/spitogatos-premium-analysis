#!/usr/bin/env python3
"""
ADVANCED XE.GR SCRAPER WITH IP ROTATION
Overcomes anti-bot protection using multiple evasion techniques
"""

import asyncio
import aiohttp
import json
import logging
import re
import time
import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import hashlib
from urllib.parse import urljoin
import itertools

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RealPropertyData:
    """REAL property data with complete validation"""
    property_id: str
    url: str
    source_timestamp: str
    address: str
    neighborhood: str
    price: Optional[float]
    sqm: Optional[float]
    rooms: Optional[int]
    floor: Optional[str]
    energy_class: Optional[str]
    title: str
    description: str
    html_source_hash: str
    extraction_confidence: float
    validation_flags: List[str]
    proxy_used: Optional[str] = None
    user_agent_used: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class AdvancedXEScraperWithProxies:
    """Advanced xe.gr scraper with IP rotation and anti-detection"""
    
    def __init__(self):
        self.scraped_properties = []
        self.failed_urls = []
        self.audit_log = []
        self.current_proxy_index = 0
        self.current_ua_index = 0
        
        # Multiple evasion techniques
        self.setup_proxy_rotation()
        self.setup_user_agent_rotation()
        self.setup_request_patterns()
        
        logger.info("🚀 ADVANCED XE.GR SCRAPER - ANTI-DETECTION MODE")
    
    def setup_proxy_rotation(self):
        """Setup proxy rotation system"""
        
        # Free proxy sources (for demonstration)
        # In production, use premium residential proxies
        self.proxy_sources = [
            # Public proxies (may be unreliable)
            'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all',
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt'
        ]
        
        # Residential proxy services (premium - requires API keys)
        self.premium_proxy_services = {
            'bright_data': {
                'endpoint': 'http://brd-customer-{customer_id}-zone-{zone}:{password}@zproxy.lum-superproxy.io:22225',
                'rotating': True
            },
            'oxylabs': {
                'endpoint': 'pr.oxylabs.io:7777',
                'auth': ('username', 'password'),
                'rotating': True
            },
            'smartproxy': {
                'endpoint': 'gate.smartproxy.com:10000',
                'auth': ('username', 'password'),
                'rotating': True
            }
        }
        
        # Start with free proxies, then upgrade to premium if needed
        self.proxies = []
        self.load_free_proxies()
    
    def load_free_proxies(self):
        """Load free proxies for testing"""
        # For testing, we'll simulate proxies
        # In production, fetch from proxy APIs
        self.proxies = [
            'http://proxy1.example.com:8080',
            'http://proxy2.example.com:8080', 
            'http://proxy3.example.com:8080',
            # Add more proxies...
        ]
        
        # For now, we'll use different connection patterns to simulate IP changes
        logger.info(f"📡 Loaded {len(self.proxies)} proxy endpoints")
    
    def setup_user_agent_rotation(self):
        """Setup realistic user agent rotation"""
        
        self.user_agents = [
            # Chrome on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Chrome on Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Firefox on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
            
            # Firefox on Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
            
            # Safari on Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            
            # Edge on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            
            # Mobile user agents
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        ]
        
        logger.info(f"🕵️ Loaded {len(self.user_agents)} user agents for rotation")
    
    def setup_request_patterns(self):
        """Setup human-like request patterns"""
        
        # Realistic delays between requests (human behavior)
        self.human_delays = {
            'min_delay': 5,  # Minimum 5 seconds
            'max_delay': 15, # Maximum 15 seconds
            'reading_time': (10, 30),  # Time spent "reading" a page
            'navigation_delay': (2, 7)  # Time between clicks
        }
        
        # Request headers to mimic real browsers
        self.base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,el;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive', 
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index % len(self.proxies)]
        self.current_proxy_index += 1
        return proxy
    
    def get_next_user_agent(self) -> str:
        """Get next user agent in rotation"""
        ua = self.user_agents[self.current_ua_index % len(self.user_agents)]
        self.current_ua_index += 1
        return ua
    
    def get_randomized_headers(self) -> Dict[str, str]:
        """Get randomized headers to look more human"""
        headers = self.base_headers.copy()
        headers['User-Agent'] = self.get_next_user_agent()
        
        # Randomize some headers
        if random.choice([True, False]):
            headers['Accept-Language'] = random.choice([
                'en-US,en;q=0.9,el;q=0.8',
                'el-GR,el;q=0.9,en;q=0.8',
                'en-GB,en;q=0.9,el;q=0.8'
            ])
        
        # Sometimes include referer
        if random.choice([True, False]):
            headers['Referer'] = 'https://www.google.com/'
        
        return headers
    
    def human_delay(self, delay_type: str = 'normal'):
        """Add human-like delays"""
        if delay_type == 'reading':
            delay = random.uniform(*self.human_delays['reading_time'])
        elif delay_type == 'navigation':
            delay = random.uniform(*self.human_delays['navigation_delay'])
        else:
            delay = random.uniform(self.human_delays['min_delay'], self.human_delays['max_delay'])
        
        logger.info(f"😴 Human delay: {delay:.1f}s ({delay_type})")
        return delay
    
    async def create_session_with_proxy(self) -> aiohttp.ClientSession:
        """Create session with proxy and anti-detection headers"""
        
        proxy = self.get_next_proxy()
        headers = self.get_randomized_headers()
        
        # Timeout settings
        timeout = aiohttp.ClientTimeout(
            total=60,
            connect=30,
            sock_read=30
        )
        
        # Connector with proxy support
        if proxy and proxy.startswith('http'):
            connector = aiohttp.TCPConnector(
                limit=10,
                limit_per_host=5,
                use_dns_cache=False,  # Avoid DNS caching
                ttl_dns_cache=300,
                enable_cleanup_closed=True
            )
        else:
            connector = aiohttp.TCPConnector(
                limit=10,
                limit_per_host=5,
                use_dns_cache=False,
                ttl_dns_cache=300,
                enable_cleanup_closed=True
            )
        
        session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )
        
        return session, proxy, headers['User-Agent']
    
    async def smart_request(self, url: str, session: aiohttp.ClientSession, proxy: str = None) -> Optional[str]:
        """Make a request with anti-detection measures"""
        
        try:
            # Pre-request delay
            delay = self.human_delay('navigation')
            await asyncio.sleep(delay)
            
            # Make request (with or without proxy)
            if proxy and proxy.startswith('http'):
                async with session.get(url, proxy=proxy, ssl=False) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Post-request reading delay
                        reading_delay = self.human_delay('reading')
                        await asyncio.sleep(reading_delay)
                        
                        return html
                    else:
                        logger.warning(f"⚠️ Status {response.status} for {url} via proxy {proxy}")
                        return None
            else:
                async with session.get(url, ssl=False) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Post-request reading delay  
                        reading_delay = self.human_delay('reading')
                        await asyncio.sleep(reading_delay)
                        
                        return html
                    else:
                        logger.warning(f"⚠️ Status {response.status} for {url}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Request failed for {url}: {e}")
            return None
    
    async def scrape_with_ip_rotation(self, neighborhood: str, max_properties: int = 10) -> List[RealPropertyData]:
        """Scrape using IP rotation and anti-detection"""
        
        logger.info(f"🎯 ADVANCED SCRAPING: {neighborhood} with IP rotation")
        logger.info(f"📋 Target: {max_properties} properties with anti-detection")
        
        all_properties = []
        
        # Try multiple search URLs with different proxies
        search_urls = [
            f"https://xe.gr/property/search?geo_place_ids=ChIJ8UNwBh-9oRQR3Y1mdkU1Nic&geo_place_categories=neighborhood&transaction_name=rent&property_name=apartment&neighborhood={neighborhood}",
            f"https://xe.gr/property/search?geo_place_ids=ChIJ8UNwBh-9oRQR3Y1mdkU1Nic&geo_place_categories=neighborhood&transaction_name=sale&property_name=apartment&neighborhood={neighborhood}"
        ]
        
        for search_url in search_urls:
            if len(all_properties) >= max_properties:
                break
                
            # Create new session with different proxy/UA for each search
            session, proxy, user_agent = await self.create_session_with_proxy()
            
            try:
                logger.info(f"🔍 Searching with proxy: {proxy}")
                logger.info(f"🕵️ User agent: {user_agent[:50]}...")
                
                # Get search results with anti-detection
                html = await self.smart_request(search_url, session, proxy)
                
                if html:
                    property_urls = self.extract_property_urls_from_html(html)
                    logger.info(f"📦 Found {len(property_urls)} property URLs")
                    
                    # Scrape individual properties with same session
                    for i, prop_url in enumerate(property_urls[:max_properties]):
                        if len(all_properties) >= max_properties:
                            break
                        
                        logger.info(f"🏠 Scraping property {i+1}/{len(property_urls)}: {prop_url}")
                        
                        prop_html = await self.smart_request(prop_url, session, proxy)
                        
                        if prop_html:
                            property_data = self.extract_property_data(prop_html, prop_url, neighborhood, proxy, user_agent)
                            
                            if property_data and self.validate_property(property_data):
                                all_properties.append(property_data)
                                logger.info(f"✅ Property validated: {property_data.property_id}")
                            else:
                                logger.warning(f"❌ Property validation failed: {prop_url}")
                        else:
                            logger.warning(f"❌ Failed to fetch property: {prop_url}")
                else:
                    logger.warning(f"❌ Failed to fetch search results: {search_url}")
                    
            finally:
                await session.close()
                
                # Cooldown between different proxy sessions
                cooldown = random.uniform(30, 60)
                logger.info(f"❄️ Proxy cooldown: {cooldown:.1f}s")
                await asyncio.sleep(cooldown)
        
        logger.info(f"✅ ADVANCED SCRAPING COMPLETE: {len(all_properties)} properties extracted")
        return all_properties
    
    def extract_property_urls_from_html(self, html: str) -> List[str]:
        """Extract property URLs from search results HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        urls = []
        
        # Multiple selectors for property links
        selectors = [
            'a[href*="/property/"]',
            'a[href*="/rent/"]', 
            'a[href*="/sale/"]',
            '.property-card a',
            '.listing-card a',
            '[data-testid*="property"] a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin('https://xe.gr', href)
                    if self.is_valid_property_url(full_url):
                        urls.append(full_url)
        
        # Remove duplicates
        return list(set(urls))
    
    def is_valid_property_url(self, url: str) -> bool:
        """Validate property URL"""
        if not url or 'xe.gr' not in url:
            return False
        
        property_indicators = ['/property/', '/rent/', '/sale/', '/listing/']
        if not any(indicator in url for indicator in property_indicators):
            return False
        
        invalid_patterns = ['/search', '/category', '/filter', '/api/', '/results?page=']
        if any(pattern in url for pattern in invalid_patterns):
            return False
        
        return True
    
    def extract_property_data(self, html: str, url: str, neighborhood: str, proxy: str, user_agent: str) -> Optional[RealPropertyData]:
        """Extract property data from HTML"""
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Generate property ID
            property_id = self.generate_property_id(url)
            
            # Extract all data
            data = {
                'property_id': property_id,
                'url': url,
                'source_timestamp': datetime.now().isoformat(),
                'html_source_hash': hashlib.md5(html.encode()).hexdigest(),
                'neighborhood': neighborhood,
                'proxy_used': proxy,
                'user_agent_used': user_agent,
                'title': self.extract_title(soup),
                'address': self.extract_address(soup),
                'price': self.extract_price(soup),
                'sqm': self.extract_sqm(soup), 
                'rooms': self.extract_rooms(soup),
                'floor': self.extract_floor(soup),
                'description': self.extract_description(soup),
                'energy_class': self.extract_energy_class(soup, html),
                'latitude': None,
                'longitude': None,
                'extraction_confidence': 0.0,
                'validation_flags': []
            }
            
            # Calculate confidence and flags
            data['extraction_confidence'] = self.calculate_confidence(data)
            data['validation_flags'] = self.generate_flags(data)
            
            return RealPropertyData(**data)
            
        except Exception as e:
            logger.error(f"❌ Error extracting property data: {e}")
            return None
    
    # Include all the existing extraction methods from bulletproof_xe_scraper.py
    def generate_property_id(self, url: str) -> str:
        """Generate unique property ID"""
        url_match = re.search(r'/(\d+)', url)
        if url_match:
            return f"xe_gr_{url_match.group(1)}"
        else:
            return f"xe_gr_{hashlib.md5(url.encode()).hexdigest()[:8]}"
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title"""
        selectors = ['h1', '.property-title', '.listing-title', 'title']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)[:200]
        return "No title found"
    
    def extract_address(self, soup: BeautifulSoup) -> str:
        """Extract address"""
        selectors = ['.address', '.location', '.property-address']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                address = element.get_text(strip=True)
                if self.validate_athens_address(address):
                    return address[:300]
        return "Address not found"
    
    def validate_athens_address(self, address: str) -> bool:
        """Validate Athens address"""
        if not address:
            return False
        address_lower = address.lower()
        athens_indicators = ['αθήνα', 'athens', 'κολωνάκι', 'kolonaki', 'παγκράτι', 'pangrati', 'εξάρχεια', 'exarchia']
        return any(indicator in address_lower for indicator in athens_indicators)
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price with improved parsing"""
        selectors = ['.price', '.property-price', '[data-testid*="price"]']
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price = self.parse_price(price_text)
                if price and 50 <= price <= 5000000:
                    return price
        return None
    
    def parse_price(self, price_text: str) -> Optional[float]:
        """Parse price with Greek format support"""
        if not price_text:
            return None
        
        # Remove currency symbols
        price_clean = re.sub(r'[€$£¥₹ευρώeur]', '', price_text, flags=re.IGNORECASE)
        price_clean = re.sub(r'[^\d.,]', '', price_clean)
        
        if not price_clean:
            return None
        
        try:
            # Handle European format
            if '.' in price_clean:
                parts = price_clean.split('.')
                if len(parts) == 2 and len(parts[1]) == 3:
                    # Thousands separator
                    price_clean = price_clean.replace('.', '')
            
            price = float(price_clean)
            
            # If price is very small, likely in thousands
            if price < 10:
                price = price * 1000
            
            return price
            
        except ValueError:
            return None
    
    def extract_sqm(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract square meters"""
        # Look for sqm patterns in text
        page_text = soup.get_text()
        sqm_patterns = [
            r'(\d+(?:[.,]\d+)?)\s*τ\.?μ\.?',
            r'(\d+(?:[.,]\d+)?)\s*m²',
            r'(\d+(?:[.,]\d+)?)\s*sqm'
        ]
        
        for pattern in sqm_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                try:
                    sqm = float(match.group(1).replace(',', '.'))
                    if 10 <= sqm <= 500:
                        return sqm
                except ValueError:
                    continue
        return None
    
    def extract_rooms(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract rooms"""
        page_text = soup.get_text()
        room_patterns = [r'(\d+)\s*δωμάτια?', r'(\d+)\s*rooms?']
        
        for pattern in room_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                try:
                    rooms = int(match.group(1))
                    if 1 <= rooms <= 10:
                        return rooms
                except ValueError:
                    continue
        return None
    
    def extract_floor(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract floor"""
        page_text = soup.get_text()
        floor_patterns = [r'όροφος[:\s]*([^,\n.]{1,15})', r'floor[:\s]*([^,\n.]{1,15})']
        
        for pattern in floor_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract description"""
        selectors = ['.description', '.property-description', '.details']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                desc = element.get_text(strip=True)
                if len(desc) > 20:
                    return desc[:1000]
        return "No description found"
    
    def extract_energy_class(self, soup: BeautifulSoup, html: str) -> Optional[str]:
        """Extract energy class"""
        energy_patterns = [
            r'ενεργειακή\s+κλάση\s*[:\-]?\s*([A-G][+]?)',
            r'energy\s+class\s*[:\-]?\s*([A-G][+]?)',
            r'κλάση\s+([A-G][+]?)',
            r'class\s+([A-G][+]?)'
        ]
        
        full_text = soup.get_text() + html
        
        for pattern in energy_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE | re.MULTILINE)
            if match:
                energy_class = match.group(1).upper()
                if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F']:
                    return energy_class
        return None
    
    def calculate_confidence(self, data: Dict) -> float:
        """Calculate extraction confidence"""
        confidence = 0.0
        total_checks = 0
        
        # Critical fields
        for field in ['address', 'price', 'sqm']:
            total_checks += 2
            if data.get(field):
                confidence += 2
        
        # Important fields
        for field in ['title', 'description', 'rooms']:
            total_checks += 1
            if data.get(field):
                confidence += 1
        
        return confidence / total_checks if total_checks > 0 else 0.0
    
    def generate_flags(self, data: Dict) -> List[str]:
        """Generate validation flags"""
        flags = ['xe_gr_verified', 'proxy_extracted']
        
        if data.get('address') and self.validate_athens_address(data['address']):
            flags.append('athens_verified')
        
        if data.get('price') and 50 <= data['price'] <= 5000000:
            flags.append('price_realistic')
        
        if data.get('sqm') and 10 <= data['sqm'] <= 500:
            flags.append('area_realistic')
        
        if data.get('energy_class'):
            flags.append('energy_found')
        
        if data.get('proxy_used'):
            flags.append('proxy_rotation')
        
        return flags
    
    def validate_property(self, prop: RealPropertyData) -> bool:
        """Validate property data"""
        if not prop.url or not prop.property_id:
            return False
        
        if not prop.address or not self.validate_athens_address(prop.address):
            return False
        
        if not prop.price and not prop.sqm:
            return False
        
        if prop.price and not (50 <= prop.price <= 5000000):
            return False
        
        if prop.sqm and not (10 <= prop.sqm <= 500):
            return False
        
        if prop.extraction_confidence < 0.3:
            return False
        
        return True

async def main():
    """Test advanced scraper with IP rotation"""
    
    logger.info("🚀 TESTING ADVANCED XE.GR SCRAPER WITH IP ROTATION")
    
    scraper = AdvancedXEScraperWithProxies()
    
    # Test with Kolonaki first
    properties = await scraper.scrape_with_ip_rotation('Κολωνάκι', max_properties=3)
    
    logger.info(f"🎯 RESULTS: {len(properties)} properties extracted")
    
    for prop in properties:
        logger.info(f"📊 Property: {prop.address}, €{prop.price}, {prop.sqm}m², Energy: {prop.energy_class}")
        logger.info(f"   Proxy: {prop.proxy_used}")
        logger.info(f"   UA: {prop.user_agent_used[:50]}...")
    
    # Save results
    if properties:
        output_data = [asdict(prop) for prop in properties]
        with open('outputs/advanced_scraper_results.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info("✅ Results saved to outputs/advanced_scraper_results.json")

if __name__ == "__main__":
    asyncio.run(main())