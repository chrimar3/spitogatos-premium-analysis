"""
Professional Spitogatos Scraper with Playwright and Advanced Anti-Detection
Enterprise-grade browser automation that bypasses modern bot detection
"""

import asyncio
import time
import random
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import re
import json
import os

from playwright.async_api import async_playwright, Page, BrowserContext, Browser
from bs4 import BeautifulSoup
import undetected_playwright as up

from config import config
from utils import PropertyData, generate_property_id

@dataclass
class BrowserSession:
    """Browser session with anti-detection features"""
    browser: Browser
    context: BrowserContext
    page: Page
    user_agent: str
    proxy: Optional[str] = None
    request_count: int = 0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class ProfessionalSpitogatosScraper:
    """Advanced Playwright-based scraper with professional anti-detection techniques"""
    
    def __init__(self):
        self.config = config
        self.sessions: List[BrowserSession] = []
        self.session_index = 0
        
        # Advanced fingerprinting
        self.greek_user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # Residential proxies (demo - replace with real proxies)
        self.proxies = [
            None,  # Direct connection
            # "http://user:pass@proxy1:port",
            # "http://user:pass@proxy2:port"
        ]
        
        # Human behavior patterns
        self.scroll_patterns = [
            {"delta_y": 300, "delay": 1.2},
            {"delta_y": 150, "delay": 0.8},
            {"delta_y": 450, "delay": 2.1}
        ]
        
        # Statistics
        self.stats = {
            'requests_made': 0,
            'properties_found': 0,
            'errors': 0,
            'session_rotations': 0,
            'blocks_detected': 0
        }
        
        logging.info("Professional Spitogatos Scraper initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._initialize_browser_sessions()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._cleanup_sessions()
    
    async def _initialize_browser_sessions(self) -> None:
        """Initialize multiple browser sessions with anti-detection"""
        self.playwright = await async_playwright().start()
        
        for i in range(min(3, len(self.proxies))):  # Max 3 sessions
            proxy = self.proxies[i] if i < len(self.proxies) else None
            user_agent = random.choice(self.greek_user_agents)
            
            # Launch browser with anti-detection
            browser = await self.playwright.chromium.launch(
                headless=True,  # Set to False for debugging
                args=[
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-ipc-flooding-protection',
                    '--disable-renderer-backgrounding',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-background-timer-throttling',
                    '--force-color-profile=srgb',
                    '--metrics-recording-only',
                    '--disable-background-networking',
                    '--disable-default-apps',
                    '--disable-extensions',
                    '--disable-sync',
                    '--disable-translate',
                    '--hide-scrollbars',
                    '--mute-audio',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            
            # Create context with Greek locale and realistic settings
            context_options = {
                'user_agent': user_agent,
                'locale': 'el-GR',
                'timezone_id': 'Europe/Athens',
                'viewport': {'width': 1920, 'height': 1080},
                'screen': {'width': 1920, 'height': 1080},
                'device_scale_factor': 1,
                'is_mobile': False,
                'has_touch': False,
                'extra_http_headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'max-age=0',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"macOS"'
                }
            }
            
            if proxy:
                context_options['proxy'] = {'server': proxy}
            
            context = await browser.new_context(**context_options)
            
            # Add stealth scripts to avoid detection
            await context.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Mock plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Mock languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['el-GR', 'el', 'en'],
                });
                
                // Mock connection
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 50,
                        downlink: 10
                    }),
                });
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            page = await context.new_page()
            
            # Set realistic viewport and simulate real browser behavior
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            session = BrowserSession(
                browser=browser,
                context=context,
                page=page,
                user_agent=user_agent,
                proxy=proxy
            )
            
            self.sessions.append(session)
            
        logging.info(f"Initialized {len(self.sessions)} professional browser sessions")
    
    async def _cleanup_sessions(self) -> None:
        """Cleanup all browser sessions"""
        for session in self.sessions:
            try:
                await session.context.close()
                await session.browser.close()
            except Exception as e:
                logging.warning(f"Error closing session: {e}")
        
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        
        self.sessions.clear()
    
    def _get_next_session(self) -> BrowserSession:
        """Get next session with intelligent rotation"""
        session = self.sessions[self.session_index]
        self.session_index = (self.session_index + 1) % len(self.sessions)
        
        # Rotate session if it's been used too much
        if session.request_count >= 50:  # Rotate after 50 requests
            self.stats['session_rotations'] += 1
            logging.info(f"Session rotation triggered after {session.request_count} requests")
        
        return session
    
    async def _simulate_human_behavior(self, page: Page) -> None:
        """Simulate realistic human browsing behavior"""
        # Random mouse movement
        await page.mouse.move(
            random.randint(100, 1800),
            random.randint(100, 900)
        )
        
        # Random delay
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Random scroll
        scroll = random.choice(self.scroll_patterns)
        await page.mouse.wheel(0, scroll["delta_y"])
        await asyncio.sleep(scroll["delay"])
        
        # Occasional random click (on safe elements)
        if random.random() < 0.1:  # 10% chance
            try:
                await page.click('body', timeout=1000)
            except:
                pass  # Ignore click failures
    
    async def _navigate_with_retry(self, page: Page, url: str, max_retries: int = 3) -> bool:
        """Navigate to URL with intelligent retry and error handling"""
        
        for attempt in range(max_retries):
            try:
                # Add random delay between attempts
                if attempt > 0:
                    delay = random.uniform(3, 8) * (attempt + 1)
                    logging.info(f"Retry {attempt + 1} after {delay:.1f}s delay")
                    await asyncio.sleep(delay)
                
                # Navigate with timeout
                response = await page.goto(
                    url,
                    wait_until='domcontentloaded',
                    timeout=30000
                )
                
                if response and response.status in [200, 301, 302]:
                    # Simulate human behavior after loading
                    await self._simulate_human_behavior(page)
                    return True
                elif response and response.status == 403:
                    logging.warning(f"403 Forbidden - possible bot detection")
                    self.stats['blocks_detected'] += 1
                    return False
                else:
                    logging.warning(f"Unexpected status {response.status if response else 'None'}")
                    
            except Exception as e:
                logging.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                if "net::ERR_NETWORK_CHANGED" in str(e):
                    await asyncio.sleep(5)  # Network issues need longer delay
        
        return False
    
    async def _extract_property_data(self, page: Page) -> List[PropertyData]:
        """Extract property data from search results page"""
        properties = []
        
        try:
            # Wait for content to load
            await page.wait_for_selector('[data-testid="ad-card"], .result-card, .listing-item', timeout=10000)
            
            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find property cards (multiple selectors for robustness)
            property_cards = soup.find_all([
                'div[data-testid="ad-card"]',
                'div[class*="result-card"]',
                'div[class*="listing-item"]',
                'article[class*="property"]'
            ])
            
            if not property_cards:
                # Fallback: look for any div with property-like content
                property_cards = soup.find_all('div', class_=re.compile(r'(card|listing|property|result)', re.I))
            
            logging.info(f"Found {len(property_cards)} potential property cards")
            
            for card in property_cards[:50]:  # Limit to first 50 to avoid memory issues
                try:
                    property_data = await self._parse_property_card(card)
                    if property_data:
                        properties.append(property_data)
                except Exception as e:
                    logging.debug(f"Error parsing property card: {e}")
                    continue
            
        except Exception as e:
            logging.warning(f"Error extracting properties: {e}")
        
        return properties
    
    async def _parse_property_card(self, card) -> Optional[PropertyData]:
        """Parse individual property card"""
        try:
            # Extract basic info with multiple fallbacks
            title_elem = card.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'(title|heading|name)', re.I))
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract price
            price_elem = card.find(['span', 'div', 'p'], class_=re.compile(r'(price|cost|euro)', re.I))
            price_text = price_elem.get_text(strip=True) if price_elem else ""
            price = self._extract_price(price_text)
            
            # Extract area/sqm
            area_elem = card.find(['span', 'div'], string=re.compile(r'\d+\s*m²', re.I))
            sqm_text = area_elem.get_text(strip=True) if area_elem else ""
            sqm = self._extract_number(sqm_text)
            
            # Extract URL
            link_elem = card.find('a', href=True)
            url = link_elem['href'] if link_elem else ""
            if url.startswith('/'):
                url = f"https://www.spitogatos.gr{url}"
            
            # Only create property if we have minimum required data
            if title and (price or sqm or url):
                return PropertyData(
                    id=generate_property_id(url or title),
                    url=url,
                    title=title,
                    address="",  # Will be extracted in detail scraping
                    price=price,
                    sqm=sqm,
                    energy_class=None,
                    floor=None,
                    rooms=None,
                    latitude=None,
                    longitude=None,
                    description="",
                    images=[],
                    scraped_at=datetime.now(),
                    confidence_score=0.8,
                    validation_flags=[]
                )
                
        except Exception as e:
            logging.debug(f"Error parsing property card: {e}")
        
        return None
    
    def _extract_price(self, text: str) -> Optional[int]:
        """Extract price from text"""
        if not text:
            return None
        
        # Remove common Greek price indicators and clean
        text = re.sub(r'[€$]', '', text)
        text = re.sub(r'[^\d.,]', '', text)
        
        # Find numbers
        numbers = re.findall(r'[\d.,]+', text)
        if numbers:
            try:
                # Handle European number format (e.g., 150.000,50)
                number_str = numbers[0].replace('.', '').replace(',', '.')
                return int(float(number_str))
            except:
                pass
        
        return None
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract numeric value from text"""
        if not text:
            return None
        
        numbers = re.findall(r'\d+', text)
        if numbers:
            try:
                return int(numbers[0])
            except:
                pass
        
        return None
    
    async def search_properties(self, location: str, max_pages: int = 10) -> List[PropertyData]:
        """Search properties for a specific location"""
        all_properties = []
        
        session = self._get_next_session()
        page = session.page
        
        try:
            # Build search URL
            base_url = "https://www.spitogatos.gr/search"
            search_params = f"?location={location}&type=apartment&transaction=sale"
            
            for page_num in range(1, max_pages + 1):
                url = f"{base_url}{search_params}&page={page_num}"
                
                logging.info(f"Scraping page {page_num}: {location}")
                
                # Navigate to search results
                if not await self._navigate_with_retry(page, url):
                    logging.warning(f"Failed to load page {page_num}")
                    continue
                
                # Extract properties from current page
                properties = await self._extract_property_data(page)
                
                if not properties:
                    logging.info(f"No properties found on page {page_num}, stopping")
                    break
                
                all_properties.extend(properties)
                session.request_count += 1
                self.stats['requests_made'] += 1
                self.stats['properties_found'] += len(properties)
                
                logging.info(f"Found {len(properties)} properties on page {page_num}")
                
                # Human-like delay between pages
                delay = random.uniform(3, 7)
                await asyncio.sleep(delay)
        
        except Exception as e:
            logging.error(f"Error searching properties for {location}: {e}")
        
        return all_properties
    
    async def comprehensive_area_search(self, area_name: str, streets: List[str]) -> List[PropertyData]:
        """Comprehensive search for an area including specific streets"""
        all_properties = []
        
        # Search main area
        logging.info(f"Searching main area: {area_name}")
        area_properties = await self.search_properties(area_name, max_pages=5)
        all_properties.extend(area_properties)
        
        # Search specific streets
        for street in streets[:3]:  # Limit to first 3 streets
            street_location = f"{street}, Athens"
            logging.info(f"Searching street: {street_location}")
            
            street_properties = await self.search_properties(street_location, max_pages=3)
            all_properties.extend(street_properties)
            
            # Delay between street searches
            await asyncio.sleep(random.uniform(5, 10))
        
        # Remove duplicates based on URL or title
        unique_properties = {}
        for prop in all_properties:
            key = prop.url or prop.title
            if key not in unique_properties:
                unique_properties[key] = prop
        
        final_properties = list(unique_properties.values())
        logging.info(f"Found {len(final_properties)} unique properties for {area_name}")
        
        return final_properties
    
    def log_statistics(self) -> None:
        """Log scraping statistics"""
        logging.info("=== Scraping Statistics ===")
        for key, value in self.stats.items():
            logging.info(f"{key}: {value}")
        logging.info("==========================")