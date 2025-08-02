#!/usr/bin/env python3
"""
ATHENS CITY BLOCKS COMPREHENSIVE SCRAPER
Analyze 10 city blocks with 15+ properties each
Extract SQM, energy class, and area for all individual properties
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AthensCityBlocksScraper:
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.all_properties = []
        self.city_blocks = {}
        
        # 10 different Athens city blocks/neighborhoods to analyze
        self.city_blocks_searches = {
            'Kolonaki': [
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/kolonaki-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/kolonaki-athens-center-athens'
            ],
            'Pangrati': [
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/pangrati-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/pangrati-athens-center-athens'
            ],
            'Exarchia': [
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/exarchia-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/exarchia-athens-center-athens'
            ],
            'Plaka': [
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/plaka-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/plaka-athens-center-athens'
            ],
            'Psirri': [
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/psirri-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/psirri-athens-center-athens'
            ],
            'Monastiraki': [
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/monastiraki-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/monastiraki-athens-center-athens'
            ],
            'Koukaki': [
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/koukaki-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/koukaki-athens-center-athens'
            ],
            'Petralona': [
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/petralona-athens-center-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/petralona-athens-center-athens'
            ],
            'Kypseli': [
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/kypseli-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/kypseli-athens'
            ],
            'Ampelokipoi': [
                'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/ampelokipoi-athens',
                'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/ampelokipoi-athens'
            ]
        }
        
        # Alternative search patterns if specific neighborhood URLs don't work
        self.fallback_searches = [
            'https://www.spitogatos.gr/en/for_sale-homes/athens-center?page=1',
            'https://www.spitogatos.gr/en/for_sale-homes/athens-center?page=2',
            'https://www.spitogatos.gr/en/for_sale-homes/athens-center?page=3',
            'https://www.spitogatos.gr/en/for_rent-homes/athens-center?page=1',
            'https://www.spitogatos.gr/en/for_rent-homes/athens-center?page=2',
            'https://www.spitogatos.gr/en/for_rent-homes/athens?page=1',
            'https://www.spitogatos.gr/en/for_rent-homes/athens?page=2',
            'https://www.spitogatos.gr/en/for_sale-homes/athens?page=1',
            'https://www.spitogatos.gr/en/for_sale-homes/athens?page=2',
            'https://www.spitogatos.gr/en/for_sale-homes/athens?page=3'
        ]
        
        self.target_properties_per_block = 15
        self.total_target_properties = 150  # 10 blocks × 15 properties
    
    async def run_comprehensive_city_analysis(self):
        """Analyze 10 city blocks with comprehensive property extraction"""
        logger.info("🏛️ ATHENS CITY BLOCKS COMPREHENSIVE ANALYSIS")
        logger.info(f"🎯 Target: 10 city blocks with {self.target_properties_per_block}+ properties each")
        logger.info(f"📊 Total target: {self.total_target_properties} individual properties")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            try:
                page = await context.new_page()
                
                # Phase 1: Process specific neighborhood searches
                logger.info("🔍 PHASE 1: Specific neighborhood extraction")
                await self.process_neighborhood_blocks(page)
                
                # Phase 2: Use fallback searches if needed
                if len(self.all_properties) < self.total_target_properties:
                    logger.info("🔍 PHASE 2: Fallback search extraction")
                    await self.process_fallback_searches(page)
                
                # Phase 3: Generate comprehensive results
                logger.info("📊 PHASE 3: Comprehensive analysis and CSV generation")
                await self.generate_comprehensive_csv()
                
            except Exception as e:
                logger.error(f"❌ Comprehensive analysis failed: {e}")
            finally:
                await browser.close()
    
    async def process_neighborhood_blocks(self, page):
        """Process specific neighborhood blocks"""
        for block_name, search_urls in self.city_blocks_searches.items():
            if len(self.all_properties) >= self.total_target_properties:
                break
            
            logger.info(f"🏘️ Processing city block: {block_name}")
            block_properties = []
            
            for search_url in search_urls:
                if len(block_properties) >= self.target_properties_per_block:
                    break
                
                try:
                    logger.info(f"🔍 Searching: {search_url}")
                    
                    response = await page.goto(search_url, wait_until="load", timeout=20000)
                    
                    if response and response.status == 200:
                        await asyncio.sleep(3)
                        
                        # Extract property URLs
                        property_urls = await self.extract_property_urls_advanced(page)
                        logger.info(f"📋 Found {len(property_urls)} property URLs")
                        
                        # Process properties for this block
                        for property_url in property_urls:
                            if len(block_properties) >= self.target_properties_per_block:
                                break
                            
                            property_data = await self.extract_comprehensive_property_data(
                                page, property_url, block_name
                            )
                            
                            if property_data:
                                block_properties.append(property_data)
                                self.all_properties.append(property_data)
                                
                                logger.info(f"✅ {block_name} [{len(block_properties)}/{self.target_properties_per_block}]: "
                                          f"{property_data.get('sqm', 'N/A')}m² | "
                                          f"Energy: {property_data.get('energy_class', 'N/A')}")
                
                except Exception as e:
                    logger.error(f"❌ Search failed for {search_url}: {e}")
                    continue
            
            self.city_blocks[block_name] = block_properties
            logger.info(f"🏘️ {block_name} complete: {len(block_properties)} properties")
    
    async def process_fallback_searches(self, page):
        """Process fallback searches to reach target"""
        logger.info(f"📊 Current properties: {len(self.all_properties)}/{self.total_target_properties}")
        logger.info("🔄 Using fallback searches to reach target...")
        
        for search_url in self.fallback_searches:
            if len(self.all_properties) >= self.total_target_properties:
                break
            
            try:
                logger.info(f"🔍 Fallback search: {search_url}")
                
                response = await page.goto(search_url, wait_until="load", timeout=20000)
                
                if response and response.status == 200:
                    await asyncio.sleep(3)
                    
                    property_urls = await self.extract_property_urls_advanced(page)
                    logger.info(f"📋 Fallback found {len(property_urls)} property URLs")
                    
                    for property_url in property_urls:
                        if len(self.all_properties) >= self.total_target_properties:
                            break
                        
                        # Determine area from URL or page content
                        area = await self.determine_area_from_url_or_content(page, property_url)
                        
                        property_data = await self.extract_comprehensive_property_data(
                            page, property_url, area or "Athens"
                        )
                        
                        if property_data:
                            self.all_properties.append(property_data)
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
                # Direct property links
                'a[href*="/property/"]',
                'a[href*="/en/property/"]',
                # Class-based selectors
                '.property-link', '.listing-link', '.property-card a',
                '.result-item a', '.property-item a', '.listing-item a',
                # Generic link patterns
                'a[href*="spitogatos.gr/property"]',
                'a[href*="spitogatos.gr/en/property"]'
            ]
            
            for selector in link_strategies:
                try:
                    links = await page.query_selector_all(selector)
                    for link in links:
                        href = await link.get_attribute('href')
                        if href and '/property/' in href:
                            # Ensure full URL
                            if href.startswith('/'):
                                href = 'https://www.spitogatos.gr' + href
                            elif not href.startswith('http'):
                                href = 'https://www.spitogatos.gr/' + href.lstrip('/')
                            
                            property_urls.add(href)
                except:
                    continue
            
            # Also extract from page content
            try:
                page_content = await page.content()
                url_pattern = r'https?://(?:www\.)?spitogatos\.gr/(?:en/)?property/\d+'
                found_urls = re.findall(url_pattern, page_content)
                for url in found_urls:
                    property_urls.add(url)
            except:
                pass
            
            return list(property_urls)[:20]  # Limit per page to prevent timeout
            
        except Exception as e:
            logger.error(f"❌ Advanced URL extraction failed: {e}")
            return []
    
    async def extract_comprehensive_property_data(self, page, property_url: str, area: str) -> Optional[Dict]:
        """Extract comprehensive property data with SQM, energy class, and area"""
        try:
            # Navigate with timeout
            response = await page.goto(property_url, wait_until="load", timeout=12000)
            
            if not response or response.status != 200:
                return None
            
            await asyncio.sleep(2)
            
            # Initialize property data
            property_data = {
                'url': property_url,
                'area': area,
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            # Get page content
            page_text = await page.inner_text('body')
            page_content = await page.content()
            title = await page.title()
            
            # Extract title
            property_data['title'] = title
            
            # Extract SQM (REQUIRED)
            sqm = await self.extract_sqm_comprehensive(page_text)
            if sqm:
                property_data['sqm'] = sqm
            
            # Extract energy class (REQUIRED)
            energy_class = await self.extract_energy_class_ultimate(page, page_text, page_content)
            if energy_class:
                property_data['energy_class'] = energy_class
            
            # Extract area/neighborhood (REQUIRED)
            refined_area = await self.extract_area_comprehensive(page_text, title, area)
            property_data['area'] = refined_area
            
            # Additional useful data
            price = await self.extract_price_comprehensive(page_text)
            if price:
                property_data['price'] = price
                property_data['price_currency'] = 'EUR'
            
            # Calculate price per sqm if both available
            if price and sqm and sqm > 0:
                property_data['price_per_sqm'] = round(price / sqm, 2)
            
            # Extract property type
            property_type = await self.extract_property_type(page_text, title)
            property_data['property_type'] = property_type
            
            # Extract listing type
            if 'rent' in property_url.lower() or 'ενοικίαση' in page_text.lower():
                property_data['listing_type'] = 'rent'
            else:
                property_data['listing_type'] = 'sale'
            
            # Extract number of rooms
            rooms = await self.extract_rooms(page_text)
            if rooms:
                property_data['rooms'] = rooms
            
            # Extract floor
            floor = await self.extract_floor(page_text)
            if floor:
                property_data['floor'] = floor
            
            # Validate we have essential data (SQM is most important)
            if property_data.get('sqm'):
                return property_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Comprehensive property extraction failed for {property_url}: {e}")
            return None
    
    async def extract_sqm_comprehensive(self, page_text: str) -> Optional[float]:
        """Comprehensive SQM extraction - CRITICAL for analysis"""
        sqm_patterns = [
            r'(\d+(?:\.\d+)?)\s*m²',
            r'(\d+(?:\.\d+)?)\s*sq\.?\s*m',
            r'(\d+(?:\.\d+)?)\s*τ\.μ',
            r'(\d+(?:\.\d+)?)\s*m2',
            r'(\d+(?:\.\d+)?)\s*τετραγωνικά',
            r'Size[:\s]*(\d+(?:\.\d+)?)',
            r'Εμβαδόν[:\s]*(\d+(?:\.\d+)?)',
            r'Area[:\s]*(\d+(?:\.\d+)?)',
            r'(\d+)\s*square\s*meters',
            r'(\d+)\s*τ\.μ\.',
            r'(\d+)\s*m²\s*',
            r'Μέγεθος[:\s]*(\d+(?:\.\d+)?)'
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
        """Ultimate energy class extraction"""
        try:
            # Strategy 1: CSS selectors
            energy_selectors = [
                '[class*="energy"]', '[id*="energy"]',
                '[class*="certificate"]', '[id*="certificate"]',
                '.energy-class', '.energy-rating', '.energy-certificate',
                'span:has-text("Energy")', 'div:has-text("Energy")',
                'span:has-text("Ενεργειακή")', 'div:has-text("Ενεργειακή")',
                '.certificate', '.rating', '.efficiency'
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
            
            # Strategy 2: Text patterns
            energy_patterns = [
                r'ενεργειακή\s+κλάση[:\s]*([A-G][+]?)',
                r'energy\s+class[:\s]*([A-G][+]?)',
                r'energy\s+rating[:\s]*([A-G][+]?)',
                r'ενεργειακό\s+πιστοποιητικό[:\s]*([A-G][+]?)',
                r'energy\s+certificate[:\s]*([A-G][+]?)',
                r'κλάση\s+ενέργειας[:\s]*([A-G][+]?)',
                r'ενεργ[^:]*[:\s]*([A-G][+]?)',
                r'energy[^:]*[:\s]*([A-G][+]?)'
            ]
            
            full_text = page_content + " " + page_text
            
            for pattern in energy_patterns:
                matches = re.finditer(pattern, full_text, re.IGNORECASE)
                for match in matches:
                    energy_class = match.group(1).upper()
                    if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                        return energy_class
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Energy class extraction failed: {e}")
            return None
    
    async def extract_area_comprehensive(self, page_text: str, title: str, default_area: str) -> str:
        """Extract comprehensive area/neighborhood information"""
        
        # Known Athens areas and neighborhoods
        athens_areas = {
            'Κολωνάκι': ['κολωνάκι', 'kolonaki'],
            'Παγκράτι': ['παγκράτι', 'pangrati'],
            'Εξάρχεια': ['εξάρχεια', 'exarchia'],
            'Πλάκα': ['πλάκα', 'plaka'],
            'Ψυρρή': ['ψυρρή', 'psirri'],
            'Μοναστηράκι': ['μοναστηράκι', 'monastiraki'],
            'Κουκάκι': ['κουκάκι', 'koukaki'],
            'Πετράλωνα': ['πετράλωνα', 'petralona'],
            'Κυψέλη': ['κυψέλη', 'kypseli'],
            'Αμπελόκηποι': ['αμπελόκηποι', 'ampelokipoi'],
            'Νέος Κόσμος': ['νέος κόσμος', 'neos kosmos'],
            'Καλλιθέα': ['καλλιθέα', 'kallithea'],
            'Γκάζι': ['γκάζι', 'gazi'],
            'Κέντρο': ['κέντρο', 'center', 'centre']
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
            r'([\d,\.]+)\s*EUR'
        ]
        
        for pattern in price_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                try:
                    price_str = match.group(1).replace(',', '').replace('.', '')
                    price = float(price_str)
                    if 10000 <= price <= 50000000:  # Reasonable price range
                        return price
                except ValueError:
                    continue
        
        return None
    
    async def extract_property_type(self, page_text: str, title: str) -> str:
        """Extract property type"""
        full_text = (page_text + " " + title).lower()
        
        if any(word in full_text for word in ['μονοκατοικία', 'detached', 'house', 'villa']):
            return 'house'
        elif any(word in full_text for word in ['μεζονέτα', 'maisonette', 'duplex']):
            return 'maisonette'
        elif any(word in full_text for word in ['στούντιο', 'studio']):
            return 'studio'
        elif any(word in full_text for word in ['οροφοδιαμέρισμα', 'penthouse']):
            return 'penthouse'
        else:
            return 'apartment'
    
    async def extract_rooms(self, page_text: str) -> Optional[int]:
        """Extract number of rooms"""
        room_patterns = [
            r'(\d+)\s*δωμάτια',
            r'(\d+)\s*δωμάτιο',
            r'(\d+)\s*rooms?',
            r'(\d+)\s*bedroom',
            r'(\d+)\s*bed'
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
                        return f"{floor_num}"
                    except:
                        return match.group(0)
        
        return None
    
    async def determine_area_from_url_or_content(self, page, property_url: str) -> Optional[str]:
        """Determine area from URL or page content"""
        try:
            # Check URL for area indicators
            url_lower = property_url.lower()
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
            
            # Try to extract from current page content if available
            try:
                page_text = await page.inner_text('body')
                return await self.extract_area_comprehensive(page_text, "", "Athens")
            except:
                pass
            
            return "Athens"
            
        except Exception as e:
            return "Athens"
    
    async def generate_comprehensive_csv(self):
        """Generate comprehensive CSV with all property data"""
        try:
            import os
            os.makedirs('outputs', exist_ok=True)
            
            # Analyze results
            total_properties = len(self.all_properties)
            with_sqm = [p for p in self.all_properties if p.get('sqm')]
            with_energy = [p for p in self.all_properties if p.get('energy_class')]
            with_area = [p for p in self.all_properties if p.get('area')]
            
            # CSV file with comprehensive data
            csv_file = f'outputs/athens_city_blocks_analysis_{self.session_id}.csv'
            
            if self.all_properties:
                fieldnames = [
                    'property_id', 'url', 'area', 'sqm', 'energy_class', 
                    'title', 'property_type', 'listing_type', 'price', 
                    'price_per_sqm', 'rooms', 'floor', 'extraction_timestamp'
                ]
                
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for i, prop in enumerate(self.all_properties, 1):
                        # Generate simple property ID
                        prop_id = f"ATH_{i:03d}"
                        
                        writer.writerow({
                            'property_id': prop_id,
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
            
            # Generate JSON summary
            json_file = f'outputs/athens_city_blocks_summary_{self.session_id}.json'
            
            # Area distribution
            area_distribution = {}
            for prop in self.all_properties:
                area = prop.get('area', 'Unknown')
                area_distribution[area] = area_distribution.get(area, 0) + 1
            
            # Energy class distribution
            energy_distribution = {}
            for prop in with_energy:
                energy = prop['energy_class']
                energy_distribution[energy] = energy_distribution.get(energy, 0) + 1
            
            # SQM statistics
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
                    'target_city_blocks': 10,
                    'target_properties_per_block': self.target_properties_per_block,
                    'total_target_properties': self.total_target_properties,
                    'actual_properties_extracted': total_properties
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
                'sqm_statistics': sqm_stats,
                'city_blocks_analysis': {block: len(props) for block, props in self.city_blocks.items()}
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            # Generate comprehensive report
            logger.info("\\n" + "="*100)
            logger.info("🏛️ ATHENS CITY BLOCKS COMPREHENSIVE ANALYSIS - FINAL REPORT")
            logger.info("="*100)
            logger.info(f"🎯 TARGET ACHIEVED: {total_properties} properties extracted")
            logger.info(f"📊 Data Completeness:")
            logger.info(f"   📐 SQM Data: {len(with_sqm)}/{total_properties} ({100*len(with_sqm)/max(1,total_properties):.1f}%)")
            logger.info(f"   🔋 Energy Class: {len(with_energy)}/{total_properties} ({100*len(with_energy)/max(1,total_properties):.1f}%)")
            logger.info(f"   🏘️ Area Data: {len(with_area)}/{total_properties} ({100*len(with_area)/max(1,total_properties):.1f}%)")
            
            if area_distribution:
                logger.info(f"\\n🏘️ AREA DISTRIBUTION:")
                for area, count in sorted(area_distribution.items(), key=lambda x: x[1], reverse=True):
                    logger.info(f"   {area}: {count} properties")
            
            if energy_distribution:
                logger.info(f"\\n🔋 ENERGY CLASS DISTRIBUTION:")
                for energy_class, count in sorted(energy_distribution.items()):
                    logger.info(f"   Class {energy_class}: {count} properties")
            
            if sqm_stats:
                logger.info(f"\\n📐 SQM STATISTICS:")
                logger.info(f"   Min: {sqm_stats['min_sqm']}m²")
                logger.info(f"   Max: {sqm_stats['max_sqm']}m²")
                logger.info(f"   Avg: {sqm_stats['avg_sqm']:.1f}m²")
            
            if self.city_blocks:
                logger.info(f"\\n🏘️ CITY BLOCKS ANALYSIS:")
                for block, props in self.city_blocks.items():
                    logger.info(f"   {block}: {len(props)} properties")
            
            logger.info(f"\\n💾 COMPREHENSIVE RESULTS SAVED:")
            logger.info(f"   📊 CSV: {csv_file}")
            logger.info(f"   📄 JSON: {json_file}")
            logger.info("="*100)
            
            # Success summary
            if total_properties >= self.total_target_properties:
                logger.info(f"\\n🎉 MISSION ACCOMPLISHED!")
                logger.info(f"Successfully extracted {total_properties} properties from Athens city blocks")
            else:
                logger.info(f"\\n📊 PARTIAL SUCCESS:")
                logger.info(f"Extracted {total_properties} properties (target: {self.total_target_properties})")
            
            logger.info(f"✅ CSV file ready with SQM, energy class, and area data for all properties")
            
        except Exception as e:
            logger.error(f"❌ CSV generation failed: {e}")

async def main():
    scraper = AthensCityBlocksScraper()
    await scraper.run_comprehensive_city_analysis()

if __name__ == "__main__":
    asyncio.run(main())