#!/usr/bin/env python3
"""
XE.GR FINAL BREAKTHROUGH SCRAPER
Using reconnaissance findings to extract real property data
"""

import asyncio
import json
import logging
import re
import csv
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XEBreakthroughScraper:
    """Final breakthrough scraper using reconnaissance intelligence"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.extracted_properties = []
        self.athens_neighborhoods = [
            "Κολωνάκι", "Παγκράτι", "Εξάρχεια", "Πλάκα", "Ψυρρή", 
            "Κυψέλη", "Αμπελόκηποι", "Γκάζι", "Νέος Κόσμος", "Πετράλωνα"
        ]
        
        # Working URLs discovered from reconnaissance
        self.working_base_urls = [
            "https://xe.gr/property",
            "https://www.xe.gr/property"
        ]
        
        # Property category URLs from reconnaissance
        self.category_urls = [
            "https://www.xe.gr/property/s/enoikiaseis-katoikion",  # rentals - residential
            "https://www.xe.gr/property/s/poliseis-katoikion",    # sales - residential
            "https://xe.gr/property/s/enoikiaseis-katoikion",
            "https://xe.gr/property/s/poliseis-katoikion"
        ]
    
    async def run_breakthrough_mission(self):
        """Execute final breakthrough scraping mission"""
        logger.info("🚀 XE.GR FINAL BREAKTHROUGH MISSION")
        logger.info("🎯 Objective: Extract REAL Athens property data")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                locale='el-GR'
            )
            
            try:
                page = await context.new_page()
                
                # Phase 1: Test category URLs for property listings
                logger.info("📋 PHASE 1: Category URL Property Discovery")
                await self.discover_properties_from_categories(page)
                
                # Phase 2: Use search system for Athens neighborhoods
                logger.info("🔍 PHASE 2: Athens Neighborhood Search")
                await self.search_athens_neighborhoods(page)
                
                # Phase 3: Extract data from discovered properties
                logger.info("📊 PHASE 3: Real Property Data Extraction")
                await self.extract_property_data(page)
                
                # Phase 4: Generate results
                logger.info("💾 PHASE 4: Results Export")
                await self.export_results()
                
            except Exception as e:
                logger.error(f"❌ Breakthrough mission failed: {e}")
            finally:
                # Keep browser open for 30 seconds to inspect results
                logger.info("🔍 Keeping browser open for inspection...")
                await asyncio.sleep(30)
                await browser.close()
    
    async def discover_properties_from_categories(self, page):
        """Discover individual property listings from category pages"""
        try:
            logger.info("🏘️ Testing category URLs for property listings...")
            
            for category_url in self.category_urls:
                logger.info(f"🧪 Testing category: {category_url}")
                
                try:
                    response = await page.goto(category_url, wait_until="networkidle", timeout=30000)
                    
                    if response and response.status == 200:
                        await asyncio.sleep(3)
                        
                        # Handle cookie consent if present
                        try:
                            cookie_btn = await page.wait_for_selector('button:has-text("ΣΥΜΦΩΝΩ")', timeout=3000)
                            if cookie_btn:
                                await cookie_btn.click()
                                await asyncio.sleep(2)
                        except:
                            pass
                        
                        # Look for property links using various selectors
                        property_selectors = [
                            'a[href*="/d/"]',
                            'a[href*="property/d/"]',
                            'a[href*="enoikiaseis"]',
                            'a[href*="poliseis"]',
                            '.property-item a',
                            '.listing a',
                            '.result-item a',
                            '[class*="property"] a',
                            '[class*="listing"] a',
                            '[data-testid*="property"] a'
                        ]
                        
                        found_properties = []
                        for selector in property_selectors:
                            try:
                                elements = await page.query_selector_all(selector)
                                for element in elements:
                                    href = await element.get_attribute('href')
                                    if href and self.is_property_url(href):
                                        if not href.startswith('http'):
                                            href = urljoin(category_url, href)
                                        
                                        found_properties.append({
                                            'url': href,
                                            'source_category': category_url,
                                            'selector': selector
                                        })
                            except:
                                continue
                        
                        # Remove duplicates
                        unique_properties = {}
                        for prop in found_properties:
                            unique_properties[prop['url']] = prop
                        
                        logger.info(f"🎯 Found {len(unique_properties)} properties in {category_url}")
                        
                        # Test first few properties to verify they work
                        for i, (url, prop_data) in enumerate(list(unique_properties.items())[:5]):
                            if await self.test_property_url(page, url):
                                self.extracted_properties.append({
                                    'url': url,
                                    'category_source': category_url,
                                    'discovery_method': 'category_scraping'
                                })
                            
                            await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Category URL failed {category_url}: {e}")
                    continue
                
                await asyncio.sleep(3)
        
        except Exception as e:
            logger.error(f"❌ Category discovery failed: {e}")
    
    async def search_athens_neighborhoods(self, page):
        """Search for properties in specific Athens neighborhoods"""
        try:
            logger.info("🏙️ Searching Athens neighborhoods...")
            
            # Go to search page
            search_url = "https://xe.gr/search"
            
            try:
                response = await page.goto(search_url, wait_until="networkidle", timeout=20000)
                
                if response and response.status == 200:
                    logger.info("✅ Search page accessible")
                    
                    for neighborhood in self.athens_neighborhoods[:5]:  # Test first 5
                        logger.info(f"🔍 Searching for properties in {neighborhood}")
                        
                        try:
                            # Find search input
                            search_input = None
                            input_selectors = [
                                'input[type="text"]',
                                'input[type="search"]',
                                'input[name*="search"]',
                                'input[name*="q"]',
                                'input[placeholder*="αναζήτηση"]',
                                '.search-input',
                                '#search'
                            ]
                            
                            for selector in input_selectors:
                                try:
                                    search_input = await page.wait_for_selector(selector, timeout=3000)
                                    if search_input and await search_input.is_visible():
                                        break
                                except:
                                    continue
                            
                            if search_input:
                                search_term = f"{neighborhood} διαμέρισμα"
                                await search_input.fill(search_term)
                                await page.keyboard.press('Enter')
                                await asyncio.sleep(5)
                                
                                # Look for search results
                                await self.extract_search_results(page, neighborhood)
                            
                        except Exception as e:
                            logger.warning(f"⚠️ Search failed for {neighborhood}: {e}")
                            continue
                        
                        await asyncio.sleep(3)
                
            except Exception as e:
                logger.warning(f"⚠️ Search page not accessible: {e}")
        
        except Exception as e:
            logger.error(f"❌ Neighborhood search failed: {e}")
    
    async def extract_search_results(self, page, neighborhood):
        """Extract property URLs from search results"""
        try:
            # Look for property links in search results
            result_selectors = [
                'a[href*="/d/"]',
                'a[href*="property"]',
                '.result a',
                '.listing a',
                '.property a',
                '[class*="result"] a',
                '[class*="listing"] a'
            ]
            
            found_results = []
            for selector in result_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        href = await element.get_attribute('href')
                        text = await element.inner_text()
                        
                        if href and self.is_property_url(href):
                            if not href.startswith('http'):
                                href = urljoin(page.url, href)
                            
                            found_results.append({
                                'url': href,
                                'text': text.strip()[:100],
                                'neighborhood': neighborhood,
                                'discovery_method': 'search_results'
                            })
                except:
                    continue
            
            logger.info(f"🎯 Found {len(found_results)} search results for {neighborhood}")
            
            # Test first few results
            for result in found_results[:3]:
                if await self.test_property_url(page, result['url']):
                    self.extracted_properties.append(result)
                await asyncio.sleep(2)
        
        except Exception as e:
            logger.error(f"❌ Search results extraction failed: {e}")
    
    def is_property_url(self, url: str) -> bool:
        """Check if URL looks like a property listing"""
        if not url:
            return False
        
        property_indicators = [
            '/d/', '/property/', '/enoikiaseis', '/poliseis',
            'diamerisma', 'apartment', 'house', 'katoikia'
        ]
        
        return any(indicator in url.lower() for indicator in property_indicators)
    
    async def test_property_url(self, page, url: str) -> bool:
        """Test if property URL contains real property data"""
        try:
            if not url.startswith('http'):
                url = f"https://xe.gr{url}" if url.startswith('/') else f"https://xe.gr/{url}"
            
            response = await page.goto(url, wait_until="load", timeout=15000)
            
            if response and response.status == 200:
                await asyncio.sleep(2)
                
                # Check for property content
                content = await page.content()
                property_indicators = [
                    'τιμή', 'price', 'τ.μ', 'm²', 'ενοικίαση', 'πώληση',
                    'διαμέρισμα', 'apartment', 'energy', 'ενεργειακή'
                ]
                
                indicator_count = sum(1 for indicator in property_indicators if indicator.lower() in content.lower())
                
                if indicator_count >= 3:
                    logger.info(f"✅ VERIFIED PROPERTY: {url}")
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"❌ Property URL test failed {url}: {e}")
            return False
    
    async def extract_property_data(self, page):
        """Extract detailed data from verified property URLs"""
        try:
            logger.info(f"📊 Extracting data from {len(self.extracted_properties)} verified properties...")
            
            for i, property_info in enumerate(self.extracted_properties):
                url = property_info['url']
                logger.info(f"📋 Extracting {i+1}/{len(self.extracted_properties)}: {url}")
                
                try:
                    response = await page.goto(url, wait_until="networkidle", timeout=20000)
                    
                    if response and response.status == 200:
                        await asyncio.sleep(3)
                        
                        # Extract property data
                        property_data = await self.extract_single_property(page, url)
                        
                        if property_data:
                            # Add discovery metadata
                            property_data.update({
                                'discovery_method': property_info.get('discovery_method', 'unknown'),
                                'source_category': property_info.get('category_source', ''),
                                'neighborhood_search': property_info.get('neighborhood', ''),
                                'extraction_timestamp': datetime.now().isoformat(),
                                'session_id': self.session_id
                            })
                            
                            self.extracted_properties[i] = property_data
                            logger.info(f"✅ Extracted: {property_data.get('title', 'No title')[:50]}...")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract {url}: {e}")
                    continue
                
                await asyncio.sleep(2)  # Respectful delay
        
        except Exception as e:
            logger.error(f"❌ Property data extraction failed: {e}")
    
    async def extract_single_property(self, page, url: str) -> Optional[Dict]:
        """Extract data from a single property page"""
        try:
            page_text = await page.inner_text('body')
            title = await page.title()
            
            # Extract key data with improved regex patterns
            property_data = {
                'url': url,
                'title': title,
                'raw_content_length': len(page_text)
            }
            
            # Price extraction
            price_patterns = [
                r'(\d{1,3}(?:\.\d{3})*)\s*€',
                r'€\s*(\d{1,3}(?:\.\d{3})*)',
                r'τιμή[:\s]*(\d{1,3}(?:\.\d{3})*)',
                r'price[:\s]*(\d{1,3}(?:\.\d{3})*)'
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    property_data['price'] = match.group(1)
                    break
            
            # SQM extraction
            sqm_patterns = [
                r'(\d+(?:[.,]\d+)?)\s*τ\.?μ\.?',
                r'(\d+(?:[.,]\d+)?)\s*m²',
                r'(\d+(?:[.,]\d+)?)\s*sq\.?m',
                r'εμβαδόν[:\s]*(\d+(?:[.,]\d+)?)'
            ]
            
            for pattern in sqm_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    property_data['sqm'] = match.group(1).replace(',', '.')
                    break
            
            # Energy class extraction
            energy_patterns = [
                r'ενεργειακή\s+κλάση[:\s]*([A-G][+\-]?)',
                r'energy\s+class[:\s]*([A-G][+\-]?)',
                r'ενεργειακό\s+πιστοποιητικό[:\s]*([A-G][+\-]?)'
            ]
            
            for pattern in energy_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    property_data['energy_class'] = match.group(1).upper()
                    break
            
            # Location/Address extraction
            location_patterns = [
                r'περιοχή[:\s]*([^,\n]+)',
                r'διεύθυνση[:\s]*([^,\n]+)',
                r'τοποθεσία[:\s]*([^,\n]+)',
                r'Αθήνα[,\s]*([^,\n]+)'
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    property_data['address'] = match.group(1).strip()
                    break
            
            # Property type
            type_patterns = [
                r'διαμέρισμα', r'μονοκατοικία', r'μεζονέτα', r'ρετιρέ',
                r'apartment', r'house', r'maisonette', r'penthouse'
            ]
            
            for pattern in type_patterns:
                if re.search(pattern, page_text, re.IGNORECASE):
                    property_data['property_type'] = pattern.capitalize()
                    break
            
            # Listing type (rental/sale)
            if re.search(r'ενοικίαση|rental|rent', page_text, re.IGNORECASE):
                property_data['listing_type'] = 'Ενοικίαση'
            elif re.search(r'πώληση|sale|sell', page_text, re.IGNORECASE):
                property_data['listing_type'] = 'Πώληση'
            
            # Rooms
            rooms_match = re.search(r'(\d+)\s*δωμάτι|(\d+)\s*room', page_text, re.IGNORECASE)
            if rooms_match:
                property_data['rooms'] = rooms_match.group(1) or rooms_match.group(2)
            
            # Floor
            floor_match = re.search(r'(\d+)ος\s*όροφος|(\d+)(st|nd|rd|th)\s*floor', page_text, re.IGNORECASE)
            if floor_match:
                property_data['floor'] = (floor_match.group(1) or floor_match.group(2)) + 'ος'
            
            # Data quality assessment
            key_fields = ['price', 'sqm', 'energy_class', 'address', 'property_type']
            filled_fields = sum(1 for field in key_fields if property_data.get(field))
            property_data['data_completeness'] = filled_fields / len(key_fields)
            
            # Only return if we have meaningful data
            if property_data.get('price') or property_data.get('sqm'):
                return property_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Single property extraction failed: {e}")
            return None
    
    async def export_results(self):
        """Export extracted property data to files"""
        try:
            logger.info("💾 Exporting breakthrough results...")
            
            # Filter for properties with actual data
            valid_properties = [
                prop for prop in self.extracted_properties 
                if isinstance(prop, dict) and (prop.get('price') or prop.get('sqm'))
            ]
            
            if not valid_properties:
                logger.warning("⚠️ No valid property data extracted")
                return
            
            # Export to JSON
            json_file = f'outputs/xe_gr_breakthrough_{self.session_id}.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'extraction_metadata': {
                        'session_id': self.session_id,
                        'extraction_timestamp': datetime.now().isoformat(),
                        'total_properties': len(valid_properties),
                        'method': 'breakthrough_scraping'
                    },
                    'properties': valid_properties
                }, f, indent=2, ensure_ascii=False)
            
            # Export to CSV
            csv_file = f'outputs/xe_gr_breakthrough_{self.session_id}.csv'
            if valid_properties:
                fieldnames = [
                    'url', 'title', 'price', 'sqm', 'energy_class', 'address',
                    'property_type', 'listing_type', 'rooms', 'floor',
                    'discovery_method', 'data_completeness', 'extraction_timestamp'
                ]
                
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for prop in valid_properties:
                        writer.writerow({key: prop.get(key, '') for key in fieldnames})
            
            # Generate summary report
            logger.info("\n" + "="*80)
            logger.info("🚀 XE.GR BREAKTHROUGH MISSION - FINAL REPORT")
            logger.info("="*80)
            logger.info(f"✅ REAL Properties Extracted: {len(valid_properties)}")
            
            # Data quality analysis
            with_price = sum(1 for p in valid_properties if p.get('price'))
            with_sqm = sum(1 for p in valid_properties if p.get('sqm'))
            with_energy = sum(1 for p in valid_properties if p.get('energy_class'))
            
            logger.info(f"💰 Properties with Price: {with_price}")
            logger.info(f"📐 Properties with SQM: {with_sqm}")
            logger.info(f"⚡ Properties with Energy Class: {with_energy}")
            
            logger.info(f"\n💾 Results saved:")
            logger.info(f"   📄 JSON: {json_file}")
            logger.info(f"   📊 CSV: {csv_file}")
            
            # Show sample results
            if valid_properties:
                logger.info(f"\n🏠 SAMPLE PROPERTIES:")
                for i, prop in enumerate(valid_properties[:3], 1):
                    title = prop.get('title', 'No title')[:50]
                    price = prop.get('price', 'N/A')
                    sqm = prop.get('sqm', 'N/A')
                    energy = prop.get('energy_class', 'N/A')
                    logger.info(f"   {i}. {title}... | €{price} | {sqm}m² | Energy {energy}")
            
            logger.info("="*80)
            
        except Exception as e:
            logger.error(f"❌ Results export failed: {e}")

async def main():
    """Run the breakthrough scraping mission"""
    scraper = XEBreakthroughScraper()
    await scraper.run_breakthrough_mission()

if __name__ == "__main__":
    asyncio.run(main())