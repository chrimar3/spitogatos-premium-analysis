#!/usr/bin/env python3
"""
SPITOGATOS.GR PRODUCTION-READY SCRAPER
Comprehensive solution for extracting real Greek property data
Target: Individual property listings in Kolonaki & Pangrati, Athens
"""

import asyncio
import json
import logging
import re
import csv
import hashlib
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urljoin, urlparse
import aiohttp
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/spitogatos_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RealPropertyData:
    """Real individual property data structure"""
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
    property_type: str
    listing_type: str  # sale or rent
    contact_info: Optional[str]
    html_source_hash: str
    extraction_confidence: float
    validation_flags: List[str]
    extraction_method: str = "spitogatos_production"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images_count: Optional[int] = None
    created_date: Optional[str] = None
    updated_date: Optional[str] = None

    def is_authentic(self) -> bool:
        """Check if property data appears authentic (not template/synthetic)"""
        if not self.price or not self.sqm:
            return False
            
        # Check for common synthetic data patterns from XE.gr analysis
        synthetic_prices = [740, 3000, 740.0, 3000.0]
        synthetic_sqm = [63, 270, 63.0, 270.0]
        
        if self.price in synthetic_prices or self.sqm in synthetic_sqm:
            self.validation_flags.append("POTENTIAL_SYNTHETIC_DATA")
            return False
            
        # Price sanity checks for Athens real estate
        if self.price < 50 or self.price > 5000000:
            self.validation_flags.append("PRICE_OUT_OF_RANGE")
            return False
            
        # SQM sanity checks
        if self.sqm < 10 or self.sqm > 1000:
            self.validation_flags.append("SQM_OUT_OF_RANGE")
            return False
            
        return True

class SpitogatosProductionScraper:
    """Production-ready scraper for Spitogatos.gr with advanced anti-detection"""
    
    def __init__(self):
        self.scraped_properties = []
        self.failed_urls = []
        self.audit_log = []
        self.session_data = {}
        
        # Target neighborhoods in Athens
        self.target_neighborhoods = {
            'Κολωνάκι': 'Kolonaki',
            'Παγκράτι': 'Pangrati'
        }
        
        # Base URLs discovered from research
        self.base_urls = {
            'main': 'https://www.spitogatos.gr',
            'search': 'https://www.spitogatos.gr/search',
            'sale': 'https://www.spitogatos.gr/for_sale-homes',
            'rent': 'https://www.spitogatos.gr/for_rent-homes'
        }
        
        # Stealth browser configuration
        self.browser_config = {
            'headless': False,  # Start with visible browser for testing
            'args': [
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--start-maximized',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',  # Speed optimization
                '--disable-javascript=false'  # Keep JS enabled
            ]
        }
        
        logger.info("🚀 SPITOGATOS.GR PRODUCTION SCRAPER INITIALIZED")
        logger.info(f"🎯 Target neighborhoods: {list(self.target_neighborhoods.keys())}")
    
    async def create_stealth_browser(self) -> Tuple[Browser, BrowserContext]:
        """Create stealth browser with anti-detection measures"""
        
        playwright = await async_playwright().start()
        
        # Launch browser with stealth configuration
        browser = await playwright.chromium.launch(**self.browser_config)
        
        # Create context with realistic user agent and settings
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='el-GR',
            timezone_id='Europe/Athens',
            extra_http_headers={
                'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        # Add stealth script to avoid detection
        await context.add_init_script("""
            // Override the `navigator.webdriver` property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Override the `window.chrome` property
            window.chrome = {
                runtime: {},
            };
            
            // Override plugins length
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['el-GR', 'el', 'en'],
            });
        """)
        
        return browser, context
    
    async def handle_anti_bot_protection(self, page: Page, url: str) -> bool:
        """Handle anti-bot protection measures"""
        
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Check for common anti-bot patterns
            page_content = await page.content()
            
            # Detect "Pardon Our Interruption" page
            if "Pardon Our Interruption" in page_content:
                logger.warning("🚫 Anti-bot protection detected - waiting for challenge")
                
                # Wait for potential automatic redirect or cookie setting
                await page.wait_for_timeout(random.randint(5000, 10000))
                
                # Check if page changed
                new_content = await page.content()
                if new_content != page_content:
                    logger.info("✅ Anti-bot challenge passed automatically")
                    return True
                else:
                    logger.error("❌ Failed to bypass anti-bot protection")
                    return False
            
            # Check if page loaded successfully
            title = await page.title()
            if "Spitogatos" in title or "σπίτι" in title.lower():
                logger.info("✅ Page loaded successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error handling anti-bot protection: {e}")
            return False
    
    async def discover_property_urls(self, page: Page, neighborhood: str, listing_type: str = "sale") -> List[str]:
        """Discover individual property listing URLs"""
        
        property_urls = []
        
        try:
            # Build search URL for specific neighborhood
            search_strategies = [
                f"{self.base_urls['main']}/search/homes/{listing_type}/athens/{neighborhood.lower()}",
                f"{self.base_urls['main']}/for_{listing_type}-homes/athens-{neighborhood.lower()}",
                f"{self.base_urls['main']}/en/for_{listing_type}-homes/athens-{neighborhood.lower()}",
                f"{self.base_urls['search']}?area={neighborhood}&type={listing_type}"
            ]
            
            for search_url in search_strategies:
                logger.info(f"🔍 Trying search strategy: {search_url}")
                
                if await self.handle_anti_bot_protection(page, search_url):
                    # Look for property listing links
                    property_links = await page.query_selector_all('a[href*="/properties/"]')
                    
                    if not property_links:
                        # Try alternative selectors
                        property_links = await page.query_selector_all('a[href*="/property/"]')
                    
                    if not property_links:
                        # Try general property page selectors
                        property_links = await page.query_selector_all('a[href*="/listing/"]')
                    
                    for link in property_links[:10]:  # Limit to first 10 properties per strategy
                        href = await link.get_attribute('href')
                        if href:
                            full_url = urljoin(self.base_urls['main'], href)
                            if full_url not in property_urls:
                                property_urls.append(full_url)
                                logger.info(f"📋 Found property URL: {full_url}")
                    
                    if property_urls:
                        break  # Success with this strategy
                
                # Random delay between strategies
                await page.wait_for_timeout(random.randint(2000, 5000))
            
        except Exception as e:
            logger.error(f"❌ Error discovering property URLs: {e}")
        
        logger.info(f"✅ Discovered {len(property_urls)} property URLs for {neighborhood}")
        return property_urls
    
    async def extract_property_data(self, page: Page, property_url: str, neighborhood: str) -> Optional[RealPropertyData]:
        """Extract comprehensive property data from individual listing page"""
        
        try:
            if not await self.handle_anti_bot_protection(page, property_url):
                logger.error(f"❌ Failed to access property page: {property_url}")
                return None
            
            # Take screenshot for debugging
            timestamp = datetime.now().strftime("%H%M%S")
            await page.screenshot(path=f"outputs/spitogatos_property_{timestamp}.png")
            
            # Extract basic property information
            title_element = await page.query_selector('h1, .property-title, [data-testid="property-title"]')
            title = await title_element.inner_text() if title_element else ""
            
            # Extract price
            price = None
            price_selectors = [
                '.price, .property-price, [data-testid="price"]',
                '.listing-price, .price-value',
                'span:has-text("€"), div:has-text("€")'
            ]
            
            for selector in price_selectors:
                price_element = await page.query_selector(selector)
                if price_element:
                    price_text = await price_element.inner_text()
                    price_match = re.search(r'€?\s*([0-9.,]+)', price_text.replace('.', '').replace(',', ''))
                    if price_match:
                        try:
                            price = float(price_match.group(1).replace(',', ''))
                            break
                        except ValueError:
                            continue
            
            # Extract square meters
            sqm = None
            sqm_selectors = [
                '.sqm, .square-meters, [data-testid="sqm"]',
                '.area, .property-area',
                'span:has-text("m²"), div:has-text("m²")',
                'span:has-text("τ.μ"), div:has-text("τ.μ")'
            ]
            
            for selector in sqm_selectors:
                sqm_element = await page.query_selector(selector)
                if sqm_element:
                    sqm_text = await sqm_element.inner_text()
                    sqm_match = re.search(r'([0-9.,]+)\s*(?:m²|τ\.μ)', sqm_text)
                    if sqm_match:
                        try:
                            sqm = float(sqm_match.group(1).replace(',', '.'))
                            break
                        except ValueError:
                            continue
            
            # Extract rooms
            rooms = None
            rooms_selectors = [
                '.rooms, .bedrooms, [data-testid="rooms"]',
                '.room-count',
                'span:has-text("δωμάτι"), div:has-text("δωμάτι")'
            ]
            
            for selector in rooms_selectors:
                rooms_element = await page.query_selector(selector)
                if rooms_element:
                    rooms_text = await rooms_element.inner_text()
                    rooms_match = re.search(r'(\d+)', rooms_text)
                    if rooms_match:
                        try:
                            rooms = int(rooms_match.group(1))
                            break
                        except ValueError:
                            continue
            
            # Extract energy class
            energy_class = None
            energy_selectors = [
                '.energy-class, [data-testid="energy-class"]',
                '.energy-rating',
                'span:has-text("Ενεργειακή"), div:has-text("Ενεργειακή")'
            ]
            
            for selector in energy_selectors:
                energy_element = await page.query_selector(selector)
                if energy_element:
                    energy_text = await energy_element.inner_text()
                    energy_match = re.search(r'([A-G][+]?)', energy_text)
                    if energy_match:
                        energy_class = energy_match.group(1)
                        break
            
            # Extract description
            description = ""
            desc_selectors = [
                '.description, .property-description, [data-testid="description"]',
                '.listing-description',
                '.property-details'
            ]
            
            for selector in desc_selectors:
                desc_element = await page.query_selector(selector)
                if desc_element:
                    description = await desc_element.inner_text()
                    break
            
            # Extract address
            address = ""
            address_selectors = [
                '.address, .property-address, [data-testid="address"]',
                '.location',
                '.property-location'
            ]
            
            for selector in address_selectors:
                addr_element = await page.query_selector(selector)
                if addr_element:
                    address = await addr_element.inner_text()
                    break
            
            # Extract contact information
            contact_info = None
            contact_selectors = [
                '.contact, .phone, [data-testid="contact"]',
                '.agent-contact',
                'a[href^="tel:"]'
            ]
            
            for selector in contact_selectors:
                contact_element = await page.query_selector(selector)
                if contact_element:
                    contact_info = await contact_element.inner_text()
                    break
            
            # Determine property type and listing type
            property_type = "apartment"  # Default
            listing_type = "sale"  # Default
            
            if "μονοκατοικία" in title.lower() or "villa" in title.lower():
                property_type = "house"
            elif "μεζονέτα" in title.lower() or "maisonette" in title.lower():
                property_type = "maisonette"
            
            if "ενοικίαση" in title.lower() or "rent" in title.lower():
                listing_type = "rent"
            
            # Generate property ID
            property_id = hashlib.md5(property_url.encode()).hexdigest()[:12]
            
            # Calculate HTML source hash for authenticity verification
            page_content = await page.content()
            html_hash = hashlib.sha256(page_content.encode()).hexdigest()[:16]
            
            # Create property data object
            property_data = RealPropertyData(
                property_id=property_id,
                url=property_url,
                source_timestamp=datetime.now().isoformat(),
                address=address,
                neighborhood=neighborhood,
                price=price,
                sqm=sqm,
                rooms=rooms,
                floor=None,  # Extract if available
                energy_class=energy_class,
                title=title,
                description=description,
                property_type=property_type,
                listing_type=listing_type,
                contact_info=contact_info,
                html_source_hash=html_hash,
                extraction_confidence=0.8,  # Base confidence
                validation_flags=[],
                images_count=None  # Extract if needed
            )
            
            # Validate data authenticity
            if property_data.is_authentic():
                property_data.validation_flags.append("AUTHENTIC_DATA")
                property_data.extraction_confidence = 0.9
                logger.info(f"✅ Extracted authentic property: {property_id} - €{price}, {sqm}m²")
            else:
                logger.warning(f"⚠️ Potential synthetic data detected: {property_id}")
            
            return property_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting property data from {property_url}: {e}")
            return None
    
    async def scrape_properties(self, max_properties_per_area: int = 10) -> List[RealPropertyData]:
        """Main scraping method for all target neighborhoods"""
        
        logger.info(f"🚀 Starting Spitogatos.gr scraping - Target: {max_properties_per_area} properties per area")
        
        all_properties = []
        browser, context = await self.create_stealth_browser()
        
        try:
            page = await context.new_page()
            
            for greek_name, english_name in self.target_neighborhoods.items():
                logger.info(f"🎯 Scraping {greek_name} ({english_name})")
                
                # Try both sale and rental properties
                for listing_type in ["sale", "rent"]:
                    logger.info(f"📋 Looking for {listing_type} properties in {greek_name}")
                    
                    # Discover property URLs
                    property_urls = await self.discover_property_urls(page, english_name, listing_type)
                    
                    # Extract data from each property
                    for i, property_url in enumerate(property_urls[:max_properties_per_area]):
                        logger.info(f"🏠 Processing property {i+1}/{len(property_urls[:max_properties_per_area])}: {property_url}")
                        
                        property_data = await self.extract_property_data(page, property_url, greek_name)
                        
                        if property_data:
                            all_properties.append(property_data)
                            logger.info(f"✅ Successfully extracted: {property_data.property_id}")
                        else:
                            self.failed_urls.append(property_url)
                            logger.warning(f"❌ Failed to extract: {property_url}")
                        
                        # Random delay between properties
                        await page.wait_for_timeout(random.randint(2000, 5000))
                    
                    # Delay between listing types
                    await page.wait_for_timeout(random.randint(3000, 7000))
                
                # Delay between neighborhoods
                await page.wait_for_timeout(random.randint(5000, 10000))
        
        finally:
            await browser.close()
        
        logger.info(f"🎉 Scraping completed! Found {len(all_properties)} properties")
        return all_properties
    
    def save_results(self, properties: List[RealPropertyData], output_dir: str = "outputs"):
        """Save results in multiple formats with comprehensive reporting"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save as JSON
        json_file = output_path / f"spitogatos_properties_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(prop) for prop in properties], f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        csv_file = output_path / f"spitogatos_properties_{timestamp}.csv"
        if properties:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=asdict(properties[0]).keys())
                writer.writeheader()
                for prop in properties:
                    writer.writerow(asdict(prop))
        
        # Generate comprehensive report
        report_file = output_path / f"spitogatos_analysis_report_{timestamp}.json"
        
        authentic_properties = [p for p in properties if p.is_authentic()]
        
        report = {
            "extraction_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_properties_found": len(properties),
                "authentic_properties": len(authentic_properties),
                "potential_synthetic_data": len(properties) - len(authentic_properties),
                "success_rate": f"{len(properties) / (len(properties) + len(self.failed_urls)) * 100:.1f}%" if properties or self.failed_urls else "0%",
                "failed_urls_count": len(self.failed_urls)
            },
            "neighborhood_breakdown": {},
            "price_analysis": {},
            "data_quality_metrics": {
                "properties_with_sqm": len([p for p in authentic_properties if p.sqm]),
                "properties_with_energy_class": len([p for p in authentic_properties if p.energy_class]),
                "properties_with_contact": len([p for p in authentic_properties if p.contact_info])
            },
            "files_generated": {
                "json_file": str(json_file),
                "csv_file": str(csv_file),
                "log_file": "outputs/spitogatos_scraper.log"
            }
        }
        
        # Analyze by neighborhood
        for neighborhood in self.target_neighborhoods.keys():
            neighborhood_props = [p for p in authentic_properties if p.neighborhood == neighborhood]
            if neighborhood_props:
                prices = [p.price for p in neighborhood_props if p.price]
                sqms = [p.sqm for p in neighborhood_props if p.sqm]
                
                report["neighborhood_breakdown"][neighborhood] = {
                    "total_properties": len(neighborhood_props),
                    "avg_price": sum(prices) / len(prices) if prices else None,
                    "avg_sqm": sum(sqms) / len(sqms) if sqms else None,
                    "price_per_sqm": (sum(prices) / len(prices)) / (sum(sqms) / len(sqms)) if prices and sqms else None
                }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Results saved:")
        logger.info(f"   JSON: {json_file}")
        logger.info(f"   CSV: {csv_file}")
        logger.info(f"   Report: {report_file}")
        
        return report

# Main execution
async def main():
    """Main execution function"""
    
    scraper = SpitogatosProductionScraper()
    
    try:
        # Scrape properties from target neighborhoods
        properties = await scraper.scrape_properties(max_properties_per_area=5)
        
        # Save results and generate report
        report = scraper.save_results(properties)
        
        # Log final summary
        logger.info("🎯 SPITOGATOS.GR SCRAPING COMPLETED")
        logger.info(f"✅ Found {report['extraction_summary']['total_properties_found']} total properties")
        logger.info(f"✅ Authentic properties: {report['extraction_summary']['authentic_properties']}")
        logger.info(f"⚠️ Success rate: {report['extraction_summary']['success_rate']}")
        
        # Show neighborhood breakdown
        for neighborhood, data in report["neighborhood_breakdown"].items():
            logger.info(f"📍 {neighborhood}: {data['total_properties']} properties, Avg €{data['avg_price']:.0f}, {data['avg_sqm']:.0f}m²" if data['avg_price'] and data['avg_sqm'] else f"📍 {neighborhood}: {data['total_properties']} properties")
        
    except Exception as e:
        logger.error(f"❌ Critical error in main execution: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())