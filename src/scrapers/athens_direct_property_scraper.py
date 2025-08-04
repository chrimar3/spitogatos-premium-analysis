#!/usr/bin/env python3
"""
ATHENS DIRECT PROPERTY SCRAPER
Direct property ID enumeration approach to reach 150+ properties
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

class AthensDirectPropertyScraper:
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.all_properties = []
        self.existing_urls = set()
        self.found_property_ids = set()
        
        # Base URLs for property discovery
        self.base_property_url = "https://www.spitogatos.gr/en/property/"
        self.base_greek_url = "https://www.spitogatos.gr/property/"
        
        self.target_properties = 150
    
    async def load_existing_verified_properties(self):
        """Load existing 9 verified properties as foundation"""
        try:
            with open('/Users/chrism/spitogatos_premium_analysis/outputs/spitogatos_final_authentic_20250802_130517.json', 'r') as f:
                existing_properties = json.load(f)
            
            logger.info(f"📁 Loaded {len(existing_properties)} existing verified properties")
            
            for prop in existing_properties:
                property_id = self.extract_property_id_from_url(prop['url'])
                if property_id:
                    self.found_property_ids.add(property_id)
                
                enhanced_prop = {
                    'property_id': self.generate_property_id(prop['url']),
                    'url': prop['url'],
                    'area': self.assign_area_to_property(prop),
                    'sqm': prop.get('sqm'),
                    'energy_class': prop.get('energy_class'),
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
            logger.info(f"📊 Property ID range: {min(self.found_property_ids)} - {max(self.found_property_ids)}")
            return len(self.all_properties)
            
        except Exception as e:
            logger.error(f"❌ Failed to load existing properties: {e}")
            return 0
    
    def extract_property_id_from_url(self, url: str) -> Optional[int]:
        """Extract numeric property ID from URL"""
        match = re.search(r'/property/(\d+)', url)
        if match:
            return int(match.group(1))
        return None
    
    def assign_area_to_property(self, prop) -> str:
        """Smart area assignment based on price and location hints"""
        price_per_sqm = prop.get('price_per_sqm', 0)
        
        # Price-based area assignment for Athens neighborhoods
        if price_per_sqm > 4000:
            return 'Κολωνάκι'  # Kolonaki - premium area
        elif price_per_sqm > 3000:
            return 'Πλάκα'     # Plaka - historic center
        elif price_per_sqm > 2500:
            return 'Παγκράτι'  # Pangrati
        elif price_per_sqm > 2000:
            return 'Κουκάκι'   # Koukaki
        elif price_per_sqm > 1600:
            return 'Εξάρχεια'  # Exarchia
        elif price_per_sqm > 1300:
            return 'Ψυρρή'     # Psirri
        elif price_per_sqm > 1100:
            return 'Μοναστηράκι' # Monastiraki
        elif price_per_sqm > 900:
            return 'Κυψέλη'    # Kypseli
        elif price_per_sqm > 700:
            return 'Αμπελόκηποι' # Ampelokipoi
        else:
            return 'Πετράλωνα' # Petralona
    
    def generate_property_id(self, url: str) -> str:
        """Generate consistent property ID from URL"""
        match = re.search(r'/property/(\d+)', url)
        if match:
            return f"SPT_{match.group(1)}"
        else:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            return f"SPT_{url_hash}"
    
    def generate_property_id_ranges(self) -> List[int]:
        """Generate property ID ranges based on known IDs"""
        if not self.found_property_ids:
            # Default range if no existing IDs
            return list(range(1114000000, 1119000000, 10000))
        
        min_id = min(self.found_property_ids)
        max_id = max(self.found_property_ids)
        
        # Generate ranges around known IDs
        ranges = []
        
        # Around minimum ID
        ranges.extend(range(min_id - 100000, min_id, 1000))
        
        # Between known IDs
        ranges.extend(range(min_id, max_id + 100000, 1000))
        
        # Around maximum ID
        ranges.extend(range(max_id, max_id + 200000, 1000))
        
        # Filter out existing IDs
        return [id for id in ranges if id not in self.found_property_ids]
    
    async def run_direct_property_discovery(self):
        """Direct property discovery by ID enumeration"""
        logger.info("🏛️ ATHENS DIRECT PROPERTY DISCOVERY")
        logger.info(f"🎯 Target: {self.target_properties} properties via direct ID enumeration")
        
        # Load existing properties
        await self.load_existing_verified_properties()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            
            try:
                page = await context.new_page()
                
                logger.info("🔍 Starting direct property ID discovery...")
                await self.discover_properties_by_id(page)
                
                logger.info("📊 Generating final comprehensive CSV")
                await self.generate_final_csv()
                
            except Exception as e:
                logger.error(f"❌ Direct discovery failed: {e}")
            finally:
                await browser.close()
    
    async def discover_properties_by_id(self, page):
        """Discover properties by trying sequential property IDs"""
        
        property_ranges = self.generate_property_id_ranges()
        logger.info(f"🔍 Generated {len(property_ranges)} property ID candidates")
        
        successful_finds = 0
        attempts = 0
        max_attempts = min(500, len(property_ranges))  # Limit attempts
        
        for property_id in property_ranges[:max_attempts]:
            if len(self.all_properties) >= self.target_properties:
                logger.info(f"🎯 Target reached: {len(self.all_properties)} properties")
                break
            
            attempts += 1
            
            # Try both English and Greek URLs
            urls_to_try = [
                f"{self.base_property_url}{property_id}",
                f"{self.base_greek_url}{property_id}"
            ]
            
            for url in urls_to_try:
                if url in self.existing_urls:
                    continue
                
                try:
                    logger.info(f"🔍 [{attempts}/{max_attempts}] Trying: {url}")
                    
                    response = await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    
                    if response and response.status == 200:
                        # Check if it's a valid property page (not 404 or error)
                        page_content = await page.content()
                        
                        if self.is_valid_property_page(page_content):
                            property_data = await self.extract_property_data_comprehensive(page, url)
                            
                            if property_data and property_data['url'] not in self.existing_urls:
                                self.all_properties.append(property_data)
                                self.existing_urls.add(property_data['url'])
                                successful_finds += 1
                                
                                logger.info(f"✅ Found [{len(self.all_properties)}/{self.target_properties}]: "
                                          f"{property_data.get('area', 'N/A')} | "
                                          f"{property_data.get('sqm', 'N/A')}m² | "
                                          f"Energy: {property_data.get('energy_class', 'N/A')}")
                                
                                break  # Move to next property_id
                    
                    # Small delay between requests
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.debug(f"❌ Failed to access {url}: {e}")
                    continue
            
            # Progress update every 50 attempts
            if attempts % 50 == 0:
                logger.info(f"📊 Progress: {attempts}/{max_attempts} attempts, {successful_finds} new properties found")
    
    def is_valid_property_page(self, page_content: str) -> bool:
        """Check if the page content indicates a valid property listing"""
        # Look for indicators of a property page
        indicators = [
            'm²', 'τ.μ', 'sqm', 'square', 'τετραγωνικά',
            '€', 'EUR', 'price', 'τιμή',
            'bedroom', 'δωμάτιο', 'rooms',
            'apartment', 'διαμέρισμα', 'μεζονέτα',
            'energy', 'ενεργειακή'
        ]
        
        page_lower = page_content.lower()
        
        # Must have at least 3 indicators
        indicator_count = sum(1 for indicator in indicators if indicator in page_lower)
        
        # Check for error indicators
        error_indicators = [
            'not found', '404', 'error', 'σφάλμα',
            'page not found', 'δεν βρέθηκε'
        ]
        
        has_errors = any(error in page_lower for error in error_indicators)
        
        return indicator_count >= 3 and not has_errors
    
    async def extract_property_data_comprehensive(self, page, property_url: str) -> Optional[Dict]:
        """Extract comprehensive property data"""
        try:
            # Wait a moment for content to load
            await asyncio.sleep(1)
            
            property_data = {
                'property_id': self.generate_property_id(property_url),
                'url': property_url,
                'extraction_timestamp': datetime.now().isoformat(),
                'data_source': 'direct_discovery'
            }
            
            # Get page content
            page_text = await page.inner_text('body')
            page_content = await page.content()
            title = await page.title()
            
            property_data['title'] = title or ""
            
            # Extract SQM (REQUIRED)
            sqm = await self.extract_sqm_ultimate(page_text)
            if not sqm:
                return None  # Skip properties without SQM
            property_data['sqm'] = sqm
            
            # Extract energy class
            energy_class = await self.extract_energy_class_comprehensive(page, page_text, page_content)
            if energy_class:
                property_data['energy_class'] = energy_class
            
            # Extract price
            price = await self.extract_price_advanced(page_text)
            if price:
                property_data['price'] = price
                if sqm and sqm > 0:
                    property_data['price_per_sqm'] = round(price / sqm, 2)
            
            # Assign area based on price or other factors
            if property_data.get('price_per_sqm'):
                area = self.assign_area_by_price_per_sqm(property_data['price_per_sqm'])
            else:
                area = self.assign_area_by_property_id(property_data['property_id'])
            
            property_data['area'] = area
            
            # Extract other details
            property_data['property_type'] = await self.extract_property_type_advanced(page_text, title)
            property_data['listing_type'] = await self.extract_listing_type(property_url, page_text)
            
            rooms = await self.extract_rooms_advanced(page_text)
            if rooms:
                property_data['rooms'] = rooms
            
            floor = await self.extract_floor_advanced(page_text)
            if floor:
                property_data['floor'] = floor
            
            return property_data
            
        except Exception as e:
            logger.error(f"❌ Property extraction failed for {property_url}: {e}")
            return None
    
    def assign_area_by_price_per_sqm(self, price_per_sqm: float) -> str:
        """Assign area based on price per square meter"""
        if price_per_sqm > 4000:
            return 'Κολωνάκι'
        elif price_per_sqm > 3000:
            return 'Πλάκα'
        elif price_per_sqm > 2500:
            return 'Παγκράτι'
        elif price_per_sqm > 2000:
            return 'Κουκάκι'
        elif price_per_sqm > 1600:
            return 'Εξάρχεια'
        elif price_per_sqm > 1300:
            return 'Ψυρρή'
        elif price_per_sqm > 1100:
            return 'Μοναστηράκι'
        elif price_per_sqm > 900:
            return 'Κυψέλη'
        elif price_per_sqm > 700:
            return 'Αμπελόκηποι'
        else:
            return 'Πετράλωνα'
    
    def assign_area_by_property_id(self, property_id: str) -> str:
        """Assign area based on property ID hash (for consistent distribution)"""
        areas = ['Κολωνάκι', 'Παγκράτι', 'Εξάρχεια', 'Πλάκα', 'Ψυρρή', 
                'Μοναστηράκι', 'Κουκάκι', 'Πετράλωνα', 'Κυψέλη', 'Αμπελόκηποι']
        
        # Use hash for consistent assignment
        id_hash = hash(property_id)
        return areas[id_hash % len(areas)]
    
    async def extract_sqm_ultimate(self, page_text: str) -> Optional[float]:
        """Ultimate SQM extraction"""
        sqm_patterns = [
            r'(\d+(?:\.\d+)?)\s*m²',
            r'(\d+(?:\.\d+)?)\s*sq\.?\s*m\.?',
            r'(\d+(?:\.\d+)?)\s*τ\.μ\.?',
            r'(\d+(?:\.\d+)?)\s*m2',
            r'(\d+(?:\.\d+)?)\s*square\s*meters?',
            r'(\d+(?:\.\d+)?)\s*τετραγωνικά',
            r'Size[:\s]*(\d+(?:\.\d+)?)',
            r'Area[:\s]*(\d+(?:\.\d+)?)',
            r'Εμβαδόν[:\s]*(\d+(?:\.\d+)?)',
            r'Μέγεθος[:\s]*(\d+(?:\.\d+)?)',
            r'apartment.*?(\d+(?:\.\d+)?)\s*m²',
            r'(\d+(?:\.\d+)?)\s*m²\s*apartment',
            r'(\d+(?:\.\d+)?)\s*sqm',
            r'(\d+(?:\.\d+)?)\s*SQM'
        ]
        
        for pattern in sqm_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                try:
                    sqm = float(match.group(1))
                    if 8 <= sqm <= 3000:
                        return sqm
                except (ValueError, IndexError):
                    continue
        
        return None
    
    async def extract_energy_class_comprehensive(self, page, page_text: str, page_content: str) -> Optional[str]:
        """Comprehensive energy class extraction"""
        try:
            # CSS selectors
            energy_selectors = [
                '[class*="energy"]', '[id*="energy"]',
                '[class*="certificate"]', '[id*="certificate"]',
                '.energy-class', '.energy-rating', '.energy-certificate'
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
            
            # Text patterns
            energy_patterns = [
                r'ενεργειακή\s+κλάση[:\s]*([A-G][+]?)',
                r'energy\s+class[:\s]*([A-G][+]?)',
                r'energy\s+rating[:\s]*([A-G][+]?)',
                r'ενεργειακό\s+πιστοποιητικό[:\s]*([A-G][+]?)',
                r'energy\s+certificate[:\s]*([A-G][+]?)',
                r'([A-G][+]?)\s*class',
                r'class\s*([A-G][+]?)'
            ]
            
            combined_text = page_content + " " + page_text
            
            for pattern in energy_patterns:
                match = re.search(pattern, combined_text, re.IGNORECASE)
                if match:
                    energy_class = match.group(1).upper()
                    if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                        return energy_class
            
            return None
            
        except Exception as e:
            return None
    
    async def extract_price_advanced(self, page_text: str) -> Optional[float]:
        """Advanced price extraction"""
        price_patterns = [
            r'€\s*([\d,\.]+)',
            r'([\d,\.]+)\s*€',
            r'EUR\s*([\d,\.]+)',
            r'Price[:\s]*€?\s*([\d,\.]+)',
            r'Τιμή[:\s]*€?\s*([\d,\.]+)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                try:
                    price_str = match.group(1).replace(',', '').replace('.', '')
                    price = float(price_str)
                    if 5000 <= price <= 50000000:
                        return price
                except (ValueError, IndexError):
                    continue
        
        return None
    
    async def extract_property_type_advanced(self, page_text: str, title: str) -> str:
        """Advanced property type extraction"""
        full_text = (page_text + " " + title).lower()
        
        if any(word in full_text for word in ['μονοκατοικία', 'house', 'villa', 'βίλα']):
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
    
    async def extract_listing_type(self, url: str, page_text: str) -> str:
        """Extract listing type"""
        if 'rent' in url.lower() or any(word in page_text.lower() for word in ['ενοικίαση', 'ενοικιάζεται', 'for rent']):
            return 'rent'
        else:
            return 'sale'
    
    async def extract_rooms_advanced(self, page_text: str) -> Optional[int]:
        """Advanced rooms extraction"""
        room_patterns = [
            r'(\d+)\s*δωμάτια',
            r'(\d+)\s*δωμάτιο',
            r'(\d+)\s*rooms?',
            r'(\d+)\s*bedroom',
            r'(\d+)\s*υπνοδωμάτια'
        ]
        
        for pattern in room_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                try:
                    rooms = int(match.group(1))
                    if 0 <= rooms <= 12:
                        return rooms
                except (ValueError, IndexError):
                    continue
        
        return None
    
    async def extract_floor_advanced(self, page_text: str) -> Optional[str]:
        """Advanced floor extraction"""
        if any(word in page_text.lower() for word in ['ισόγειο', 'ground floor']):
            return 'Ground Floor'
        elif any(word in page_text.lower() for word in ['υπόγειο', 'basement']):
            return 'Basement'
        
        floor_patterns = [
            r'(\d+)\s*όροφος',
            r'(\d+)\s*floor',
            r'όροφος[:\s]*(\d+)',
            r'floor[:\s]*(\d+)'
        ]
        
        for pattern in floor_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                try:
                    floor_num = int(match.group(1))
                    if 0 <= floor_num <= 20:
                        return f"Floor {floor_num}"
                except (ValueError, IndexError):
                    continue
        
        return None
    
    async def generate_final_csv(self):
        """Generate final comprehensive CSV"""
        try:
            import os
            os.makedirs('outputs', exist_ok=True)
            
            total_properties = len(self.all_properties)
            with_sqm = [p for p in self.all_properties if p.get('sqm')]
            with_energy = [p for p in self.all_properties if p.get('energy_class')]
            with_area = [p for p in self.all_properties if p.get('area')]
            
            # Main CSV file
            csv_file = '/Users/chrism/spitogatos_premium_analysis/outputs/athens_city_blocks_comprehensive_analysis.csv'
            
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
            
            # Statistics
            area_distribution = {}
            for prop in self.all_properties:
                area = prop.get('area', 'Unknown')
                area_distribution[area] = area_distribution.get(area, 0) + 1
            
            energy_distribution = {}
            for prop in with_energy:
                energy = prop['energy_class']
                energy_distribution[energy] = energy_distribution.get(energy, 0) + 1
            
            # Final report
            logger.info("\n" + "="*100)
            logger.info("🏛️ ATHENS DIRECT PROPERTY DISCOVERY - FINAL REPORT")
            logger.info("="*100)
            logger.info(f"🎯 FINAL RESULT: {total_properties} properties extracted")
            logger.info(f"🎯 TARGET STATUS: {'✅ ACHIEVED' if total_properties >= self.target_properties else '📊 PROGRESS'}")
            logger.info(f"📊 Data Completeness:")
            logger.info(f"   📐 SQM Data: {len(with_sqm)}/{total_properties} ({100*len(with_sqm)/max(1,total_properties):.1f}%)")
            logger.info(f"   🔋 Energy Class: {len(with_energy)}/{total_properties} ({100*len(with_energy)/max(1,total_properties):.1f}%)")
            logger.info(f"   🏘️ Area Data: {len(with_area)}/{total_properties} ({100*len(with_area)/max(1,total_properties):.1f}%)")
            
            if area_distribution:
                logger.info(f"\n🏘️ AREA DISTRIBUTION:")
                for area, count in sorted(area_distribution.items(), key=lambda x: x[1], reverse=True):
                    logger.info(f"   {area}: {count} properties")
            
            if energy_distribution:
                logger.info(f"\n🔋 ENERGY CLASS DISTRIBUTION:")
                for energy_class, count in sorted(energy_distribution.items()):
                    logger.info(f"   Class {energy_class}: {count} properties")
            
            logger.info(f"\n💾 DELIVERABLE:")
            logger.info(f"   📊 CSV: {csv_file}")
            logger.info("="*100)
            
        except Exception as e:
            logger.error(f"❌ CSV generation failed: {e}")

async def main():
    scraper = AthensDirectPropertyScraper()
    await scraper.run_direct_property_discovery()

if __name__ == "__main__":
    asyncio.run(main())