#!/usr/bin/env python3
"""
XE.GR PROFESSIONAL CONCURRENT SCRAPER
Implements all expert principles: Producer-Consumer, Proxy Management, Anti-Detection
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from config import config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PropertyData:
    url: str
    neighborhood: str
    title: str = ""
    address: str = ""
    price: Optional[float] = None
    sqm: Optional[float] = None
    rooms: Optional[int] = None
    description: str = ""
    extraction_timestamp: str = ""
    worker_id: str = ""

class ProxyManager:
    """Professional proxy management with rotation and sticky sessions"""
    
    def __init__(self, proxy_list: List[str]):
        self.proxies = proxy_list or []
        self.current_index = 0
        self.request_count = 0
        self.session_start_time = time.time()
    
    def get_current_proxy(self) -> Optional[str]:
        if not self.proxies:
            return None
        return self.proxies[self.current_index]
    
    def should_rotate(self) -> bool:
        """Check if proxy should be rotated based on requests or time"""
        if not self.proxies:
            return False
        
        # Rotate after N requests or after session duration
        return (self.request_count >= config.proxy_rotation_interval or
                time.time() - self.session_start_time >= config.sticky_session_duration)
    
    def rotate_proxy(self):
        """Rotate to next proxy"""
        if self.proxies:
            self.current_index = (self.current_index + 1) % len(self.proxies)
            self.request_count = 0
            self.session_start_time = time.time()
            logger.info(f"🔄 Rotated to proxy: {self.get_current_proxy()}")
    
    def increment_request(self):
        """Increment request counter"""
        self.request_count += 1

class BrowserManager:
    """Manages browser contexts with anti-detection"""
    
    def __init__(self, proxy_manager: ProxyManager):
        self.proxy_manager = proxy_manager
        self.browser: Optional[Browser] = None
    
    async def create_browser(self) -> Browser:
        """Create browser with anti-detection settings"""
        p = await async_playwright().start()
        
        # Enhanced stealth arguments
        args = [
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--disable-gpu',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-default-apps',
            '--disable-plugins-discovery',
            '--disable-notifications',
            '--disable-popup-blocking'
        ]
        
        proxy_config = None
        if self.proxy_manager.get_current_proxy():
            proxy_config = {"server": self.proxy_manager.get_current_proxy()}
        
        self.browser = await p.chromium.launch(
            headless=config.headless,
            args=args,
            proxy=proxy_config
        )
        
        return self.browser
    
    async def create_context(self) -> BrowserContext:
        """Create context with human-like settings"""
        if not self.browser:
            await self.create_browser()
        
        # Randomized viewport
        viewport_width = config.viewport_width + random.randint(-100, 100)
        viewport_height = config.viewport_height + random.randint(-100, 100)
        
        # Random user agent selection
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]
        
        context = await self.browser.new_context(
            viewport={'width': viewport_width, 'height': viewport_height},
            user_agent=random.choice(user_agents),
            locale='el-GR',
            timezone_id='Europe/Athens',
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'el-GR,el;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none'
            }
        )
        
        return context
    
    async def apply_stealth(self, page: Page):
        """Apply stealth techniques to page"""
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['el-GR', 'el', 'en-US', 'en'] });
        """)
        
        # Simulate human mouse movement
        await page.mouse.move(random.randint(100, 200), random.randint(100, 200))
        await asyncio.sleep(random.uniform(0.1, 0.3))

class ProfessionalScraper:
    """Main scraper class implementing all expert principles"""
    
    def __init__(self):
        self.proxy_manager = ProxyManager(config.proxy_list)
        self.browser_manager = BrowserManager(self.proxy_manager)
        self.url_queue = asyncio.Queue()
        self.results = []
        self.stats = {
            'urls_discovered': 0,
            'properties_scraped': 0,
            'failures': 0,
            'start_time': None,
            'end_time': None
        }
    
    async def run(self) -> List[PropertyData]:
        """Main orchestration method"""
        logger.info("🚀 PROFESSIONAL XE.GR SCRAPER STARTING")
        logger.info(f"📊 Config: {config.max_workers} workers, {len(config.neighborhoods)} areas")
        
        self.stats['start_time'] = datetime.now()
        
        # Start producer and consumers concurrently
        tasks = []
        
        # Producer task (URL discovery)
        tasks.append(asyncio.create_task(self.producer()))
        
        # Consumer tasks (property scraping)
        for i in range(config.max_workers):
            tasks.append(asyncio.create_task(self.consumer(f"worker-{i+1}")))
        
        # Wait for producer to finish, then let consumers finish remaining work
        await tasks[0]  # Wait for producer
        logger.info("📦 URL discovery complete, waiting for workers to finish...")
        
        # Wait a bit for consumers to finish remaining work
        await asyncio.sleep(10)
        
        # Cancel remaining consumer tasks
        for task in tasks[1:]:
            task.cancel()
        
        self.stats['end_time'] = datetime.now()
        self.print_stats()
        
        return self.results
    
    async def producer(self):
        """Producer: Discovers property URLs and adds them to queue"""
        logger.info("🔍 PRODUCER: Starting URL discovery")
        
        try:
            context = await self.browser_manager.create_context()
            page = await context.new_page()
            await self.browser_manager.apply_stealth(page)
            
            # Navigate to homepage and handle cookies
            await page.goto(config.base_url, wait_until="load", timeout=30000)
            await asyncio.sleep(2)
            
            # Handle cookie consent
            try:
                cookie_btn = await page.wait_for_selector('button:has-text("ΣΥΜΦΩΝΩ")', timeout=5000)
                if cookie_btn:
                    await cookie_btn.click()
                    await asyncio.sleep(2)
            except:
                pass
            
            # Navigate to property section
            property_link = await page.wait_for_selector('a:has-text("Ακίνητα")', timeout=10000)
            await property_link.click()
            await asyncio.sleep(3)
            
            # Search each neighborhood
            for neighborhood in config.neighborhoods:
                logger.info(f"🔍 PRODUCER: Discovering URLs for {neighborhood}")
                
                urls = await self.discover_urls_for_neighborhood(page, neighborhood)
                
                for url in urls[:config.max_properties_per_area]:
                    await self.url_queue.put((url, neighborhood))
                    self.stats['urls_discovered'] += 1
                
                logger.info(f"📦 PRODUCER: Added {len(urls)} URLs for {neighborhood}")
                await asyncio.sleep(config.producer_delay)
            
            # Add sentinel values to signal end
            for _ in range(config.max_workers):
                await self.url_queue.put(None)
            
            await context.close()
            
        except Exception as e:
            logger.error(f"❌ PRODUCER failed: {e}")
    
    async def discover_urls_for_neighborhood(self, page: Page, neighborhood: str) -> List[str]:
        """Discover property URLs for a specific neighborhood"""
        try:
            # Fill search form
            location_input = await page.wait_for_selector('input[placeholder*="Τοποθεσία"]', timeout=10000)
            await location_input.fill(f"Αθήνα, {neighborhood}")
            await asyncio.sleep(1)
            
            # Submit search - use Enter key (most reliable)
            await page.keyboard.press('Enter')
            logger.info(f"🔍 Submitted search for {neighborhood}")
            
            await asyncio.sleep(5)  # Wait for results
            
            # Extract property URLs
            urls = []
            for selector in ['a[href*="/d/"]', 'a[href*="property"]', 'a[href*="enoikiaseis"]']:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        href = await element.get_attribute('href')
                        if href and 'xe.gr' in href and '/d/' in href:
                            urls.append(href)
                except:
                    continue
            
            return list(set(urls))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"❌ URL discovery failed for {neighborhood}: {e}")
            return []
    
    async def consumer(self, worker_id: str):
        """Consumer: Scrapes individual properties"""
        logger.info(f"👷 {worker_id}: Starting consumer")
        
        while True:
            try:
                # Get URL from queue
                item = await self.url_queue.get()
                if item is None:  # Sentinel value
                    break
                
                url, neighborhood = item
                
                # Check if proxy should rotate
                if self.proxy_manager.should_rotate():
                    self.proxy_manager.rotate_proxy()
                
                # Create fresh context for each property
                context = await self.browser_manager.create_context()
                page = await context.new_page()
                await self.browser_manager.apply_stealth(page)
                
                logger.info(f"👷 {worker_id}: Scraping {url[:60]}...")
                
                # Scrape property
                property_data = await self.scrape_property(page, url, neighborhood, worker_id)
                
                if property_data:
                    self.results.append(property_data)
                    self.stats['properties_scraped'] += 1
                    logger.info(f"✅ {worker_id}: Success - {property_data.title[:50]}...")
                else:
                    self.stats['failures'] += 1
                    logger.warning(f"❌ {worker_id}: Failed to extract data")
                
                await context.close()
                self.proxy_manager.increment_request()
                
                # Human-like delay
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
            except Exception as e:
                logger.error(f"❌ {worker_id}: Consumer error: {e}")
                self.stats['failures'] += 1
                continue
        
        logger.info(f"👷 {worker_id}: Consumer finished")
    
    async def scrape_property(self, page: Page, url: str, neighborhood: str, worker_id: str) -> Optional[PropertyData]:
        """Scrape individual property page"""
        try:
            await page.goto(url, wait_until="load", timeout=30000)
            await asyncio.sleep(2)
            
            # Basic validation
            content = await page.content()
            if not any(indicator in content.lower() for indicator in ['τιμή', 'price', 'ενοικίαση']):
                return None
            
            property_data = PropertyData(
                url=url,
                neighborhood=neighborhood,
                worker_id=worker_id,
                extraction_timestamp=datetime.now().isoformat()
            )
            
            # Extract title
            try:
                title_element = await page.query_selector('h1, .property-title, .listing-title')
                if title_element:
                    property_data.title = (await title_element.inner_text()).strip()[:200]
            except:
                pass
            
            # Extract price
            try:
                page_text = await page.inner_text('body')
                import re
                
                price_patterns = [
                    r'(\d{1,3}(?:\.\d{3})*)\s*€',
                    r'€\s*(\d{1,3}(?:\.\d{3})*)',
                    r'τιμή[:\s]*(\d{1,3}(?:\.\d{3})*)'
                ]
                
                for pattern in price_patterns:
                    match = re.search(pattern, page_text)
                    if match:
                        try:
                            price = float(match.group(1).replace('.', ''))
                            if 50 <= price <= 5000000:
                                property_data.price = price
                                break
                        except:
                            continue
            except:
                pass
            
            # Extract area
            try:
                sqm_patterns = [r'(\d+(?:[.,]\d+)?)\s*τ\.?μ\.?', r'(\d+(?:[.,]\d+)?)\s*m²']
                for pattern in sqm_patterns:
                    match = re.search(pattern, page_text)
                    if match:
                        try:
                            sqm = float(match.group(1).replace(',', '.'))
                            if 10 <= sqm <= 500:
                                property_data.sqm = sqm
                                break
                        except:
                            continue
            except:
                pass
            
            # Must have at least title or price to be valid
            if property_data.title or property_data.price:
                return property_data
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Property scraping failed: {e}")
            return None
    
    def print_stats(self):
        """Print execution statistics"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        logger.info("\n" + "="*50)
        logger.info("📊 SCRAPING STATISTICS")
        logger.info("="*50)
        logger.info(f"⏱️  Duration: {duration}")
        logger.info(f"🔗 URLs discovered: {self.stats['urls_discovered']}")
        logger.info(f"✅ Properties scraped: {self.stats['properties_scraped']}")
        logger.info(f"❌ Failures: {self.stats['failures']}")
        logger.info(f"📈 Success rate: {self.stats['properties_scraped'] / max(1, self.stats['urls_discovered']) * 100:.1f}%")
        logger.info(f"⚡ Speed: {self.stats['properties_scraped'] / max(1, duration.total_seconds()) * 60:.1f} properties/minute")
        
        if self.results:
            with_price = len([p for p in self.results if p.price])
            with_area = len([p for p in self.results if p.sqm])
            logger.info(f"💰 Properties with price: {with_price}")
            logger.info(f"📐 Properties with area: {with_area}")
        
        logger.info("="*50)

async def main():
    """Main entry point"""
    scraper = ProfessionalScraper()
    results = await scraper.run()
    
    if results:
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'outputs/professional_results_{timestamp}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(r) for r in results], f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Results saved: {output_file}")
        
        # Show sample results
        logger.info("\n🎯 SAMPLE RESULTS:")
        for i, prop in enumerate(results[:3], 1):
            logger.info(f"{i}. {prop.title[:50]} - €{prop.price} - {prop.sqm}m²")
    
    await scraper.browser_manager.browser.close()

if __name__ == "__main__":
    asyncio.run(main())