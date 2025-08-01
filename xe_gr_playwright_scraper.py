#!/usr/bin/env python3
"""
XE.GR PLAYWRIGHT SCRAPER - DYNAMIC CONTENT SOLUTION
Handles React SPA dynamic loading using browser automation
"""

import asyncio
import json
import logging
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import hashlib
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RealPropertyData:
    """Real property data with complete validation"""
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
    extraction_method: str = "playwright_dynamic"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PlaywrightXEScraper:
    """XE.gr scraper using Playwright for dynamic content"""
    
    def __init__(self):
        self.scraped_properties = []
        self.failed_urls = []
        self.audit_log = []
        
        # Discovered working endpoint
        self.search_url = "https://xe.gr/search"
        
        logger.info("🎭 PLAYWRIGHT XE.GR SCRAPER")
        logger.info("🚀 Browser automation for React dynamic content")
    
    async def scrape_properties_dynamic(self, neighborhood: str, max_properties: int = 10) -> List[RealPropertyData]:
        """Scrape properties using browser automation"""
        
        logger.info(f"🎯 DYNAMIC SCRAPING: {neighborhood}")
        logger.info(f"📋 Target: {max_properties} properties with full browser rendering")
        
        properties = []
        
        async with async_playwright() as p:
            # Launch browser with realistic settings
            browser = await p.chromium.launch(
                headless=True,  # Set to False for debugging
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-extensions',
                    '--disable-gpu',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-default-apps'
                ]
            )
            
            # Create context with realistic viewport
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                locale='el-GR',
                timezone_id='Europe/Athens'
            )
            
            try:
                page = await context.new_page()
                
                # Intercept and log network requests (for debugging)
                await page.route('**/*', self.handle_route)
                
                # Step 1: Navigate to search page and perform search
                logger.info("🔍 Loading search page...")
                await page.goto(self.search_url, wait_until='networkidle')
                
                # Wait for React to load
                await page.wait_for_timeout(3000)
                
                # Step 2: Fill search form with neighborhood
                logger.info(f"📝 Searching for: {neighborhood}")
                await self.perform_search(page, neighborhood)
                
                # Step 3: Wait for results and extract property URLs
                logger.info("⏳ Waiting for search results...")
                property_urls = await self.extract_property_urls_dynamic(page)
                logger.info(f"📦 Found {len(property_urls)} property URLs")
                
                # Step 4: Visit each property page and extract data
                for i, prop_url in enumerate(property_urls[:max_properties]):
                    logger.info(f"🏠 Scraping property {i+1}/{min(len(property_urls), max_properties)}: {prop_url[:80]}...")
                    
                    prop_data = await self.scrape_property_page(page, prop_url, neighborhood)
                    if prop_data:
                        properties.append(prop_data)
                        logger.info(f"✅ Property: {prop_data.address[:50]}... €{prop_data.price}")
                    else:
                        logger.warning(f"❌ Failed to scrape: {prop_url[:80]}...")
                    
                    # Respectful delay
                    await page.wait_for_timeout(2000)
                    
            except Exception as e:
                logger.error(f"❌ Browser automation failed: {e}")
            finally:
                await browser.close()
        
        logger.info(f"🎭 PLAYWRIGHT SCRAPING COMPLETE: {len(properties)} properties")
        return properties
    
    async def handle_route(self, route):
        """Handle network requests (for debugging)"""
        # Continue with all requests
        await route.continue_()
    
    async def perform_search(self, page: Page, neighborhood: str):
        """Perform search on the loaded page"""
        
        try:
            # Method 1: Look for freetext search input
            freetext_selectors = [
                'input[name="Publication.freetext"]',
                'input[placeholder*="search"]',
                'input[type="text"]',
                '.search-input',
                '#search-input'
            ]
            
            search_filled = False
            for selector in freetext_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=2000)
                    if element:
                        await element.fill(f"Αθήνα {neighborhood}")
                        logger.info(f"✅ Filled search with: Αθήνα {neighborhood}")
                        search_filled = True
                        break
                except:
                    continue
            
            if not search_filled:
                logger.warning("⚠️ Could not find search input field")
                # Try to type in any visible input
                await page.keyboard.type(f"Αθήνα {neighborhood}")
            
            # Look for submit button or press Enter
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                '.search-button',
                '.submit-button',
                'button:has-text("Αναζήτηση")',
                'button:has-text("Search")'
            ]
            
            submitted = False
            for selector in submit_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=2000)
                    if element:
                        await element.click()
                        logger.info("✅ Clicked search button")
                        submitted = True
                        break
                except:
                    continue
            
            if not submitted:
                # Try pressing Enter
                await page.keyboard.press('Enter')
                logger.info("✅ Pressed Enter to search")
            
            # Wait for search results to load
            await page.wait_for_timeout(3000)
            
        except Exception as e:
            logger.error(f"❌ Search form submission failed: {e}")
    
    async def extract_property_urls_dynamic(self, page: Page) -> List[str]:
        """Extract property URLs from dynamically loaded results"""
        
        urls = set()
        
        try:
            # Wait for content to load
            await page.wait_for_timeout(5000)
            
            # Method 1: Look for property links in the DOM
            property_selectors = [
                'a[href*="/property/"]',
                'a[href*="/d/"]',
                'a[href*="enoikiaseis"]',
                'a[href*="poliseis"]',
                '.property-card a',
                '.listing a',
                '.result-item a',
                '[data-testid*="property"] a',
                '[class*="property"] a',
                '[class*="listing"] a'
            ]
            
            for selector in property_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        href = await element.get_attribute('href')
                        if href:
                            if href.startswith('/'):
                                full_url = f"https://xe.gr{href}"
                            else:
                                full_url = href
                            
                            if self.is_valid_property_url(full_url):
                                urls.add(full_url)
                                logger.info(f"📎 Found property URL: {full_url[:80]}...")
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Method 2: Extract URLs from page content/JavaScript
            page_content = await page.content()
            
            # Look for property URLs in the HTML
            url_patterns = [
                r'https://xe\.gr/property/d/[^"\s]+',
                r'https://xe\.gr/[^"\s]*enoikiaseis[^"\s]*',
                r'https://xe\.gr/[^"\s]*poliseis[^"\s]*',
                r'/property/d/[^"\s]+',
                r'/[^"\s]*enoikiaseis[^"\s]*',
                r'/[^"\s]*poliseis[^"\s]*'
            ]
            
            for pattern in url_patterns:
                matches = re.findall(pattern, page_content)
                for match in matches:
                    if match.startswith('/'):
                        full_url = f"https://xe.gr{match}"
                    else:
                        full_url = match
                    
                    if self.is_valid_property_url(full_url):
                        urls.add(full_url)
            
            # Method 3: Scroll and look for more content (lazy loading)
            if len(urls) < 5:
                logger.info("🔄 Scrolling to load more results...")
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(3000)
                
                # Try extracting again after scroll
                elements = await page.query_selector_all('a[href*="/property/"], a[href*="/d/"]')
                for element in elements:
                    href = await element.get_attribute('href')
                    if href:
                        if href.startswith('/'):
                            full_url = f"https://xe.gr{href}"
                        else:
                            full_url = href
                        
                        if self.is_valid_property_url(full_url):
                            urls.add(full_url)
            
            # Save debug info
            debug_file = f'outputs/search_page_debug_{datetime.now().strftime("%H%M%S")}.html'
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(page_content)
            logger.info(f"🔍 Search page saved: {debug_file}")
            
        except Exception as e:
            logger.error(f"❌ URL extraction failed: {e}")
        
        return list(urls)
    
    def is_valid_property_url(self, url: str) -> bool:
        """Validate property URL"""
        
        if not url or 'xe.gr' not in url:
            return False
        
        # Must contain property indicators
        property_indicators = ['/property/', '/d/', '/enoikiaseis/', '/poliseis/']
        if not any(indicator in url for indicator in property_indicators):
            return False
        
        # Must not be search, admin, or API
        invalid_patterns = ['/search', '/admin', '/api/', '/results', '/filter', 'javascript:', 'mailto:']
        if any(pattern in url.lower() for pattern in invalid_patterns):
            return False
        
        # Should contain some ID or specific identifier
        if not re.search(r'\d{6,}', url):
            return False
        
        return True
    
    async def scrape_property_page(self, page: Page, url: str, neighborhood: str) -> Optional[RealPropertyData]:
        """Scrape individual property page with browser automation"""
        
        try:
            logger.info(f"🏠 Loading property page: {url[:80]}...")
            
            # Navigate to property page
            await page.goto(url, wait_until='networkidle')
            
            # Wait for React content to load
            await page.wait_for_timeout(3000)
            
            # Get page content after JavaScript execution
            html = await page.content()
            
            # Quick validation - is this actually a property page?
            if not self.is_property_page_content(html, neighborhood):
                logger.warning(f"⚠️ Not a property page: {url}")
                return None
            
            # Extract property data using dynamic content
            data = {
                'property_id': self.generate_property_id(url),
                'url': url,
                'source_timestamp': datetime.now().isoformat(),
                'html_source_hash': hashlib.md5(html.encode()).hexdigest(),
                'neighborhood': neighborhood,
                'extraction_method': 'playwright_dynamic',
                'title': await self.extract_title_dynamic(page),
                'address': await self.extract_address_dynamic(page),
                'price': await self.extract_price_dynamic(page),
                'sqm': await self.extract_sqm_dynamic(page),
                'rooms': await self.extract_rooms_dynamic(page),
                'floor': await self.extract_floor_dynamic(page),
                'description': await self.extract_description_dynamic(page),
                'energy_class': await self.extract_energy_class_dynamic(page, html),
                'latitude': None,
                'longitude': None,
                'extraction_confidence': 0.0,
                'validation_flags': []
            }
            
            # Calculate confidence and flags
            data['extraction_confidence'] = self.calculate_confidence(data)
            data['validation_flags'] = self.generate_flags(data)
            
            prop = RealPropertyData(**data)
            
            # Final validation
            if self.validate_property(prop):
                logger.info(f"✅ Valid property: {prop.address[:50]}...")
                return prop
            else:
                logger.warning(f"❌ Property validation failed")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
            return None
    
    async def extract_title_dynamic(self, page: Page) -> str:
        """Extract title using dynamic selectors"""
        selectors = ['h1', '.property-title', '.listing-title', 'title', '[class*="title"]']
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    title = await element.inner_text()
                    if title and len(title.strip()) > 5:
                        return title.strip()[:200]
            except:
                continue
        
        return "No title found"
    
    async def extract_address_dynamic(self, page: Page) -> str:
        """Extract address using dynamic selectors"""
        selectors = ['.address', '.location', '.property-address', '.geo-info', '[class*="address"]', '[class*="location"]']
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    address = await element.inner_text()
                    if address and self.validate_athens_address(address.strip()):
                        return address.strip()[:300]
            except:
                continue
        
        # Try page text for Athens references
        try:
            page_text = await page.inner_text('body')
            athens_patterns = [
                r'[Αα]θήνα[^,\n]{0,50}',
                r'Athens[^,\n]{0,50}',
                r'[Κκ]ολωνάκι[^,\n]{0,30}',
                r'[Ππ]αγκράτι[^,\n]{0,30}',
                r'[Εε]ξάρχεια[^,\n]{0,30}'
            ]
            
            for pattern in athens_patterns:
                match = re.search(pattern, page_text)
                if match:
                    return match.group(0).strip()
        except:
            pass
        
        return "Address not found"
    
    def validate_athens_address(self, address: str) -> bool:
        """Validate Athens address"""
        if not address or len(address) < 5:
            return False
        address_lower = address.lower()
        indicators = ['αθήνα', 'athens', 'κολωνάκι', 'kolonaki', 'παγκράτι', 'pangrati', 'εξάρχεια', 'exarchia']
        return any(indicator in address_lower for indicator in indicators)
    
    async def extract_price_dynamic(self, page: Page) -> Optional[float]:
        """Extract price using dynamic selectors"""
        selectors = ['.price', '.property-price', '[data-testid*="price"]', '.cost', '[class*="price"]']
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    price_text = await element.inner_text()
                    price = self.parse_price(price_text.strip())
                    if price and 50 <= price <= 5000000:
                        return price
            except:
                continue
        
        # Search page text
        try:
            page_text = await page.inner_text('body')
            price_patterns = [
                r'(\d{1,3}(?:\.\d{3})*)\s*€',
                r'€\s*(\d{1,3}(?:\.\d{3})*)',
                r'τιμή[:\s]*(\d{1,3}(?:\.\d{3})*)',
                r'(\d{1,3}(?:\.\d{3})*)\s*ευρώ'
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    price = self.parse_price(match.group(1))
                    if price and 50 <= price <= 5000000:
                        return price
        except:
            pass
        
        return None
    
    def parse_price(self, price_text: str) -> Optional[float]:
        """Parse price with Greek format"""
        if not price_text:
            return None
        
        # Clean price text
        price_clean = re.sub(r'[€$£¥₹ευρώeur]', '', price_text, flags=re.IGNORECASE)
        price_clean = re.sub(r'[^\d.,]', '', price_clean)
        
        if not price_clean:
            return None
        
        try:
            # Handle thousands separators
            if '.' in price_clean:
                parts = price_clean.split('.')
                if len(parts) == 2 and len(parts[1]) == 3:
                    # 1.500 format (thousands)
                    price_clean = price_clean.replace('.', '')
            
            price = float(price_clean)
            
            # If very small, might be in thousands
            if price < 10:
                price = price * 1000
            
            return price
        except ValueError:
            return None
    
    async def extract_sqm_dynamic(self, page: Page) -> Optional[float]:
        """Extract square meters using dynamic content"""
        try:
            page_text = await page.inner_text('body')
            sqm_patterns = [
                r'(\d+(?:[.,]\d+)?)\s*τ\.?μ\.?',
                r'(\d+(?:[.,]\d+)?)\s*m²',
                r'(\d+(?:[.,]\d+)?)\s*sqm',
                r'εμβαδόν[:\s]*(\d+(?:[.,]\d+)?)',
                r'(\d+(?:[.,]\d+)?)\s*τετραγωνικά'
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
        except:
            pass
        
        return None
    
    async def extract_rooms_dynamic(self, page: Page) -> Optional[int]:
        """Extract rooms using dynamic content"""
        try:
            page_text = await page.inner_text('body')
            room_patterns = [
                r'(\d+)\s*δωμάτια?',
                r'(\d+)\s*rooms?',
                r'(\d+)\s*υπνοδωμάτια?',
                r'(\d+)\s*bedrooms?'
            ]
            
            for pattern in room_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    try:
                        rooms = int(match.group(1))
                        if 1 <= rooms <= 10:
                            return rooms
                    except ValueError:
                        continue
        except:
            pass
        
        return None
    
    async def extract_floor_dynamic(self, page: Page) -> Optional[str]:
        """Extract floor using dynamic content"""
        try:
            page_text = await page.inner_text('body')
            floor_patterns = [
                r'όροφος[:\s]*([^,\n.]{1,15})',
                r'floor[:\s]*([^,\n.]{1,15})',
                r'(\d+)ος\s*όροφος'
            ]
            
            for pattern in floor_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        except:
            pass
        
        return None
    
    async def extract_description_dynamic(self, page: Page) -> str:
        """Extract description using dynamic selectors"""
        selectors = ['.description', '.property-description', '.details', '[class*="description"]', '.content']
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    desc = await element.inner_text()
                    if desc and len(desc.strip()) > 20:
                        return desc.strip()[:1000]
            except:
                continue
        
        return "No description found"
    
    async def extract_energy_class_dynamic(self, page: Page, html: str) -> Optional[str]:
        """Extract energy class using dynamic content"""
        try:
            page_text = await page.inner_text('body')
            energy_patterns = [
                r'ενεργειακή\s+κλάση\s*[:\-]?\s*([A-G][+]?)',
                r'energy\s+class\s*[:\-]?\s*([A-G][+]?)',
                r'κλάση\s+([A-G][+]?)',
                r'class\s+([A-G][+]?)',
                r'ενεργειακό\s+πιστοποιητικό\s*[:\-]?\s*([A-G][+]?)'
            ]
            
            full_text = page_text + html
            
            for pattern in energy_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    energy_class = match.group(1).upper()
                    if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F']:
                        return energy_class
        except:
            pass
        
        return None
    
    def is_property_page_content(self, html: str, neighborhood: str) -> bool:
        """Check if HTML contains actual property content"""
        
        html_lower = html.lower()
        
        # Must have property-related content
        property_indicators = ['τιμή', 'price', 'τ.μ', 'sqm', 'm²', 'ενοικίαση', 'πώληση', 'διαμέρισμα']
        if not any(indicator in html_lower for indicator in property_indicators):
            return False
        
        # Should mention location
        location_indicators = ['αθήνα', 'athens', neighborhood.lower()]
        has_location = any(indicator in html_lower for indicator in location_indicators)
        
        # Check content length (real property pages should be substantial)
        if len(html) < 5000:  # Too short to be a real property page
            return False
        
        return has_location or len(html) > 20000  # Either has location or is very detailed
    
    def generate_property_id(self, url: str) -> str:
        """Generate property ID"""
        url_match = re.search(r'/(\d+)', url)
        if url_match:
            return f"xe_gr_{url_match.group(1)}"
        else:
            return f"xe_gr_{hashlib.md5(url.encode()).hexdigest()[:8]}"
    
    def calculate_confidence(self, data: Dict) -> float:
        """Calculate confidence"""
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
        
        # Bonus fields
        for field in ['energy_class', 'floor']:
            total_checks += 0.5
            if data.get(field):
                confidence += 0.5
        
        return confidence / total_checks if total_checks > 0 else 0.0
    
    def generate_flags(self, data: Dict) -> List[str]:
        """Generate validation flags"""
        flags = ['xe_gr_verified', 'playwright_dynamic']
        
        if data.get('address') and self.validate_athens_address(data['address']):
            flags.append('athens_verified')
        
        if data.get('price') and 50 <= data['price'] <= 5000000:
            flags.append('price_realistic')
        
        if data.get('sqm') and 10 <= data['sqm'] <= 500:
            flags.append('area_realistic')
        
        if data.get('energy_class'):
            flags.append('energy_found')
        
        if data.get('extraction_confidence', 0) > 0.7:
            flags.append('high_confidence')
        
        return flags
    
    def validate_property(self, prop: RealPropertyData) -> bool:
        """Validate property"""
        if not prop.url or not prop.property_id:
            return False
        
        if not prop.address or not self.validate_athens_address(prop.address):
            return False
        
        # Must have at least price OR sqm
        if not prop.price and not prop.sqm:
            return False
        
        # Price validation
        if prop.price and not (50 <= prop.price <= 5000000):
            return False
        
        # Area validation
        if prop.sqm and not (10 <= prop.sqm <= 500):
            return False
        
        # Minimum confidence
        if prop.extraction_confidence < 0.3:
            return False
        
        return True

async def main():
    """Test Playwright scraper"""
    
    logger.info("🎭 TESTING PLAYWRIGHT XE.GR SCRAPER")
    logger.info("🚀 Browser automation for dynamic content")
    
    scraper = PlaywrightXEScraper()
    
    # Test with Kolonaki
    properties = await scraper.scrape_properties_dynamic('Κολωνάκι', max_properties=5)
    
    logger.info(f"\n🎯 PLAYWRIGHT RESULTS: {len(properties)} properties")
    
    if properties:
        for i, prop in enumerate(properties, 1):
            logger.info(f"\n📊 PROPERTY {i}:")
            logger.info(f"   Address: {prop.address}")
            logger.info(f"   Price: €{prop.price}")
            logger.info(f"   Area: {prop.sqm}m²")
            logger.info(f"   Rooms: {prop.rooms}")
            logger.info(f"   Energy: {prop.energy_class}")
            logger.info(f"   Confidence: {prop.extraction_confidence:.2f}")
            logger.info(f"   URL: {prop.url}")
        
        # Save results
        output_data = [asdict(prop) for prop in properties]
        with open('outputs/playwright_results.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✅ PLAYWRIGHT SUCCESS!")
        logger.info(f"📄 Results saved: outputs/playwright_results.json")
        logger.info(f"🎭 {len(properties)} DYNAMIC properties extracted!")
    else:
        logger.warning("❌ No properties extracted")

if __name__ == "__main__":
    asyncio.run(main())