"""
Intelligent Spitogatos Scraper with Advanced Anti-Detection
Enterprise-grade web scraping with rate limiting, session management, and error handling
"""

import asyncio
import aiohttp
import time
import random
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json

from config import config
from utils import (
    PropertyData, CacheManager, PerformanceMonitor, 
    safe_sleep, generate_property_id
)

@dataclass
class SearchParams:
    """Search parameters for property queries"""
    location: str
    property_type: str = "apartment"
    transaction_type: str = "sale"
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_sqm: Optional[int] = None
    max_sqm: Optional[int] = None
    energy_class: Optional[str] = None
    page: int = 1

@dataclass
class ScrapingSession:
    """Session data for web scraping"""
    session: aiohttp.ClientSession
    user_agent: str
    request_count: int = 0
    created_at: datetime = None
    last_request: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class IntelligentSpitogatosScraper:
    """Advanced scraper with intelligent rate limiting and session management"""
    
    def __init__(self):
        self.config = config
        self.cache = CacheManager()
        self.performance_monitor = PerformanceMonitor()
        self.user_agent = UserAgent()
        
        # Session management
        self.sessions: List[ScrapingSession] = []
        self.session_index = 0
        self.total_requests = 0
        
        # Rate limiting state
        self.last_request_time = 0
        self.consecutive_errors = 0
        self.blocked_until = None
        
        # Discovered URLs and properties
        self.discovered_urls: Set[str] = set()
        self.scraped_properties: Dict[str, PropertyData] = {}
        
        # Statistics
        self.stats = {
            'requests_made': 0,
            'properties_found': 0,
            'cache_hits': 0,
            'errors': 0,
            'session_rotations': 0
        }
        
        logging.info("Intelligent Spitogatos Scraper initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._initialize_sessions()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._cleanup_sessions()
        
    async def _initialize_sessions(self) -> None:
        """Initialize multiple scraping sessions"""
        for i in range(self.config.SCRAPING.max_concurrent_requests):
            user_agent = random.choice(self.config.USER_AGENTS)
            
            timeout = aiohttp.ClientTimeout(total=self.config.SCRAPING.request_timeout)
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=2)
            
            session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={'User-Agent': user_agent}
            )
            
            scraping_session = ScrapingSession(
                session=session,
                user_agent=user_agent
            )
            
            self.sessions.append(scraping_session)
            
        logging.info(f"Initialized {len(self.sessions)} scraping sessions")
    
    async def _cleanup_sessions(self) -> None:
        """Cleanup all sessions"""
        for scraping_session in self.sessions:
            await scraping_session.session.close()
        self.sessions.clear()
        
    def _get_next_session(self) -> ScrapingSession:
        """Get next session in rotation"""
        session = self.sessions[self.session_index]
        self.session_index = (self.session_index + 1) % len(self.sessions)
        
        # Check if session needs rotation
        if session.request_count >= self.config.SCRAPING.session_rotation_frequency:
            self.stats['session_rotations'] += 1
            logging.info(f"Rotating session after {session.request_count} requests")
        
        return session
    
    async def _apply_rate_limiting(self) -> None:
        """Apply intelligent rate limiting"""
        if self.blocked_until and datetime.now() < self.blocked_until:
            wait_time = (self.blocked_until - datetime.now()).total_seconds()
            logging.warning(f"Scraper blocked, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            self.blocked_until = None
            
        # Calculate dynamic delay based on recent errors
        base_delay = self.config.RATE_LIMITS.base_delay_seconds
        error_multiplier = 1 + (self.consecutive_errors * 0.5)
        
        delay = base_delay * error_multiplier
        jitter = random.uniform(0, self.config.RATE_LIMITS.random_jitter_max)
        
        total_delay = min(delay + jitter, self.config.RATE_LIMITS.max_delay)
        
        # Ensure minimum time between requests
        time_since_last = time.time() - self.last_request_time
        if time_since_last < total_delay:
            await asyncio.sleep(total_delay - time_since_last)
            
        self.last_request_time = time.time()
    
    async def _make_request(self, url: str, params: Optional[Dict] = None, 
                          retry_count: int = 0) -> Optional[str]:
        """Make robust HTTP request with error handling"""
        
        # Check cache first
        cache_key = f"{url}_{str(params or {})}"
        cached_content = self.cache.get(cache_key)
        if cached_content:
            self.stats['cache_hits'] += 1
            return cached_content
        
        # Apply rate limiting
        await self._apply_rate_limiting()
        
        # Get session for request
        scraping_session = self._get_next_session()
        
        try:
            self.performance_monitor.start_timer('request')
            
            async with scraping_session.session.get(url, params=params) as response:
                scraping_session.request_count += 1
                scraping_session.last_request = datetime.now()
                self.stats['requests_made'] += 1
                
                if response.status == 200:
                    content = await response.text()
                    
                    # Cache successful response
                    if self.config.SCRAPING.enable_caching:
                        self.cache.set(cache_key, content)
                    
                    self.consecutive_errors = 0
                    self.performance_monitor.end_timer('request')
                    
                    return content
                    
                elif response.status == 429:  # Rate limited
                    self.consecutive_errors += 1
                    retry_after = int(response.headers.get('Retry-After', 60))
                    self.blocked_until = datetime.now() + timedelta(seconds=retry_after)
                    
                    logging.warning(f"Rate limited (429), blocked for {retry_after}s")
                    
                elif response.status in [403, 404]:
                    logging.warning(f"Access denied or not found: {response.status} for {url}")
                    return None
                    
                else:
                    logging.warning(f"Unexpected status {response.status} for {url}")
                    
        except asyncio.TimeoutError:
            self.consecutive_errors += 1
            logging.warning(f"Timeout requesting {url}")
            
        except Exception as e:
            self.consecutive_errors += 1
            logging.error(f"Request error for {url}: {e}")
            
        finally:
            self.performance_monitor.end_timer('request')
        
        # Retry logic with exponential backoff
        if retry_count < self.config.RATE_LIMITS.max_retries:
            backoff = self.config.RATE_LIMITS.backoff_multiplier ** retry_count
            await asyncio.sleep(backoff)
            return await self._make_request(url, params, retry_count + 1)
            
        self.stats['errors'] += 1
        return None
    
    def _build_search_url(self, search_params: SearchParams) -> str:
        """Build search URL with parameters"""
        base_url = f"{self.config.SPITOGATOS_BASE_URL}/search"
        
        # Build query parameters
        params = {
            'location': search_params.location,
            'type': search_params.property_type,
            'transaction': search_params.transaction_type,
            'page': search_params.page
        }
        
        if search_params.min_price:
            params['price_from'] = search_params.min_price
        if search_params.max_price:
            params['price_to'] = search_params.max_price
        if search_params.min_sqm:
            params['sqm_from'] = search_params.min_sqm
        if search_params.max_sqm:
            params['sqm_to'] = search_params.max_sqm
        if search_params.energy_class:
            params['energy_class'] = search_params.energy_class
            
        # Convert to URL
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
    
    def _parse_property_listing(self, html: str, source_url: str) -> List[PropertyData]:
        """Parse property listings from search results HTML"""
        properties = []
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Find property listings (adjust selectors based on actual HTML structure)
            property_elements = soup.find_all('div', class_=['property-item', 'listing-item'])
            
            for element in property_elements:
                try:
                    property_data = self._extract_property_data(element, source_url)
                    if property_data:
                        properties.append(property_data)
                        self.stats['properties_found'] += 1
                        
                except Exception as e:
                    logging.warning(f"Error parsing property element: {e}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error parsing property listings: {e}")
            
        return properties
    
    def _extract_property_data(self, element, source_url: str) -> Optional[PropertyData]:
        """Extract property data from HTML element"""
        try:
            # Extract URL
            link_elem = element.find('a', href=True)
            if not link_elem:
                return None
                
            property_url = urljoin(self.config.SPITOGATOS_BASE_URL, link_elem['href'])
            
            # Extract title
            title_elem = element.find(['h2', 'h3', 'h4'], class_=['title', 'property-title'])
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract address
            address_elem = element.find(['div', 'span'], class_=['address', 'location'])
            address = address_elem.get_text(strip=True) if address_elem else ""
            
            # Extract price
            price_elem = element.find(['div', 'span'], class_=['price', 'cost'])
            price_text = price_elem.get_text(strip=True) if price_elem else ""
            price = self._extract_price(price_text)
            
            # Extract square meters
            sqm_elem = element.find(['div', 'span'], text=re.compile(r'τ\.μ\.|m²'))
            sqm_text = sqm_elem.get_text(strip=True) if sqm_elem else ""
            sqm = self._extract_sqm(sqm_text)
            
            # Extract energy class
            energy_elem = element.find(['div', 'span'], class_=['energy', 'energy-class'])
            energy_class = energy_elem.get_text(strip=True) if energy_elem else ""
            
            # Extract images
            img_elements = element.find_all('img', src=True)
            images = [img['src'] for img in img_elements if img.get('src')]
            
            # Generate unique ID
            property_id = generate_property_id(property_url, address)
            
            # Create property data object
            property_data = PropertyData(
                id=property_id,
                url=property_url,
                title=title,
                address=address,
                price=price,
                sqm=sqm,
                energy_class=energy_class.upper() if energy_class else None,
                floor=None,  # Will be extracted from detail page
                rooms=None,  # Will be extracted from detail page
                latitude=None,
                longitude=None,
                description="",  # Will be extracted from detail page
                images=images,
                scraped_at=datetime.now(),
                confidence_score=0.0,  # Will be calculated
                validation_flags=[],
                source="spitogatos_search"
            )
            
            return property_data
            
        except Exception as e:
            logging.warning(f"Error extracting property data: {e}")
            return None
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extract price from text"""
        if not price_text:
            return None
            
        # Remove currency symbols and clean up
        cleaned = re.sub(r'[€,.]', '', price_text)
        match = re.search(r'(\d+)', cleaned)
        
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
                
        return None
    
    def _extract_sqm(self, sqm_text: str) -> Optional[float]:
        """Extract square meters from text"""
        if not sqm_text:
            return None
            
        match = re.search(r'(\d+(?:\.\d+)?)', sqm_text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
                
        return None
    
    async def search_properties(self, search_params: SearchParams, 
                              max_pages: int = 10) -> List[PropertyData]:
        """Search for properties with given parameters"""
        all_properties = []
        
        logging.info(f"Starting property search for {search_params.location}")
        
        for page in range(1, max_pages + 1):
            search_params.page = page
            search_url = self._build_search_url(search_params)
            
            logging.info(f"Searching page {page}: {search_url}")
            
            html_content = await self._make_request(search_url)
            if not html_content:
                logging.warning(f"Failed to fetch page {page}")
                continue
                
            # Parse properties from this page
            page_properties = self._parse_property_listing(html_content, search_url)
            
            if not page_properties:
                logging.info(f"No properties found on page {page}, stopping search")
                break
                
            all_properties.extend(page_properties)
            
            # Add discovered URLs
            for prop in page_properties:
                self.discovered_urls.add(prop.url)
                self.scraped_properties[prop.id] = prop
                
            logging.info(f"Found {len(page_properties)} properties on page {page}")
            
            # Small delay between pages
            await asyncio.sleep(1)
            
        logging.info(f"Search completed. Found {len(all_properties)} total properties")
        return all_properties
    
    async def scrape_property_details(self, property_url: str) -> Optional[PropertyData]:
        """Scrape detailed information for a specific property"""
        
        html_content = await self._make_request(property_url)
        if not html_content:
            return None
            
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Extract detailed information
            # (Implementation would depend on actual HTML structure)
            
            # This is a placeholder - actual implementation would parse
            # detailed property information from the property detail page
            
            return None  # Placeholder
            
        except Exception as e:
            logging.error(f"Error scraping property details from {property_url}: {e}")
            return None
    
    async def comprehensive_area_search(self, area_name: str, 
                                      streets: List[Dict[str, Any]]) -> List[PropertyData]:
        """Perform comprehensive search for an area using multiple strategies"""
        all_properties = []
        
        logging.info(f"Starting comprehensive search for {area_name}")
        
        # Strategy 1: Systematic street search
        for street_info in streets:
            street_name = street_info['name']
            address_range = street_info.get('range', '1-100')
            priority = street_info.get('priority', 1)
            
            # Search specific street
            search_params = SearchParams(
                location=f"{street_name}, Athens",
                property_type="apartment"
            )
            
            properties = await self.search_properties(search_params, max_pages=15)
            all_properties.extend(properties)
            
            logging.info(f"Found {len(properties)} properties on {street_name}")
            
            # Delay between streets based on priority
            delay = 2.0 if priority == 1 else 4.0
            await asyncio.sleep(delay)
        
        # Strategy 2: General area search
        area_search_params = SearchParams(
            location=f"{area_name}, Athens",
            property_type="apartment"
        )
        
        area_properties = await self.search_properties(area_search_params, max_pages=20)
        all_properties.extend(area_properties)
        
        # Remove duplicates based on property ID
        unique_properties = {}
        for prop in all_properties:
            if prop.id not in unique_properties:
                unique_properties[prop.id] = prop
                
        final_properties = list(unique_properties.values())
        
        logging.info(f"Comprehensive search for {area_name} completed. "
                    f"Found {len(final_properties)} unique properties")
        
        return final_properties
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        return {
            **self.stats,
            'discovered_urls': len(self.discovered_urls),
            'scraped_properties': len(self.scraped_properties),
            'performance_metrics': {
                op: self.performance_monitor.get_stats(op) 
                for op in ['request']
            },
            'session_info': {
                'active_sessions': len(self.sessions),
                'total_session_requests': sum(s.request_count for s in self.sessions)
            }
        }
    
    def log_statistics(self) -> None:
        """Log comprehensive statistics"""
        stats = self.get_statistics()
        
        logging.info("=== Scraping Statistics ===")
        logging.info(f"Requests made: {stats['requests_made']}")
        logging.info(f"Properties found: {stats['properties_found']}")
        logging.info(f"Cache hits: {stats['cache_hits']}")
        logging.info(f"Errors: {stats['errors']}")
        logging.info(f"Session rotations: {stats['session_rotations']}")
        logging.info(f"Discovered URLs: {stats['discovered_urls']}")
        
        # Log performance metrics
        self.performance_monitor.log_summary()

# Example usage and testing
async def test_scraper():
    """Test the scraper functionality"""
    async with IntelligentSpitogatosScraper() as scraper:
        # Test search
        search_params = SearchParams(
            location="Kolonaki, Athens",
            property_type="apartment"
        )
        
        properties = await scraper.search_properties(search_params, max_pages=3)
        
        print(f"Found {len(properties)} properties")
        for prop in properties[:5]:  # Show first 5
            print(f"- {prop.title[:50]}... | {prop.address} | €{prop.price}")
            
        scraper.log_statistics()

if __name__ == "__main__":
    asyncio.run(test_scraper())