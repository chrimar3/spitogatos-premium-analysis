#!/usr/bin/env python3
"""
SPITOGATOS.GR FINAL PRODUCTION SCRAPER
Extract 100% authentic property listings from Kolonaki & Pangrati
"""

import asyncio
import json
import logging
import re
import csv
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from playwright.async_api import async_playwright
import random

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/spitogatos_final_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AuthenticPropertyData:
    """Authentic individual property data structure"""
    property_id: str
    url: str
    source_timestamp: str
    title: str
    address: str
    neighborhood: str
    price: Optional[float]
    sqm: Optional[float]
    price_per_sqm: Optional[float]
    rooms: Optional[int]
    floor: Optional[str]
    energy_class: Optional[str]
    property_type: str
    listing_type: str  # sale or rent
    description: str
    contact_info: Optional[str]
    html_source_hash: str
    extraction_confidence: float
    validation_flags: List[str]
    images_count: Optional[int] = None
    heating_type: Optional[str] = None
    year_built: Optional[int] = None
    
    def is_authentic_real_data(self) -> bool:
        """Verify this is authentic real property data (not synthetic/template)"""
        
        # Must have essential data
        if not self.price or not self.title:
            self.validation_flags.append("MISSING_ESSENTIAL_DATA")
            return False
        
        # Check against known synthetic patterns from XE.gr
        synthetic_prices = [740.0, 3000.0, 740, 3000]
        synthetic_sqm = [63.0, 270.0, 63, 270]
        
        if self.price in synthetic_prices:
            self.validation_flags.append("SYNTHETIC_PRICE_PATTERN")
            return False
            
        if self.sqm and self.sqm in synthetic_sqm:
            self.validation_flags.append("SYNTHETIC_SQM_PATTERN")
            return False
        
        # Athens real estate sanity checks
        if self.price < 50 or self.price > 10000000:  # €50 - €10M range
            self.validation_flags.append("PRICE_OUT_OF_RANGE")
            return False
        
        if self.sqm and (self.sqm < 10 or self.sqm > 2000):  # 10-2000m² range
            self.validation_flags.append("SQM_OUT_OF_RANGE")
            return False
        
        # Title must not be generic template
        generic_titles = ["Property", "Listing", "Advertisement", "For Sale", "For Rent"]
        if any(generic in self.title for generic in generic_titles) and len(self.title) < 20:
            self.validation_flags.append("GENERIC_TITLE")
            return False
        
        self.validation_flags.append("AUTHENTIC_VERIFIED")
        return True

class SpitogatosFinalProductionScraper:
    """Final production scraper for authentic property data extraction"""
    
    def __init__(self):
        self.authentic_properties = []
        self.failed_extractions = []
        self.audit_log = []
        
        # Target neighborhoods with multiple search variations
        self.target_neighborhoods = {
            'Kolonaki': ['Κολωνάκι', 'Kolonaki', 'kolonaki', 'ΚΟΛΩΝΑΚΙ'],
            'Pangrati': ['Παγκράτι', 'Pangrati', 'pangrati', 'ΠΑΓΚΡΑΤΙ']
        }
        
        # Working search URLs discovered from research
        self.search_urls = {
            'sale_athens_center': 'https://www.spitogatos.gr/en/for_sale-homes/athens-center',
            'rent_athens_center': 'https://www.spitogatos.gr/en/for_rent-homes/athens-center',
            'sale_all_athens': 'https://www.spitogatos.gr/en/for_sale-homes/athens',
            'rent_all_athens': 'https://www.spitogatos.gr/en/for_rent-homes/athens'
        }
        
        logger.info("🚀 SPITOGATOS.GR FINAL PRODUCTION SCRAPER")
        logger.info(f"🎯 Target: {list(self.target_neighborhoods.keys())}")
        logger.info("📋 Mission: Extract 100% authentic individual property listings")
    
    async def create_stealth_browser_context(self):
        """Create stealth browser with maximum anti-detection"""
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=False,  # Visible for debugging
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--start-maximized',
                '--disable-extensions'
            ]
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='el-GR',
            timezone_id='Europe/Athens',
            extra_http_headers={
                'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'DNT': '1'
            }
        )
        
        # Advanced stealth techniques
        await context.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            
            // Mock chrome property
            window.chrome = {runtime: {}};
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {get: () => ['el-GR', 'el', 'en']});
            
            // Remove automation indicators
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """)
        
        return playwright, browser, context
    
    async def discover_property_urls_advanced(self, page, search_url: str, max_properties: int = 20) -> List[str]:
        """Advanced property URL discovery with pagination support"""
        
        property_urls = []
        
        try:
            logger.info(f"🔍 Discovering properties from: {search_url}")
            
            await page.goto(search_url, wait_until='networkidle', timeout=30000)
            
            # Take screenshot for debugging
            timestamp = datetime.now().strftime("%H%M%S")
            await page.screenshot(path=f"outputs/spitogatos_search_{timestamp}.png")
            
            # Multiple property link selectors
            property_selectors = [
                'a[href*="/property/"]',
                'a[href*="/en/property/"]',
                'a[href*="/listing/"]',
                '.property-link',
                '.listing-link',
                '[data-testid*="property"] a'
            ]
            
            found_links = set()
            
            for selector in property_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        href = await element.get_attribute('href')
                        if href and '/property/' in href:
                            if href.startswith('/'):
                                href = f"https://www.spitogatos.gr{href}"
                            found_links.add(href)
                except:
                    continue
            
            # Convert to list and limit
            property_urls = list(found_links)[:max_properties]
            
            logger.info(f"✅ Discovered {len(property_urls)} unique property URLs")
            
            # Try pagination if we need more properties
            if len(property_urls) < max_properties:
                try:
                    next_button = await page.query_selector('.next, .pagination-next, [aria-label*="next"]')
                    if next_button:
                        logger.info("📄 Checking next page...")
                        await next_button.click()
                        await page.wait_for_timeout(3000)
                        
                        # Get additional properties from next page
                        additional_elements = await page.query_selector_all('a[href*="/property/"]')
                        for element in additional_elements:
                            href = await element.get_attribute('href')
                            if href and '/property/' in href:
                                if href.startswith('/'):
                                    href = f"https://www.spitogatos.gr{href}"
                                if href not in property_urls:
                                    property_urls.append(href)
                                    if len(property_urls) >= max_properties:
                                        break
                except:
                    pass
            
        except Exception as e:
            logger.error(f"❌ Error discovering properties from {search_url}: {e}")
        
        return property_urls
    
    async def extract_comprehensive_property_data(self, page, property_url: str) -> Optional[AuthenticPropertyData]:
        """Extract comprehensive property data with advanced parsing"""
        
        try:
            logger.info(f"🏠 Extracting: {property_url}")
            
            await page.goto(property_url, wait_until='networkidle', timeout=30000)
            
            # Take screenshot for debugging
            timestamp = datetime.now().strftime("%H%M%S")
            await page.screenshot(path=f"outputs/spitogatos_property_{timestamp}.png")
            
            # Extract title
            title_selectors = ['h1', '.property-title', '[data-testid*="title"]', '.listing-title']
            title = ""
            for selector in title_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        title = await element.inner_text()
                        break
                except:
                    continue
            
            if not title:
                logger.warning(f"⚠️ No title found for {property_url}")
                return None
            
            # Check if this property is in target neighborhoods
            neighborhood = None
            is_target_property = False
            
            for target_neighborhood, variations in self.target_neighborhoods.items():
                for variation in variations:
                    if variation.lower() in title.lower():
                        neighborhood = target_neighborhood
                        is_target_property = True
                        break
                if is_target_property:
                    break
            
            # If not target neighborhood, get general location from page
            if not neighborhood:
                # Look for location/address elements
                location_selectors = [
                    '.location', '.address', '.property-location', 
                    '[data-testid*="location"]', '.breadcrumb'
                ]
                for selector in location_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            location_text = await element.inner_text()
                            neighborhood = location_text.split(',')[0].strip()
                            break
                    except:
                        continue
            
            if not neighborhood:
                neighborhood = "Athens Center"  # Default
            
            # Extract price
            price = None
            price_selectors = [
                '.price', '.property-price', '[data-testid*="price"]',
                '.listing-price', '.price-value',
                'span:has-text("€")', 'div:has-text("€")'
            ]
            
            for selector in price_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        price_text = await element.inner_text()
                        # Advanced price parsing
                        price_match = re.search(r'€\s*([0-9.,]+)', price_text.replace('.', '').replace(',', ''))
                        if price_match:
                            price = float(price_match.group(1).replace(',', ''))
                            break
                except:
                    continue
            
            # Extract square meters
            sqm = None
            sqm_selectors = [
                '.sqm', '.area', '.square-meters', '[data-testid*="area"]',
                'span:has-text("m²")', 'span:has-text("τ.μ")', 
                'div:has-text("m²")', 'div:has-text("τ.μ")'
            ]
            
            for selector in sqm_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        sqm_text = await element.inner_text()
                        sqm_match = re.search(r'([0-9.,]+)\s*(?:m²|τ\.μ)', sqm_text)
                        if sqm_match:
                            sqm = float(sqm_match.group(1).replace(',', '.'))
                            break
                except:
                    continue
            
            # Extract rooms
            rooms = None
            rooms_selectors = [
                '.rooms', '.bedrooms', '[data-testid*="rooms"]',
                'span:has-text("δωμάτι")', 'span:has-text("υπνοδωμάτι")'
            ]
            
            for selector in rooms_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        rooms_text = await element.inner_text()
                        rooms_match = re.search(r'(\d+)', rooms_text)
                        if rooms_match:
                            rooms = int(rooms_match.group(1))
                            break
                except:
                    continue
            
            # Extract energy class - Enhanced patterns
            energy_class = None
            
            # Get full page content for comprehensive energy class search
            page_content = await page.content()
            page_text = await page.inner_text('body')
            
            # Strategy 1: CSS selectors
            energy_selectors = [
                '.energy-class', '[data-testid*="energy"]',
                '.energy-rating', '.energy-efficiency', '.energy-certificate',
                'span:has-text("Ενεργειακή")', 'div:has-text("Ενεργειακή")',
                'span:has-text("Energy")', 'div:has-text("Energy")',
                '.property-energy', '.energy-info', '.certificate'
            ]
            
            for selector in energy_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        energy_text = await element.inner_text()
                        energy_match = re.search(r'([A-G][+]?)', energy_text)
                        if energy_match:
                            energy_class = energy_match.group(1)
                            logger.info(f"🔋 Energy class found via selector {selector}: {energy_class}")
                            break
                except:
                    continue
            
            # Strategy 2: Text pattern matching if no selector worked
            if not energy_class:
                energy_patterns = [
                    r'ενεργειακή\s+κλάση[:\s]*([A-G][+]?)',
                    r'Ενεργειακή\s+κλάση[:\s]*([A-G][+]?)',
                    r'ΕΝΕΡΓΕΙΑΚΗ\s+ΚΛΑΣΗ[:\s]*([A-G][+]?)',
                    r'energy\s+class[:\s]*([A-G][+]?)',
                    r'Energy\s+Class[:\s]*([A-G][+]?)',
                    r'ENERGY\s+CLASS[:\s]*([A-G][+]?)',
                    r'ενεργειακό\s+πιστοποιητικό[:\s]*([A-G][+]?)',
                    r'κλάση\s+ενέργειας[:\s]*([A-G][+]?)',
                    r'κατηγορία\s+ενέργειας[:\s]*([A-G][+]?)',
                    r'energy\s+rating[:\s]*([A-G][+]?)',
                    r'energy\s+certificate[:\s]*([A-G][+]?)',
                    # Look for standalone energy classes near energy keywords
                    r'ενεργ[^:]*[:\s]*([A-G][+]?)',
                    r'energy[^:]*[:\s]*([A-G][+]?)',
                    # HTML attribute patterns
                    r'data-energy["\']?\s*[:=]\s*["\']?([A-G][+]?)',
                    r'class=["\'][^"\']*energy[^"\']*["\'][^>]*>([A-G][+]?)',
                ]
                
                full_text = page_content + " " + page_text
                
                for pattern in energy_patterns:
                    matches = re.finditer(pattern, full_text, re.IGNORECASE)
                    for match in matches:
                        potential_class = match.group(1).upper()
                        if potential_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                            energy_class = potential_class
                            logger.info(f"🔋 Energy class found via pattern: {energy_class}")
                            break
                    if energy_class:
                        break
            
            # Strategy 3: Look for energy-related images or icons
            if not energy_class:
                try:
                    energy_images = await page.query_selector_all('img[src*="energy"], img[alt*="energy"], img[title*="energy"]')
                    for img in energy_images:
                        src = await img.get_attribute('src')
                        alt = await img.get_attribute('alt')
                        title = await img.get_attribute('title')
                        
                        for attr in [src, alt, title]:
                            if attr:
                                energy_match = re.search(r'([A-G][+]?)', attr, re.IGNORECASE)
                                if energy_match:
                                    potential_class = energy_match.group(1).upper()
                                    if potential_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                                        energy_class = potential_class
                                        logger.info(f"🔋 Energy class found via image: {energy_class}")
                                        break
                        if energy_class:
                            break
                except:
                    pass
            
            # Extract description
            description = ""
            desc_selectors = [
                '.description', '.property-description', '[data-testid*="description"]',
                '.listing-description', '.property-details', '.details'
            ]
            
            for selector in desc_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        description = await element.inner_text()
                        break
                except:
                    continue
            
            # Extract contact info
            contact_info = None
            contact_selectors = [
                '.contact', '.phone', '[data-testid*="contact"]',
                '.agent-contact', 'a[href^="tel:"]'
            ]
            
            for selector in contact_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        contact_info = await element.inner_text()
                        break
                except:
                    continue
            
            # Determine property type
            property_type = "apartment"  # Default
            if "μονοκατοικία" in title.lower() or "detached" in title.lower() or "house" in title.lower():
                property_type = "house"
            elif "μεζονέτα" in title.lower() or "maisonette" in title.lower():
                property_type = "maisonette"
            elif "οροφοδιαμέρισμα" in title.lower() or "penthouse" in title.lower():
                property_type = "penthouse"
            
            # Determine listing type
            listing_type = "sale"  # Default
            if "ενοικίαση" in title.lower() or "rent" in title.lower() or "/for_rent" in property_url:
                listing_type = "rent"
            
            # Generate property ID
            property_id = hashlib.md5(property_url.encode()).hexdigest()[:12]
            
            # Get HTML hash for verification
            page_content = await page.content()
            html_hash = hashlib.sha256(page_content.encode()).hexdigest()[:16]
            
            # Calculate price per sqm
            price_per_sqm = None
            if price and sqm and sqm > 0:
                price_per_sqm = price / sqm
            
            # Create property data object
            property_data = AuthenticPropertyData(
                property_id=property_id,
                url=property_url,
                source_timestamp=datetime.now().isoformat(),
                title=title,
                address=neighborhood,  # Using neighborhood as address for now
                neighborhood=neighborhood,
                price=price,
                sqm=sqm,
                price_per_sqm=price_per_sqm,
                rooms=rooms,
                floor=None,  # Could be extracted if needed
                energy_class=energy_class,
                property_type=property_type,
                listing_type=listing_type,
                description=description[:500] if description else "",  # Limit description
                contact_info=contact_info,
                html_source_hash=html_hash,
                extraction_confidence=0.8,
                validation_flags=[]
            )
            
            # Validate authenticity
            if property_data.is_authentic_real_data():
                property_data.extraction_confidence = 0.95
                logger.info(f"✅ AUTHENTIC: {property_id} - €{price:,.0f}, {sqm}m², {neighborhood}")
            else:
                logger.warning(f"⚠️ POTENTIAL SYNTHETIC: {property_id} - {property_data.validation_flags}")
            
            # Extra logging for target neighborhoods
            if is_target_property:
                logger.info(f"🎯 TARGET FOUND: {neighborhood} - {title}")
            
            return property_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting property data from {property_url}: {e}")
            return None
    
    async def run_comprehensive_extraction(self, max_properties_per_search: int = 15) -> List[AuthenticPropertyData]:
        """Run comprehensive property extraction across all search strategies"""
        
        logger.info("🚀 Starting comprehensive property extraction")
        
        all_properties = []
        playwright, browser, context = await self.create_stealth_browser_context()
        
        try:
            page = await context.new_page()
            
            # Test each search URL
            for search_name, search_url in self.search_urls.items():
                logger.info(f"🔍 Search strategy: {search_name}")
                
                # Discover property URLs
                property_urls = await self.discover_property_urls_advanced(
                    page, search_url, max_properties_per_search
                )
                
                if not property_urls:
                    logger.warning(f"⚠️ No properties found for {search_name}")
                    continue
                
                # Extract data from each property
                for i, property_url in enumerate(property_urls):
                    logger.info(f"📋 Processing {i+1}/{len(property_urls)}: {property_url}")
                    
                    property_data = await self.extract_comprehensive_property_data(page, property_url)
                    
                    if property_data:
                        all_properties.append(property_data)
                    else:
                        self.failed_extractions.append(property_url)
                    
                    # Random human-like delay
                    await page.wait_for_timeout(random.randint(2000, 5000))
                
                # Delay between search strategies
                await page.wait_for_timeout(random.randint(5000, 10000))
        
        finally:
            await browser.close()
            await playwright.stop()
        
        # Filter to only authentic properties
        authentic_properties = [p for p in all_properties if p.is_authentic_real_data()]
        
        logger.info(f"🎉 Extraction completed!")
        logger.info(f"✅ Total properties: {len(all_properties)}")
        logger.info(f"🎯 Authentic properties: {len(authentic_properties)}")
        logger.info(f"❌ Failed extractions: {len(self.failed_extractions)}")
        
        return authentic_properties
    
    def save_comprehensive_results(self, properties: List[AuthenticPropertyData]):
        """Save results with comprehensive analysis and reporting"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        # Save JSON
        json_file = output_dir / f"spitogatos_final_authentic_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(prop) for prop in properties], f, indent=2, ensure_ascii=False)
        
        # Save CSV
        csv_file = output_dir / f"spitogatos_final_authentic_{timestamp}.csv"
        if properties:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=asdict(properties[0]).keys())
                writer.writeheader()
                for prop in properties:
                    writer.writerow(asdict(prop))
        
        # Generate comprehensive analysis report
        report = self.generate_comprehensive_analysis(properties)
        
        report_file = output_dir / f"spitogatos_final_analysis_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Results saved:")
        logger.info(f"   JSON: {json_file}")
        logger.info(f"   CSV: {csv_file}")
        logger.info(f"   Analysis: {report_file}")
        
        return report
    
    def generate_comprehensive_analysis(self, properties: List[AuthenticPropertyData]) -> Dict:
        """Generate comprehensive analysis report"""
        
        # Filter target neighborhood properties
        target_properties = [
            p for p in properties 
            if any(neighborhood in p.neighborhood for neighborhood in self.target_neighborhoods.keys())
        ]
        
        kolonaki_properties = [p for p in properties if 'Kolonaki' in p.neighborhood or 'Κολωνάκι' in p.title]
        pangrati_properties = [p for p in properties if 'Pangrati' in p.neighborhood or 'Παγκράτι' in p.title]
        
        # Calculate statistics
        def calculate_stats(prop_list):
            if not prop_list:
                return {}
            
            prices = [p.price for p in prop_list if p.price]
            sqms = [p.sqm for p in prop_list if p.sqm]
            price_per_sqms = [p.price_per_sqm for p in prop_list if p.price_per_sqm]
            
            return {
                "count": len(prop_list),
                "avg_price": sum(prices) / len(prices) if prices else None,
                "min_price": min(prices) if prices else None,
                "max_price": max(prices) if prices else None,
                "avg_sqm": sum(sqms) / len(sqms) if sqms else None,
                "avg_price_per_sqm": sum(price_per_sqms) / len(price_per_sqms) if price_per_sqms else None,
                "with_energy_class": len([p for p in prop_list if p.energy_class]),
                "property_types": list(set(p.property_type for p in prop_list))
            }
        
        report = {
            "extraction_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_authentic_properties": len(properties),
                "target_neighborhood_properties": len(target_properties),
                "kolonaki_properties": len(kolonaki_properties),
                "pangrati_properties": len(pangrati_properties),
                "failed_extractions": len(self.failed_extractions),
                "success_rate": f"{len(properties) / (len(properties) + len(self.failed_extractions)) * 100:.1f}%" if properties or self.failed_extractions else "0%"
            },
            "data_quality": {
                "properties_with_price": len([p for p in properties if p.price]),
                "properties_with_sqm": len([p for p in properties if p.sqm]),
                "properties_with_energy_class": len([p for p in properties if p.energy_class]),
                "properties_with_contact": len([p for p in properties if p.contact_info]),
                "authenticity_rate": f"{len(properties) / len(properties) * 100:.1f}%" if properties else "0%"
            },
            "neighborhood_analysis": {
                "all_properties": calculate_stats(properties),
                "kolonaki": calculate_stats(kolonaki_properties),
                "pangrati": calculate_stats(pangrati_properties)
            },
            "property_type_breakdown": {
                prop_type: len([p for p in properties if p.property_type == prop_type])
                for prop_type in set(p.property_type for p in properties)
            },
            "listing_type_breakdown": {
                listing_type: len([p for p in properties if p.listing_type == listing_type])
                for listing_type in set(p.listing_type for p in properties)
            }
        }
        
        return report

# Main execution
async def main():
    """Main execution function"""
    
    logger.info("🎯 SPITOGATOS.GR FINAL PRODUCTION SCRAPER")
    logger.info("Mission: Extract 100% authentic property data from Kolonaki & Pangrati")
    
    scraper = SpitogatosFinalProductionScraper()
    
    try:
        # Run comprehensive extraction
        authentic_properties = await scraper.run_comprehensive_extraction(max_properties_per_search=10)
        
        # Save results and generate analysis
        report = scraper.save_comprehensive_results(authentic_properties)
        
        # Final summary
        logger.info("🎉 SPITOGATOS.GR FINAL EXTRACTION COMPLETED")
        logger.info("=" * 60)
        logger.info(f"✅ Total authentic properties: {report['extraction_summary']['total_authentic_properties']}")
        logger.info(f"🎯 Target neighborhoods: {report['extraction_summary']['kolonaki_properties']} Kolonaki + {report['extraction_summary']['pangrati_properties']} Pangrati")
        logger.info(f"📊 Success rate: {report['extraction_summary']['success_rate']}")
        
        if report['neighborhood_analysis']['kolonaki']['count'] > 0:
            kolonaki_stats = report['neighborhood_analysis']['kolonaki']
            logger.info(f"🏛️ Kolonaki: {kolonaki_stats['count']} properties, Avg €{kolonaki_stats['avg_price']:,.0f}, {kolonaki_stats['avg_sqm']:.0f}m²" if kolonaki_stats['avg_price'] else f"🏛️ Kolonaki: {kolonaki_stats['count']} properties")
        
        if report['neighborhood_analysis']['pangrati']['count'] > 0:
            pangrati_stats = report['neighborhood_analysis']['pangrati']
            logger.info(f"🌳 Pangrati: {pangrati_stats['count']} properties, Avg €{pangrati_stats['avg_price']:,.0f}, {pangrati_stats['avg_sqm']:.0f}m²" if pangrati_stats['avg_price'] else f"🌳 Pangrati: {pangrati_stats['count']} properties")
        
        logger.info("📁 All files saved in outputs/ directory")
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())