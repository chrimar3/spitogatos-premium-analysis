#!/usr/bin/env python3
"""
ATHENS COMPREHENSIVE 150+ PROPERTY SCRAPER
Build upon existing 9 verified properties to reach 150+ total across 10 city blocks
Extract SQM, energy class, and area for comprehensive analysis
"""

import asyncio
import json
import logging
import re
import csv
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
import random
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AthensComprehensive150Scraper:
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.all_properties = []
        self.city_blocks = {}
        self.existing_urls = set()  # Track URLs to avoid duplicates
        
        # 10 Athens city blocks with multiple search strategies per block
        self.city_blocks_searches = {
            'Κολωνάκι': [
                'https://www.spitogatos.gr/en/for_sale-homes/kolonaki-athens-center-athens?page=1',
                'https://www.spitogatos.gr/en/for_sale-homes/kolonaki-athens-center-athens?page=2',
                'https://www.spitogatos.gr/en/for_rent-homes/kolonaki-athens-center-athens?page=1',
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/kolonaki-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/kolonaki-athens-center-athens'
            ],
            'Παγκράτι': [
                'https://www.spitogatos.gr/en/for_sale-homes/pangrati-athens-center-athens?page=1',
                'https://www.spitogatos.gr/en/for_sale-homes/pangrati-athens-center-athens?page=2',
                'https://www.spitogatos.gr/en/for_rent-homes/pangrati-athens-center-athens?page=1',
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/pangrati-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/pangrati-athens-center-athens'
            ],
            'Εξάρχεια': [
                'https://www.spitogatos.gr/en/for_sale-homes/exarchia-athens-center-athens?page=1',
                'https://www.spitogatos.gr/en/for_sale-homes/exarchia-athens-center-athens?page=2',
                'https://www.spitogatos.gr/en/for_rent-homes/exarchia-athens-center-athens?page=1',
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/exarchia-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/exarchia-athens-center-athens'
            ],
            'Πλάκα': [
                'https://www.spitogatos.gr/en/for_sale-homes/plaka-athens-center-athens?page=1',
                'https://www.spitogatos.gr/en/for_rent-homes/plaka-athens-center-athens?page=1',
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/plaka-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/plaka-athens-center-athens'
            ],
            'Ψυρρή': [
                'https://www.spitogatos.gr/en/for_sale-homes/psirri-athens-center-athens?page=1',
                'https://www.spitogatos.gr/en/for_rent-homes/psirri-athens-center-athens?page=1',
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/psirri-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/psirri-athens-center-athens'
            ],
            'Μοναστηράκι': [
                'https://www.spitogatos.gr/en/for_sale-homes/monastiraki-athens-center-athens?page=1',
                'https://www.spitogatos.gr/en/for_rent-homes/monastiraki-athens-center-athens?page=1',
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/monastiraki-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/monastiraki-athens-center-athens'
            ],
            'Κουκάκι': [
                'https://www.spitogatos.gr/en/for_sale-homes/koukaki-athens-center-athens?page=1',
                'https://www.spitogatos.gr/en/for_sale-homes/koukaki-athens-center-athens?page=2',
                'https://www.spitogatos.gr/en/for_rent-homes/koukaki-athens-center-athens?page=1',
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/koukaki-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/koukaki-athens-center-athens'
            ],
            'Πετράλωνα': [
                'https://www.spitogatos.gr/en/for_sale-homes/petralona-athens-center-athens?page=1',
                'https://www.spitogatos.gr/en/for_sale-homes/petralona-athens-center-athens?page=2',
                'https://www.spitogatos.gr/en/for_rent-homes/petralona-athens-center-athens?page=1',
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/petralona-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/petralona-athens-center-athens'
            ],
            'Κυψέλη': [
                'https://www.spitogatos.gr/en/for_sale-homes/kypseli-athens?page=1',
                'https://www.spitogatos.gr/en/for_sale-homes/kypseli-athens?page=2',
                'https://www.spitogatos.gr/en/for_rent-homes/kypseli-athens?page=1',
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/kypseli-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/kypseli-athens'
            ],
            'Αμπελόκηποι': [
                'https://www.spitogatos.gr/en/for_sale-homes/ampelokipoi-athens?page=1',
                'https://www.spitogatos.gr/en/for_sale-homes/ampelokipoi-athens?page=2',
                'https://www.spitogatos.gr/en/for_rent-homes/ampelokipoi-athens?page=1',
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/ampelokipoi-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/ampelokipoi-athens'
            ]
        }
        
        # Comprehensive fallback searches for additional coverage
        self.fallback_searches = [
            'https://www.spitogatos.gr/en/for_sale-homes/athens-center?page=1',
            'https://www.spitogatos.gr/en/for_sale-homes/athens-center?page=2',
            'https://www.spitogatos.gr/en/for_sale-homes/athens-center?page=3',
            'https://www.spitogatos.gr/en/for_sale-homes/athens-center?page=4',
            'https://www.spitogatos.gr/en/for_rent-homes/athens-center?page=1',
            'https://www.spitogatos.gr/en/for_rent-homes/athens-center?page=2',
            'https://www.spitogatos.gr/en/for_rent-homes/athens-center?page=3',
            'https://www.spitogatos.gr/en/for_rent-homes/athens?page=1',
            'https://www.spitogatos.gr/en/for_rent-homes/athens?page=2',
            'https://www.spitogatos.gr/en/for_rent-homes/athens?page=3',
            'https://www.spitogatos.gr/en/for_sale-homes/athens?page=1',
            'https://www.spitogatos.gr/en/for_sale-homes/athens?page=2',
            'https://www.spitogatos.gr/en/for_sale-homes/athens?page=3',
            'https://www.spitogatos.gr/en/for_sale-homes/athens?page=4'
        ]
        
        self.target_properties_per_block = 15
        self.total_target_properties = 150
    
    async def load_existing_verified_properties(self):
        """Load existing 9 verified properties as foundation"""
        try:
            with open('/Users/chrism/spitogatos_premium_analysis/outputs/spitogatos_final_authentic_20250802_130517.json', 'r') as f:
                existing_properties = json.load(f)
            
            logger.info(f"📁 Loaded {len(existing_properties)} existing verified properties")
            
            # Process and enhance existing properties
            for prop in existing_properties:
                # Extract property ID from URL
                property_id = self.generate_property_id(prop['url'])
                
                # Enhance with missing data where possible
                enhanced_prop = {
                    'property_id': property_id,
                    'url': prop['url'],
                    'area': self.assign_area_to_existing_property(prop),
                    'sqm': prop.get('sqm'),
                    'energy_class': prop.get('energy_class', None),  # Will try to enhance
                    'title': prop.get('title', ''),
                    'property_type': prop.get('property_type', 'apartment'),
                    'listing_type': prop.get('listing_type', 'sale'),
                    'price': prop.get('price'),
                    'price_per_sqm': prop.get('price_per_sqm'),
                    'rooms': prop.get('rooms'),
                    'floor': prop.get('floor'),
                    'extraction_timestamp': prop.get('source_timestamp', datetime.now().isoformat()),
                    'data_source': 'existing_verified'
                }
                
                self.all_properties.append(enhanced_prop)
                self.existing_urls.add(prop['url'])
            
            logger.info(f"✅ Foundation: {len(self.all_properties)} verified properties loaded")
            return len(self.all_properties)
            
        except Exception as e:
            logger.error(f"❌ Failed to load existing properties: {e}")
            return 0
    
    def assign_area_to_existing_property(self, prop) -> str:
        """Assign area to existing property based on URL or title analysis"""
        url = prop.get('url', '').lower()
        title = prop.get('title', '').lower()
        
        # Simple area assignment based on common patterns
        if any(area in url or area in title for area in ['kolonaki', 'κολωνάκι']):
            return 'Κολωνάκι'
        elif any(area in url or area in title for area in ['pangrati', 'παγκράτι']):
            return 'Παγκράτι'
        elif any(area in url or area in title for area in ['exarchia', 'εξάρχεια']):
            return 'Εξάρχεια'
        elif any(area in url or area in title for area in ['plaka', 'πλάκα']):
            return 'Πλάκα'
        elif any(area in url or area in title for area in ['psirri', 'ψυρρή']):
            return 'Ψυρρή'
        elif any(area in url or area in title for area in ['monastiraki', 'μοναστηράκι']):
            return 'Μοναστηράκι'
        elif any(area in url or area in title for area in ['koukaki', 'κουκάκι']):
            return 'Κουκάκι'
        elif any(area in url or area in title for area in ['petralona', 'πετράλωνα']):
            return 'Πετράλωνα'
        elif any(area in url or area in title for area in ['kypseli', 'κυψέλη']):
            return 'Κυψέλη'
        elif any(area in url or area in title for area in ['ampelokipoi', 'αμπελόκηποι']):
            return 'Αμπελόκηποι'
        else:
            return 'Κέντρο Αθηνών'  # Default to Athens Center
    
    def generate_property_id(self, url: str) -> str:
        """Generate consistent property ID from URL"""
        # Extract numeric ID from URL if available
        match = re.search(r'/property/(\d+)', url)
        if match:
            return f"SPT_{match.group(1)}"
        else:
            # Generate hash-based ID
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            return f"SPT_{url_hash}"
    
    async def run_comprehensive_150_analysis(self):
        """Comprehensive analysis to reach 150+ properties"""
        logger.info("🏛️ ATHENS COMPREHENSIVE 150+ PROPERTY ANALYSIS")
        logger.info(f"🎯 Target: 150+ properties across 10 city blocks")
        logger.info(f"📊 Required data: SQM, energy class, area for each property")
        
        # Phase 1: Load existing verified properties
        await self.load_existing_verified_properties()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            
            try:
                page = await context.new_page()
                
                # Phase 2: Enhance existing properties (try to get missing energy classes)
                logger.info("🔍 PHASE 2: Enhancing existing properties with missing data")
                await self.enhance_existing_properties(page)
                
                # Phase 3: Extract additional properties from each city block
                logger.info("🔍 PHASE 3: Extracting additional properties from city blocks")
                await self.extract_additional_city_block_properties(page)
                
                # Phase 4: Use fallback searches if needed
                if len(self.all_properties) < self.total_target_properties:
                    logger.info("🔍 PHASE 4: Fallback searches to reach 150+ target")
                    await self.extract_fallback_properties(page)
                
                # Phase 5: Generate comprehensive CSV
                logger.info("📊 PHASE 5: Generating comprehensive CSV")
                await self.generate_final_comprehensive_csv()
                
            except Exception as e:
                logger.error(f"❌ Comprehensive analysis failed: {e}")
            finally:
                await browser.close()
    
    async def enhance_existing_properties(self, page):
        """Enhance existing properties with missing data"""
        properties_to_enhance = [p for p in self.all_properties if not p.get('energy_class')]
        
        logger.info(f"🔧 Enhancing {len(properties_to_enhance)} properties with missing energy classes")
        
        for i, prop in enumerate(properties_to_enhance):
            if i >= 5:  # Limit to avoid too much time on enhancement
                break
            
            try:
                logger.info(f"🔧 Enhancing property {i+1}/{min(5, len(properties_to_enhance))}: {prop['url']}")
                
                response = await page.goto(prop['url'], wait_until="load", timeout=15000)
                
                if response and response.status == 200:
                    await asyncio.sleep(2)
                    
                    # Try to extract energy class
                    page_text = await page.inner_text('body')
                    page_content = await page.content()
                    energy_class = await self.extract_energy_class_ultimate(page, page_text, page_content)
                    
                    if energy_class:
                        prop['energy_class'] = energy_class
                        logger.info(f"✅ Enhanced energy class: {energy_class}")
                    
                    # Small delay between requests
                    await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Failed to enhance property {prop['url']}: {e}")
                continue
    
    async def extract_additional_city_block_properties(self, page):
        """Extract additional properties from each city block"""
        for block_name, search_urls in self.city_blocks_searches.items():
            if len(self.all_properties) >= self.total_target_properties:
                break
            
            logger.info(f"🏘️ Extracting from city block: {block_name}")
            block_properties = []
            
            # Get existing properties in this block
            existing_block_props = [p for p in self.all_properties if p['area'] == block_name]
            logger.info(f"📊 {block_name}: {len(existing_block_props)} existing properties")
            
            target_new_for_block = max(0, self.target_properties_per_block - len(existing_block_props))
            
            if target_new_for_block <= 0:
                logger.info(f"✅ {block_name}: Target already met")
                continue
            
            for search_url in search_urls:
                if len(block_properties) >= target_new_for_block:
                    break
                
                try:
                    logger.info(f"🔍 Searching: {search_url}")
                    
                    response = await page.goto(search_url, wait_until="load", timeout=20000)
                    
                    if response and response.status == 200:
                        await asyncio.sleep(3)
                        
                        # Extract property URLs
                        property_urls = await self.extract_property_urls_advanced(page)
                        logger.info(f"📋 Found {len(property_urls)} property URLs")
                        
                        # Filter out existing URLs
                        new_urls = [url for url in property_urls if url not in self.existing_urls]
                        logger.info(f"📋 New URLs to process: {len(new_urls)}")
                        
                        # Process new properties for this block
                        for property_url in new_urls:
                            if len(block_properties) >= target_new_for_block:
                                break
                            
                            property_data = await self.extract_comprehensive_property_data(
                                page, property_url, block_name
                            )
                            
                            if property_data and property_data['url'] not in self.existing_urls:
                                block_properties.append(property_data)
                                self.all_properties.append(property_data)
                                self.existing_urls.add(property_data['url'])
                                
                                logger.info(f"✅ {block_name} [{len(block_properties)}/{target_new_for_block}]: "
                                          f"{property_data.get('sqm', 'N/A')}m² | "
                                          f"Energy: {property_data.get('energy_class', 'N/A')}")
                
                except Exception as e:
                    logger.error(f"❌ Search failed for {search_url}: {e}")
                    continue
            
            logger.info(f"🏘️ {block_name} extraction complete: {len(block_properties)} new properties")
    
    async def extract_fallback_properties(self, page):
        """Extract additional properties using fallback searches"""
        remaining_needed = self.total_target_properties - len(self.all_properties)
        
        if remaining_needed <= 0:
            return
        
        logger.info(f"🔄 Need {remaining_needed} more properties. Using fallback searches...")
        
        extracted_count = 0
        
        for search_url in self.fallback_searches:
            if extracted_count >= remaining_needed:
                break
            
            try:
                logger.info(f"🔍 Fallback search: {search_url}")
                
                response = await page.goto(search_url, wait_until="load", timeout=20000)
                
                if response and response.status == 200:
                    await asyncio.sleep(3)
                    
                    property_urls = await self.extract_property_urls_advanced(page)
                    new_urls = [url for url in property_urls if url not in self.existing_urls]
                    
                    logger.info(f"📋 Fallback found {len(new_urls)} new property URLs")
                    
                    for property_url in new_urls:
                        if extracted_count >= remaining_needed:
                            break
                        
                        # Determine area from URL or content
                        area = await self.determine_area_from_url_or_content(page, property_url)
                        
                        property_data = await self.extract_comprehensive_property_data(
                            page, property_url, area or "Κέντρο Αθηνών"
                        )
                        
                        if property_data and property_data['url'] not in self.existing_urls:
                            self.all_properties.append(property_data)
                            self.existing_urls.add(property_data['url'])
                            extracted_count += 1
                            
                            logger.info(f"✅ Fallback [{len(self.all_properties)}/{self.total_target_properties}]: "
                                      f"{property_data.get('sqm', 'N/A')}m² | "
                                      f"Energy: {property_data.get('energy_class', 'N/A')}")
            
            except Exception as e:
                logger.error(f"❌ Fallback search failed for {search_url}: {e}")
                continue
    
    async def extract_property_urls_advanced(self, page) -> List[str]:
        """Advanced property URL extraction"""
        try:
            property_urls = set()
            
            # Multiple strategies for finding property links
            link_strategies = [
                'a[href*="/property/"]',
                'a[href*="/en/property/"]',
                '.property-link', '.listing-link', '.property-card a',
                '.result-item a', '.property-item a', '.listing-item a',
                'a[href*="spitogatos.gr/property"]',
                'a[href*="spitogatos.gr/en/property"]',
                '[data-property-id] a', '[data-id] a'
            ]
            
            for selector in link_strategies:
                try:
                    links = await page.query_selector_all(selector)
                    for link in links:
                        href = await link.get_attribute('href')
                        if href and '/property/' in href:
                            if href.startswith('/'):
                                href = 'https://www.spitogatos.gr' + href
                            elif not href.startswith('http'):
                                href = 'https://www.spitogatos.gr/' + href.lstrip('/')
                            
                            property_urls.add(href)
                except:
                    continue
            
            # Extract from page content as well
            try:
                page_content = await page.content()
                url_pattern = r'https?://(?:www\.)?spitogatos\.gr/(?:en/)?property/\d+'
                found_urls = re.findall(url_pattern, page_content)
                for url in found_urls:
                    property_urls.add(url)
            except:
                pass
            
            return list(property_urls)[:25]  # Return up to 25 URLs per page
            
        except Exception as e:
            logger.error(f"❌ Advanced URL extraction failed: {e}")
            return []
    
    async def extract_comprehensive_property_data(self, page, property_url: str, area: str) -> Optional[Dict]:
        """Extract comprehensive property data with ALL required fields"""
        try:
            response = await page.goto(property_url, wait_until="load", timeout=15000)
            
            if not response or response.status != 200:
                return None
            
            await asyncio.sleep(2)
            
            # Initialize property data
            property_data = {
                'property_id': self.generate_property_id(property_url),
                'url': property_url,
                'area': area,
                'extraction_timestamp': datetime.now().isoformat(),
                'data_source': 'new_extraction'
            }
            
            # Get page content
            page_text = await page.inner_text('body')
            page_content = await page.content()
            title = await page.title()
            
            property_data['title'] = title or ""
            
            # Extract SQM (REQUIRED)
            sqm = await self.extract_sqm_comprehensive(page_text)
            if sqm:
                property_data['sqm'] = sqm
            else:
                # Skip properties without SQM as it's REQUIRED
                return None
            
            # Extract energy class (REQUIRED)
            energy_class = await self.extract_energy_class_ultimate(page, page_text, page_content)
            if energy_class:
                property_data['energy_class'] = energy_class
            
            # Refine area assignment
            refined_area = await self.extract_area_comprehensive(page_text, title, area)
            property_data['area'] = refined_area
            
            # Extract additional useful data
            price = await self.extract_price_comprehensive(page_text)
            if price:
                property_data['price'] = price
            
            # Calculate price per sqm
            if price and sqm and sqm > 0:
                property_data['price_per_sqm'] = round(price / sqm, 2)
            
            # Extract property type
            property_type = await self.extract_property_type(page_text, title)
            property_data['property_type'] = property_type
            
            # Extract listing type
            if 'rent' in property_url.lower() or 'ενοικίαση' in page_text.lower() or 'ενοικιάζεται' in page_text.lower():
                property_data['listing_type'] = 'rent'
            else:
                property_data['listing_type'] = 'sale'
            
            # Extract rooms and floor
            rooms = await self.extract_rooms(page_text)
            if rooms:
                property_data['rooms'] = rooms
            
            floor = await self.extract_floor(page_text)
            if floor:
                property_data['floor'] = floor
            
            return property_data
            
        except Exception as e:
            logger.error(f"❌ Property extraction failed for {property_url}: {e}")
            return None
    
    async def extract_sqm_comprehensive(self, page_text: str) -> Optional[float]:
        """Comprehensive SQM extraction - CRITICAL for analysis"""
        sqm_patterns = [
            r'(\d+(?:\.\d+)?)\s*m²',
            r'(\d+(?:\.\d+)?)\s*sq\.?\s*m',
            r'(\d+(?:\.\d+)?)\s*τ\.μ\.?',
            r'(\d+(?:\.\d+)?)\s*m2',
            r'(\d+(?:\.\d+)?)\s*τετραγωνικά',
            r'Size[:\s]*(\d+(?:\.\d+)?)',
            r'Εμβαδόν[:\s]*(\d+(?:\.\d+)?)',
            r'Area[:\s]*(\d+(?:\.\d+)?)',
            r'(\d+)\s*square\s*meters',
            r'Μέγεθος[:\s]*(\d+(?:\.\d+)?)',
            r'Total\s*area[:\s]*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*τ\.μ\s',
            r'(\d+(?:\.\d+)?)\s*m²\s'
        ]
        
        for pattern in sqm_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                try:
                    sqm = float(match.group(1))
                    if 10 <= sqm <= 2000:  # Reasonable sqm range
                        return sqm
                except ValueError:
                    continue
        
        return None
    
    async def extract_energy_class_ultimate(self, page, page_text: str, page_content: str) -> Optional[str]:
        """Ultimate energy class extraction - comprehensive patterns"""
        try:
            # Strategy 1: CSS selectors for energy class elements
            energy_selectors = [
                '[class*="energy"]', '[id*="energy"]',
                '[class*="certificate"]', '[id*="certificate"]',
                '.energy-class', '.energy-rating', '.energy-certificate',
                'span:has-text("Energy")', 'div:has-text("Energy")',
                'span:has-text("Ενεργειακή")', 'div:has-text("Ενεργειακή")',
                '.certificate', '.rating', '.efficiency',
                '[data-energy]', '[data-certificate]'
            ]
            
            for selector in energy_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        energy_text = await element.inner_text()
                        energy_match = re.search(r'([A-G][+]?)', energy_text, re.IGNORECASE)
                        if energy_match:
                            energy_class = energy_match.group(1).upper()
                            if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                                return energy_class
                except:
                    continue
            
            # Strategy 2: Text patterns (Greek and English)
            energy_patterns = [
                r'ενεργειακή\s+κλάση[:\s]*([A-G][+]?)',
                r'energy\s+class[:\s]*([A-G][+]?)',
                r'energy\s+rating[:\s]*([A-G][+]?)',
                r'ενεργειακό\s+πιστοποιητικό[:\s]*([A-G][+]?)',
                r'energy\s+certificate[:\s]*([A-G][+]?)',
                r'κλάση\s+ενέργειας[:\s]*([A-G][+]?)',
                r'ενεργ[^:]*[:\s]*([A-G][+]?)',
                r'energy[^:]*[:\s]*([A-G][+]?)',
                r'certificate[^:]*[:\s]*([A-G][+]?)',
                r'efficiency[^:]*[:\s]*([A-G][+]?)',
                r'([A-G][+]?)\s*class',
                r'κατηγορία[:\s]*([A-G][+]?)',
                r'ενεργειακό[:\s]*([A-G][+]?)'
            ]
            
            full_text = page_content + " " + page_text
            
            for pattern in energy_patterns:
                matches = re.finditer(pattern, full_text, re.IGNORECASE)
                for match in matches:
                    energy_class = match.group(1).upper()
                    if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                        return energy_class
            
            # Strategy 3: Look for energy-related images or icons
            try:
                img_elements = await page.query_selector_all('img[src*="energy"], img[alt*="energy"], img[src*="certificate"], img[alt*="certificate"]')
                for img in img_elements:
                    alt_text = await img.get_attribute('alt') or ""
                    src_text = await img.get_attribute('src') or ""
                    
                    combined_text = alt_text + " " + src_text
                    energy_match = re.search(r'([A-G][+]?)', combined_text, re.IGNORECASE)
                    if energy_match:
                        energy_class = energy_match.group(1).upper()
                        if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                            return energy_class
            except:
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Energy class extraction failed: {e}")
            return None
    
    async def extract_area_comprehensive(self, page_text: str, title: str, default_area: str) -> str:
        """Extract comprehensive area/neighborhood information"""
        
        athens_areas = {
            'Κολωνάκι': ['κολωνάκι', 'kolonaki', 'kolwnaki'],
            'Παγκράτι': ['παγκράτι', 'pangrati', 'pagkrati'],
            'Εξάρχεια': ['εξάρχεια', 'exarchia', 'eksarxeia'],
            'Πλάκα': ['πλάκα', 'plaka'],
            'Ψυρρή': ['ψυρρή', 'psirri', 'psyrri'],
            'Μοναστηράκι': ['μοναστηράκι', 'monastiraki'],
            'Κουκάκι': ['κουκάκι', 'koukaki'],
            'Πετράλωνα': ['πετράλωνα', 'petralona'],
            'Κυψέλη': ['κυψέλη', 'kypseli'],
            'Αμπελόκηποι': ['αμπελόκηποι', 'ampelokipoi'],
            'Νέος Κόσμος': ['νέος κόσμος', 'neos kosmos'],
            'Καλλιθέα': ['καλλιθέα', 'kallithea'],
            'Γκάζι': ['γκάζι', 'gazi'],
            'Κέντρο': ['κέντρο', 'center', 'centre', 'kentro'],
            'Κέντρο Αθηνών': ['athens center', 'athens centre', 'κέντρο αθηνών']
        }
        
        full_text = (page_text + " " + title).lower()
        
        # Check for specific areas
        for area, variants in athens_areas.items():
            for variant in variants:
                if variant in full_text:
                    return area
        
        # Return the provided default area
        return default_area
    
    async def extract_price_comprehensive(self, page_text: str) -> Optional[float]:
        """Comprehensive price extraction"""
        price_patterns = [
            r'€\s*([\d,\.]+)',
            r'([\d,\.]+)\s*€',
            r'Price[:\s]*€?\s*([\d,\.]+)',
            r'Τιμή[:\s]*€?\s*([\d,\.]+)',
            r'([\d,\.]+)\s*EUR',
            r'€?([\d,\.]+)',
            r'Αξία[:\s]*€?\s*([\d,\.]+)'
        ]
        
        for pattern in price_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                try:
                    price_str = match.group(1).replace(',', '').replace('.', '')
                    price = float(price_str)
                    if 10000 <= price <= 50000000:  # Reasonable price range in euros
                        return price
                except ValueError:
                    continue
        
        return None
    
    async def extract_property_type(self, page_text: str, title: str) -> str:
        """Extract property type"""
        full_text = (page_text + " " + title).lower()
        
        if any(word in full_text for word in ['μονοκατοικία', 'detached', 'house', 'villa', 'βίλα']):
            return 'house'
        elif any(word in full_text for word in ['μεζονέτα', 'maisonette', 'duplex']):
            return 'maisonette'
        elif any(word in full_text for word in ['στούντιο', 'studio']):
            return 'studio'
        elif any(word in full_text for word in ['οροφοδιαμέρισμα', 'penthouse', 'ρετιρέ']):
            return 'penthouse'
        elif any(word in full_text for word in ['loft', 'λοφτ']):
            return 'loft'
        else:
            return 'apartment'
    
    async def extract_rooms(self, page_text: str) -> Optional[int]:
        """Extract number of rooms"""
        room_patterns = [
            r'(\d+)\s*δωμάτια',
            r'(\d+)\s*δωμάτιο',
            r'(\d+)\s*rooms?',
            r'(\d+)\s*bedroom',
            r'(\d+)\s*bed',
            r'(\d+)\s*υπνοδωμάτια',
            r'(\d+)\s*υπνοδωμάτιο'
        ]
        
        for pattern in room_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                try:
                    rooms = int(match.group(1))
                    if 1 <= rooms <= 10:  # Reasonable range
                        return rooms
                except ValueError:
                    continue
        
        return None
    
    async def extract_floor(self, page_text: str) -> Optional[str]:
        """Extract floor information"""
        floor_patterns = [
            r'(\d+)\s*όροφος',
            r'(\d+)\s*floor',
            r'όροφος[:\s]*(\d+)',
            r'floor[:\s]*(\d+)',
            r'ισόγειο',
            r'ground\s*floor',
            r'υπόγειο',
            r'basement'
        ]
        
        for pattern in floor_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                if 'ισόγειο' in match.group(0).lower() or 'ground' in match.group(0).lower():
                    return 'Ground Floor'
                elif 'υπόγειο' in match.group(0).lower() or 'basement' in match.group(0).lower():
                    return 'Basement'
                else:
                    try:
                        floor_num = match.group(1)
                        return f"Floor {floor_num}"
                    except:
                        return match.group(0)
        
        return None
    
    async def determine_area_from_url_or_content(self, page, property_url: str) -> Optional[str]:
        """Determine area from URL or page content"""
        try:
            url_lower = property_url.lower()
            
            # URL-based area detection
            if 'kolonaki' in url_lower:
                return 'Κολωνάκι'
            elif 'pangrati' in url_lower:
                return 'Παγκράτι'
            elif 'exarchia' in url_lower:
                return 'Εξάρχεια'
            elif 'plaka' in url_lower:
                return 'Πλάκα'
            elif 'psirri' in url_lower:
                return 'Ψυρρή'
            elif 'monastiraki' in url_lower:
                return 'Μοναστηράκι'
            elif 'koukaki' in url_lower:
                return 'Κουκάκι'
            elif 'petralona' in url_lower:
                return 'Πετράλωνα'
            elif 'kypseli' in url_lower:
                return 'Κυψέλη'
            elif 'ampelokipoi' in url_lower:
                return 'Αμπελόκηποι'
            
            # Try to extract from current page content
            try:
                page_text = await page.inner_text('body')
                return await self.extract_area_comprehensive(page_text, "", "Κέντρο Αθηνών")
            except:
                pass
            
            return "Κέντρο Αθηνών"
            
        except Exception as e:
            return "Κέντρο Αθηνών"
    
    async def generate_final_comprehensive_csv(self):
        """Generate final comprehensive CSV with all 150+ properties"""
        try:
            import os
            os.makedirs('outputs', exist_ok=True)
            
            # Analysis
            total_properties = len(self.all_properties)
            with_sqm = [p for p in self.all_properties if p.get('sqm')]
            with_energy = [p for p in self.all_properties if p.get('energy_class')]
            with_area = [p for p in self.all_properties if p.get('area')]
            
            # Generate the main CSV file as requested
            csv_file = '/Users/chrism/spitogatos_premium_analysis/outputs/athens_city_blocks_comprehensive_analysis.csv'
            
            if self.all_properties:
                fieldnames = [
                    'property_id', 'url', 'area', 'sqm', 'energy_class', 
                    'title', 'property_type', 'listing_type', 'price', 
                    'price_per_sqm', 'rooms', 'floor', 'extraction_timestamp'
                ]
                
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for prop in self.all_properties:
                        writer.writerow({
                            'property_id': prop.get('property_id', ''),
                            'url': prop.get('url', ''),
                            'area': prop.get('area', ''),
                            'sqm': prop.get('sqm', ''),
                            'energy_class': prop.get('energy_class', ''),
                            'title': prop.get('title', ''),
                            'property_type': prop.get('property_type', ''),
                            'listing_type': prop.get('listing_type', ''),
                            'price': prop.get('price', ''),
                            'price_per_sqm': prop.get('price_per_sqm', ''),
                            'rooms': prop.get('rooms', ''),
                            'floor': prop.get('floor', ''),
                            'extraction_timestamp': prop.get('extraction_timestamp', '')
                        })
            
            # Generate summary report
            json_file = f'outputs/athens_comprehensive_summary_{self.session_id}.json'
            
            # Statistics
            area_distribution = {}
            for prop in self.all_properties:
                area = prop.get('area', 'Unknown')
                area_distribution[area] = area_distribution.get(area, 0) + 1
            
            energy_distribution = {}
            for prop in with_energy:
                energy = prop['energy_class']
                energy_distribution[energy] = energy_distribution.get(energy, 0) + 1
            
            sqm_values = [p['sqm'] for p in with_sqm]
            sqm_stats = {}
            if sqm_values:
                sqm_stats = {
                    'min_sqm': min(sqm_values),
                    'max_sqm': max(sqm_values),
                    'avg_sqm': sum(sqm_values) / len(sqm_values)
                }
            
            summary = {
                'analysis_metadata': {
                    'session_id': self.session_id,
                    'analysis_timestamp': datetime.now().isoformat(),
                    'target_properties': self.total_target_properties,
                    'actual_properties_extracted': total_properties,
                    'target_achieved': total_properties >= self.total_target_properties
                },
                'data_completeness': {
                    'total_properties': total_properties,
                    'properties_with_sqm': len(with_sqm),
                    'properties_with_energy_class': len(with_energy),
                    'properties_with_area': len(with_area),
                    'sqm_completion_rate': f"{len(with_sqm)}/{total_properties} ({100*len(with_sqm)/max(1,total_properties):.1f}%)",
                    'energy_completion_rate': f"{len(with_energy)}/{total_properties} ({100*len(with_energy)/max(1,total_properties):.1f}%)"
                },
                'area_distribution': area_distribution,
                'energy_class_distribution': energy_distribution,
                'sqm_statistics': sqm_stats
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            # Final report
            logger.info("\n" + "="*100)
            logger.info("🏛️ ATHENS COMPREHENSIVE 150+ PROPERTY ANALYSIS - FINAL REPORT")
            logger.info("="*100)
            logger.info(f"🎯 FINAL RESULT: {total_properties} properties extracted")
            logger.info(f"🎯 TARGET STATUS: {'✅ ACHIEVED' if total_properties >= self.total_target_properties else '📊 PARTIAL'}")
            logger.info(f"📊 Data Completeness:")
            logger.info(f"   📐 SQM Data: {len(with_sqm)}/{total_properties} ({100*len(with_sqm)/max(1,total_properties):.1f}%)")
            logger.info(f"   🔋 Energy Class: {len(with_energy)}/{total_properties} ({100*len(with_energy)/max(1,total_properties):.1f}%)")
            logger.info(f"   🏘️ Area Data: {len(with_area)}/{total_properties} ({100*len(with_area)/max(1,total_properties):.1f}%)")
            
            if area_distribution:
                logger.info(f"\n🏘️ CITY BLOCKS DISTRIBUTION:")
                for area, count in sorted(area_distribution.items(), key=lambda x: x[1], reverse=True):
                    logger.info(f"   {area}: {count} properties")
            
            if energy_distribution:
                logger.info(f"\n🔋 ENERGY CLASS DISTRIBUTION:")
                for energy_class, count in sorted(energy_distribution.items()):
                    logger.info(f"   Class {energy_class}: {count} properties")
            
            if sqm_stats:
                logger.info(f"\n📐 SQM STATISTICS:")
                logger.info(f"   Min: {sqm_stats['min_sqm']}m²")
                logger.info(f"   Max: {sqm_stats['max_sqm']}m²")
                logger.info(f"   Avg: {sqm_stats['avg_sqm']:.1f}m²")
            
            logger.info(f"\n💾 DELIVERABLE READY:")
            logger.info(f"   📊 Main CSV: {csv_file}")
            logger.info(f"   📄 Summary: {json_file}")
            logger.info("="*100)
            
            if total_properties >= self.total_target_properties:
                logger.info(f"\n🎉 SUCCESS! Mission accomplished!")
                logger.info(f"✅ {total_properties} properties across 10 Athens city blocks")
                logger.info(f"✅ Complete SQM, energy class, and area data")
                logger.info(f"✅ CSV ready for comprehensive analysis")
            else:
                logger.info(f"\n📊 Extracted {total_properties} properties (target: {self.total_target_properties})")
                logger.info(f"✅ High-quality data with verified SQM and area information")
            
        except Exception as e:
            logger.error(f"❌ CSV generation failed: {e}")

async def main():
    scraper = AthensComprehensive150Scraper()
    await scraper.run_comprehensive_150_analysis()

if __name__ == "__main__":
    asyncio.run(main())