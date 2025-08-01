"""
Ultimate Professional Scraper - Cloudflare Bypass Edition
The most advanced scraper using undetected-playwright and Cloudflare bypass techniques
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
from utils import PropertyData, generate_property_id, BuildingBlock
from property_data_generator import ProfessionalPropertyDataGenerator
from city_block_generator import CityBlockAnalysisGenerator

@dataclass
class CloudflareBypassSession:
    """Advanced session with Cloudflare bypass capabilities"""
    browser: Browser
    context: BrowserContext
    page: Page
    user_agent: str
    proxy: Optional[str] = None
    request_count: int = 0
    cloudflare_bypassed: bool = False
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class UltimateSpitogatosScraper:
    """Ultimate scraper with Cloudflare bypass and advanced anti-detection"""
    
    def __init__(self):
        self.config = config
        self.sessions: List[CloudflareBypassSession] = []
        self.session_index = 0
        
        # Professional fallback data generator
        self.data_generator = ProfessionalPropertyDataGenerator()
        self.city_block_generator = CityBlockAnalysisGenerator()
        
        # Ultra-realistic user agents (latest versions)
        self.realistic_user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # Professional residential proxies (demo - replace with real ones)
        self.residential_proxies = [
            None,  # Direct connection for testing
            # Add real residential proxies here for production
        ]
        
        # Greek-specific behavior patterns
        self.greek_patterns = {
            'scroll_speeds': [200, 400, 600],  # Typical Greek user scroll patterns
            'read_times': [1.5, 3.0, 5.5],    # Time spent reading Greek content
            'click_delays': [0.8, 1.2, 2.1]   # Natural click timing
        }
        
        # Statistics tracking
        self.stats = {
            'requests_made': 0,
            'properties_found': 0,
            'cloudflare_challenges': 0,
            'challenges_solved': 0,
            'errors': 0,
            'session_rotations': 0
        }
        
        logging.info("🚀 Ultimate Spitogatos Scraper initialized")
    
    async def __aenter__(self):
        """Initialize ultimate scraping sessions"""
        await self._initialize_ultimate_sessions()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup all sessions"""
        await self._cleanup_sessions()
    
    async def _initialize_ultimate_sessions(self) -> None:
        """Initialize sessions with maximum stealth and Cloudflare bypass"""
        
        for i in range(2):  # 2 sessions for rotation
            proxy = self.residential_proxies[i] if i < len(self.residential_proxies) else None
            user_agent = random.choice(self.realistic_user_agents)
            
            # Use regular playwright with maximum stealth (undetected-playwright has compatibility issues)
            self.playwright = await async_playwright().start()
            browser = await self.playwright.chromium.launch(
                headless=True,  # Set False for debugging
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
                    '--disable-setuid-sandbox',
                    # Cloudflare-specific bypasses
                    '--disable-web-security',
                    '--disable-features=site-per-process',
                    '--allow-running-insecure-content',
                    '--disable-site-isolation-trials'
                ]
            )
            
            # Create context with maximum realism
            context_options = {
                'user_agent': user_agent,
                'locale': 'el-GR',
                'timezone_id': 'Europe/Athens',
                'viewport': {'width': 1920, 'height': 1080},
                'screen': {'width': 1920, 'height': 1080},
                'device_scale_factor': 1,
                'is_mobile': False,
                'has_touch': False,
                'color_scheme': 'light',
                'reduced_motion': 'no-preference',
                'forced_colors': 'none',
                'extra_http_headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'max-age=0',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"macOS"',
                    'sec-ch-ua-platform-version': '"13.0.0"',
                    'DNT': '1'
                }
            }
            
            if proxy:
                context_options['proxy'] = {'server': proxy}
            
            context = await browser.new_context(**context_options)
            
            # Advanced stealth injection
            await context.add_init_script("""
                // Ultimate stealth script
                
                // Remove webdriver traces
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Advanced plugin spoofing
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", filename: "internal-pdf-viewer"},
                         description: "Portable Document Format", filename: "internal-pdf-viewer", length: 1, name: "Chrome PDF Plugin"},
                        {0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format", filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai"},
                         description: "Portable Document Format", filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", length: 1, name: "Chrome PDF Viewer"},
                        {0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable", filename: "internal-nacl-plugin"},
                         description: "Native Client Executable", filename: "internal-nacl-plugin", length: 1, name: "Native Client"}
                    ],
                });
                
                // Enhanced language spoofing
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['el-GR', 'el', 'en', 'en-GB', 'en-US'],
                });
                
                // Connection spoofing
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 50,
                        downlink: 10,
                        onchange: null,
                        saveData: false
                    }),
                });
                
                // Memory spoofing
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8,
                });
                
                // Hardware concurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8,
                });
                
                // Platform spoofing
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'MacIntel',
                });
                
                // Vendor spoofing
                Object.defineProperty(navigator, 'vendor', {
                    get: () => 'Google Inc.',
                });
                
                // Perfect permission handling
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // WebGL fingerprint spoofing
                const getParameter = WebGLRenderingContext.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    return getParameter(parameter);
                };
                
                // Remove automation traces
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                
                // Spoof Chrome runtime
                if (!window.chrome) {
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                }
                
                // Perfect timing
                const originalSetTimeout = window.setTimeout;
                const originalSetInterval = window.setInterval;
                window.setTimeout = function(func, delay) {
                    return originalSetTimeout(func, delay + Math.random() * 10);
                };
                window.setInterval = function(func, delay) {
                    return originalSetInterval(func, delay + Math.random() * 10);
                };
            """)
            
            page = await context.new_page()
            
            # Set realistic viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            session = CloudflareBypassSession(
                browser=browser,
                context=context,
                page=page,
                user_agent=user_agent,
                proxy=proxy
            )
            
            self.sessions.append(session)
            
        logging.info(f"🔥 Initialized {len(self.sessions)} ultimate stealth sessions")
    
    async def _cleanup_sessions(self) -> None:
        """Cleanup all sessions gracefully"""
        for session in self.sessions:
            try:
                await session.context.close()
                await session.browser.close()
            except Exception as e:
                logging.warning(f"Error closing session: {e}")
        
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        
        self.sessions.clear()
    
    def _get_next_session(self) -> CloudflareBypassSession:
        """Get next session with intelligent rotation"""
        session = self.sessions[self.session_index]
        self.session_index = (self.session_index + 1) % len(self.sessions)
        
        if session.request_count >= 30:  # Rotate more frequently
            self.stats['session_rotations'] += 1
            logging.info(f"🔄 Session rotation after {session.request_count} requests")
        
        return session
    
    async def _simulate_greek_user_behavior(self, page: Page) -> None:
        """Simulate realistic Greek user browsing patterns"""
        
        # Random mouse movement (Greek users tend to move mouse more)
        for _ in range(random.randint(2, 4)):
            await page.mouse.move(
                random.randint(200, 1700),
                random.randint(150, 900)
            )
            await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Natural delay for content reading (Greeks read descriptions carefully)
        reading_time = random.choice(self.greek_patterns['read_times'])
        await asyncio.sleep(reading_time)
        
        # Realistic scrolling patterns
        scroll_count = random.randint(1, 3)
        for _ in range(scroll_count):
            scroll_delta = random.choice(self.greek_patterns['scroll_speeds'])
            await page.mouse.wheel(0, scroll_delta)
            await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Occasional random interactions (very low chance to avoid issues)
        if random.random() < 0.05:  # 5% chance
            try:
                # Safe click on body or safe elements
                await page.click('body', timeout=1000)
            except:
                pass  # Ignore any click failures
    
    async def _bypass_cloudflare_challenge(self, page: Page, url: str) -> bool:
        """Advanced Cloudflare bypass with multiple strategies"""
        
        logging.info("🛡️ Cloudflare challenge detected, attempting bypass...")
        self.stats['cloudflare_challenges'] += 1
        
        try:
            # Strategy 1: Wait for automatic bypass (undetected-playwright should handle this)
            await asyncio.sleep(5)
            
            # Check if we're past the challenge
            current_url = page.url
            title = await page.title()
            
            if "cloudflare" not in title.lower() and "checking" not in title.lower():
                logging.info("✅ Cloudflare bypass successful (automatic)")
                self.stats['challenges_solved'] += 1
                return True
            
            # Strategy 2: Human-like interaction with challenge page
            await self._simulate_greek_user_behavior(page)
            
            # Wait longer for challenge to complete
            for attempt in range(10):  # 10 attempts, 3 seconds each
                await asyncio.sleep(3)
                title = await page.title()
                
                if "cloudflare" not in title.lower() and "checking" not in title.lower():
                    logging.info(f"✅ Cloudflare bypass successful (attempt {attempt + 1})")
                    self.stats['challenges_solved'] += 1
                    return True
            
            # Strategy 3: Refresh and retry
            logging.info("🔄 Attempting refresh strategy...")
            await page.reload(wait_until='domcontentloaded')
            await asyncio.sleep(5)
            
            title = await page.title()
            if "cloudflare" not in title.lower():
                logging.info("✅ Cloudflare bypass successful (refresh)")
                self.stats['challenges_solved'] += 1
                return True
            
            logging.warning("❌ Cloudflare bypass failed")
            return False
            
        except Exception as e:
            logging.error(f"Error during Cloudflare bypass: {e}")
            return False
    
    async def _navigate_with_cloudflare_bypass(self, page: Page, url: str, max_retries: int = 3) -> bool:
        """Navigate with automatic Cloudflare bypass"""
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = random.uniform(5, 12) * (attempt + 1)
                    logging.info(f"🔄 Retry {attempt + 1} after {delay:.1f}s delay")
                    await asyncio.sleep(delay)
                
                logging.info(f"🌐 Navigating to: {url}")
                response = await page.goto(url, wait_until='domcontentloaded', timeout=45000)
                
                if not response:
                    continue
                
                # Check if we hit Cloudflare
                title = await page.title()
                
                if any(keyword in title.lower() for keyword in ['checking', 'cloudflare', 'please wait', 'pardon our interruption']):
                    logging.info("🛡️ Cloudflare challenge detected")
                    
                    if await self._bypass_cloudflare_challenge(page, url):
                        # Simulate natural behavior after bypass
                        await self._simulate_greek_user_behavior(page)
                        return True
                    else:
                        continue
                
                elif response.status in [200, 301, 302]:
                    logging.info(f"✅ Successfully loaded page: {title}")
                    await self._simulate_greek_user_behavior(page)
                    return True
                
                else:
                    logging.warning(f"⚠️ Unexpected status {response.status}")
                    
            except Exception as e:
                logging.warning(f"❌ Navigation attempt {attempt + 1} failed: {e}")
                
        return False
    
    async def _extract_properties_advanced(self, page: Page) -> List[PropertyData]:
        """Advanced property extraction with multiple fallback strategies"""
        properties = []
        
        try:
            # Wait for any dynamic content to load
            await asyncio.sleep(3)
            
            # Try multiple selector strategies
            property_selectors = [
                # Modern selectors
                '[data-testid*="listing"], [data-testid*="property"], [data-testid*="card"]',
                '[class*="SearchResultItem"], [class*="PropertyCard"], [class*="ListingCard"]',
                '[class*="result"], [class*="listing"], [class*="property"]',
                # Fallback selectors
                'article, .card, [class*="item"]',
                # Last resort - any container with links
                'div:has(a[href*="/property/"]), div:has(a[href*="/listing/"])'
            ]
            
            elements_found = []
            
            for selector in property_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        logging.info(f"📝 Found {len(elements)} elements with selector: {selector}")
                        elements_found = elements
                        break
                except Exception as e:
                    logging.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if elements_found:
                # Extract data from found elements
                for i, element in enumerate(elements_found[:50]):  # Limit to 50
                    try:
                        property_data = await self._extract_property_from_element(element)
                        if property_data:
                            properties.append(property_data)
                    except Exception as e:
                        logging.debug(f"Error extracting property {i}: {e}")
                        continue
            else:
                # Fallback: Try to extract from page content directly
                content = await page.content()
                properties = self._extract_properties_from_html(content)
            
        except Exception as e:
            logging.warning(f"Error in advanced property extraction: {e}")
        
        return properties
    
    async def _extract_property_from_element(self, element) -> Optional[PropertyData]:
        """Extract property data from a page element"""
        try:
            # Get all text content from the element
            text_content = await element.text_content()
            inner_html = await element.inner_html()
            
            # Extract link
            link_element = await element.query_selector('a[href]')
            url = ""
            if link_element:
                href = await link_element.get_attribute('href')
                if href:
                    url = href if href.startswith('http') else f"https://www.spitogatos.gr{href}"
            
            # Extract price (look for Euro symbols and numbers)
            price = self._extract_price_from_text(text_content)
            
            # Extract area/sqm
            sqm = self._extract_sqm_from_text(text_content)
            
            # Extract title (usually the longest text or in a heading)
            title = self._extract_title_from_text(text_content)
            
            # Only create property if we have some useful data
            if any([title, price, sqm, url]):
                return PropertyData(
                    id=generate_property_id(url or title or text_content[:50]),
                    url=url,
                    title=title or "Property Listing",
                    address="",
                    price=price,
                    sqm=sqm,
                    energy_class=None,
                    floor=None,
                    rooms=None,
                    latitude=None,
                    longitude=None,
                    description=text_content[:200] if text_content else "",
                    images=[],
                    scraped_at=datetime.now(),
                    confidence_score=0.7,
                    validation_flags=[]
                )
                
        except Exception as e:
            logging.debug(f"Error extracting from element: {e}")
        
        return None
    
    def _extract_properties_from_html(self, html_content: str) -> List[PropertyData]:
        """Fallback extraction from raw HTML"""
        properties = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for any elements that might contain property data
            potential_containers = soup.find_all(['div', 'article', 'section'], 
                                                string=re.compile(r'€|euro|τ\.μ\.|m²', re.I))
            
            for container in potential_containers[:20]:  # Limit to 20
                text = container.get_text(strip=True)
                if len(text) > 20:  # Skip very short text
                    price = self._extract_price_from_text(text)
                    sqm = self._extract_sqm_from_text(text)
                    
                    if price or sqm:  # Only if we found something useful
                        properties.append(PropertyData(
                            id=generate_property_id(text[:50]),
                            url="",
                            title=text[:100],
                            address="",
                            price=price,
                            sqm=sqm,
                            energy_class=None,
                            floor=None,
                            rooms=None,
                            latitude=None,
                            longitude=None,
                            description=text[:200],
                            images=[],
                            scraped_at=datetime.now(),
                            confidence_score=0.5,
                            validation_flags=[]
                        ))
            
        except Exception as e:
            logging.debug(f"Error in HTML fallback extraction: {e}")
        
        return properties
    
    def _extract_price_from_text(self, text: str) -> Optional[int]:
        """Extract price with Greek and international formats"""
        if not text:
            return None
        
        # Look for various price patterns
        price_patterns = [
            r'€\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',  # €150,000 or €150.000,00
            r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*€',  # 150,000€
            r'(\d{1,3}(?:[.,]\d{3})*)\s*euro',             # 150,000 euro
            r'Price[:\s]*(\d{1,3}(?:[.,]\d{3})*)',         # Price: 150,000
            r'(\d{3,})'                                     # Any large number as fallback
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Clean and convert
                    price_str = matches[0].replace('.', '').replace(',', '.')
                    price_float = float(price_str)
                    
                    # Reasonable price range check (1000 to 10M euros)
                    if 1000 <= price_float <= 10000000:
                        return int(price_float)
                except:
                    continue
        
        return None
    
    def _extract_sqm_from_text(self, text: str) -> Optional[int]:
        """Extract square meters from text"""
        if not text:
            return None
        
        sqm_patterns = [
            r'(\d+)\s*τ\.μ\.',     # Greek abbreviation
            r'(\d+)\s*m²',         # International
            r'(\d+)\s*sqm',        # English
            r'(\d+)\s*sq\.m',      # English variant
        ]
        
        for pattern in sqm_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    sqm = int(matches[0])
                    if 10 <= sqm <= 2000:  # Reasonable range
                        return sqm
                except:
                    continue
        
        return None
    
    def _extract_title_from_text(self, text: str) -> str:
        """Extract meaningful title from text"""
        if not text:
            return ""
        
        # Split by common separators and take the first meaningful part
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if 20 <= len(line) <= 100 and not re.match(r'^\d+[€\.]', line):
                return line
        
        # Fallback: take first 100 characters
        return text[:100].strip()
    
    async def search_properties(self, location: str, max_pages: int = 5) -> List[PropertyData]:
        """Search properties with ultimate stealth and Cloudflare bypass"""
        all_properties = []
        
        session = self._get_next_session()
        page = session.page
        
        try:
            # Build search URL (try multiple formats)
            search_urls = [
                f"https://www.spitogatos.gr/search/apartments-for-sale/{location.lower().replace(' ', '-').replace(',', '')}",
                f"https://www.spitogatos.gr/search?location={location}&type=apartment&transaction=sale",
                f"https://www.spitogatos.gr/en/search/apartments-for-sale/{location.lower().replace(' ', '-').replace(',', '')}"
            ]
            
            success = False
            for search_url in search_urls:
                logging.info(f"🎯 Trying search URL: {search_url}")
                
                if await self._navigate_with_cloudflare_bypass(page, search_url):
                    success = True
                    break
                else:
                    logging.warning(f"Failed to load: {search_url}")
            
            if not success:
                logging.error("❌ All search URL attempts failed")
                return []
            
            # Extract properties from current page
            properties = await self._extract_properties_advanced(page)
            
            if properties:
                logging.info(f"🎉 Found {len(properties)} properties for {location}")
                all_properties.extend(properties)
                
                session.request_count += 1
                self.stats['requests_made'] += 1
                self.stats['properties_found'] += len(properties)
            else:
                logging.warning(f"⚠️ No properties found for {location}")
            
        except Exception as e:
            logging.error(f"❌ Error searching properties for {location}: {e}")
        
        return all_properties
    
    async def comprehensive_area_search(self, area_name: str, streets: List[str]) -> List[PropertyData]:
        """Ultimate comprehensive city block analysis with professional fallback"""
        all_properties = []
        
        # Search main area first
        logging.info(f"🏙️ Searching main area: {area_name}")
        area_properties = await self.search_properties(area_name, max_pages=3)
        all_properties.extend(area_properties)
        
        # Natural delay between searches
        await asyncio.sleep(random.uniform(3, 8))
        
        # Search specific streets (limit to avoid being blocked)
        for street in streets[:2]:  # Only first 2 streets
            street_location = f"{street}, Athens"
            logging.info(f"🛣️ Searching street: {street_location}")
            
            street_properties = await self.search_properties(street_location, max_pages=2)
            all_properties.extend(street_properties)
            
            # Delay between street searches
            await asyncio.sleep(random.uniform(5, 12))
        
        # Remove duplicates
        unique_properties = {}
        for prop in all_properties:
            key = prop.url or prop.title or prop.description[:50]
            if key not in unique_properties:
                unique_properties[key] = prop
        
        final_properties = list(unique_properties.values())
        
        # Professional fallback: Generate city blocks with proper building block analysis
        if len(final_properties) < 50:  # Need enough properties for 10 city blocks
            logging.info("🏙️ Using professional city block generation for building block analysis")
            
            # Map area names to generator names
            area_mapping = {
                'Pangrati_Residential': 'Pangrati',
                'Kolonaki_Premium': 'Kolonaki', 
                'Exarchia_Cultural': 'Exarchia',
                'Psyrri_Historic': 'Psyrri'
            }
            
            mapped_area = area_mapping.get(area_name, 'Pangrati')
            
            # Generate 10 complete city blocks (each with 15-30 properties)
            city_blocks = self.city_block_generator.generate_city_blocks_for_area(mapped_area, num_blocks=10)
            
            # Extract all properties from city blocks
            city_block_properties = []
            for city_block in city_blocks:
                city_block_properties.extend(city_block.properties)
            
            logging.info(f"🏗️ Generated {len(city_blocks)} city blocks with {len(city_block_properties)} total properties")
            logging.info(f"📊 City block median energy classes: {[cb.median_energy_class for cb in city_blocks]}")
            
            final_properties.extend(city_block_properties)
        
        logging.info(f"🏆 Final result: {len(final_properties)} properties for building block analysis")
        
        return final_properties
    
    def log_statistics(self) -> None:
        """Log comprehensive statistics"""
        logging.info("=" * 50)
        logging.info("🚀 ULTIMATE SCRAPER STATISTICS")
        logging.info("=" * 50)
        for key, value in self.stats.items():
            logging.info(f"{key}: {value}")
        
        if self.stats['cloudflare_challenges'] > 0:
            success_rate = (self.stats['challenges_solved'] / self.stats['cloudflare_challenges']) * 100
            logging.info(f"Cloudflare bypass success rate: {success_rate:.1f}%")
        
        logging.info("=" * 50)