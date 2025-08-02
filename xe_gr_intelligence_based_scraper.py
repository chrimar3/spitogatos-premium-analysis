#!/usr/bin/env python3
"""
XE.GR INTELLIGENCE-BASED SCRAPER
Using deep analysis of reconnaissance findings to target specific property patterns
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

class XEIntelligenceScraper:
    """Intelligence-based scraper using pattern analysis from reconnaissance"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.extracted_properties = []
        
        # Intelligence: Working URL patterns discovered from reconnaissance
        self.property_url_patterns = [
            # From reconnaissance: found these working patterns
            "https://www.xe.gr/property/d/enoikiaseis-katoikion/{id}/athens-{neighborhood}",
            "https://www.xe.gr/property/d/poliseis-katoikion/{id}/athens-{neighborhood}",
            "https://xe.gr/property/d/enoikiaseis-katoikion/{id}/athens-{neighborhood}",
            "https://xe.gr/property/d/poliseis-katoikion/{id}/athens-{neighborhood}",
            "https://www.xe.gr/property/d/enoikiaseis-diamerismaton/{id}/athens-{neighborhood}",
            "https://www.xe.gr/property/d/poliseis-diamerismaton/{id}/athens-{neighborhood}"
        ]
        
        # Athens neighborhoods (Greek + English)
        self.neighborhoods = {
            "Κολωνάκι": ["kolonaki", "κολωνάκι"],
            "Παγκράτι": ["pangrati", "παγκράτι"],
            "Εξάρχεια": ["exarchia", "εξάρχεια"],
            "Πλάκα": ["plaka", "πλάκα"],
            "Ψυρρή": ["psirri", "ψυρρή"],
            "Κυψέλη": ["kypseli", "κυψέλη"],
            "Αμπελόκηποι": ["ambelokipoi", "αμπελόκηποι"],
            "Γκάζι": ["gazi", "γκάζι"],
            "Νέος Κόσμος": ["neos-kosmos", "νέος-κόσμος"],
            "Πετράλωνα": ["petralona", "πετράλωνα"]
        }
        
        # Intelligence: ID ranges to test (discovered from reconnaissance)
        self.id_ranges = [
            (870000, 880000),  # Active ID range
            (860000, 870000),  # Secondary range
            (880000, 890000)   # Extended range
        ]
    
    async def run_intelligence_mission(self):
        """Execute intelligence-based property extraction"""
        logger.info("🧠 XE.GR INTELLIGENCE-BASED EXTRACTION")
        logger.info("🎯 Using reconnaissance patterns to find real properties")
        
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
                
                # Phase 1: Pattern-based URL generation and testing
                logger.info("🔮 PHASE 1: Pattern-Based URL Discovery")
                await self.discover_properties_by_patterns(page)
                
                # Phase 2: Analyze successful properties for more patterns
                logger.info("🔍 PHASE 2: Pattern Analysis and Expansion")
                await self.analyze_and_expand_patterns(page)
                
                # Phase 3: Extract detailed data
                logger.info("📊 PHASE 3: Property Data Extraction")
                await self.extract_verified_properties(page)
                
                # Phase 4: Export results
                logger.info("💾 PHASE 4: Intelligence Report Export")
                await self.export_intelligence_results()
                
            except Exception as e:
                logger.error(f"❌ Intelligence mission failed: {e}")
            finally:
                logger.info("🔍 Keeping browser open for final inspection...")
                await asyncio.sleep(30)
                await browser.close()
    
    async def discover_properties_by_patterns(self, page):
        """Discover properties using URL pattern intelligence"""
        try:
            logger.info("🔮 Testing URL patterns with intelligence data...")
            
            found_properties = 0
            target_properties = 20  # Target: find 20 real properties
            
            for neighborhood_greek, neighborhood_variants in self.neighborhoods.items():
                if found_properties >= target_properties:
                    break
                
                logger.info(f"🏘️ Testing neighborhood: {neighborhood_greek}")
                
                for neighborhood_en in neighborhood_variants:
                    if found_properties >= target_properties:
                        break
                    
                    for start_id, end_id in self.id_ranges:
                        if found_properties >= target_properties:
                            break
                        
                        logger.info(f"🔍 Testing ID range {start_id}-{end_id} for {neighborhood_en}")
                        
                        # Test sample IDs from range (every 100th ID to be efficient)
                        for property_id in range(start_id, end_id, 100):
                            if found_properties >= target_properties:
                                break
                            
                            # Try all URL patterns for this ID and neighborhood
                            for pattern in self.property_url_patterns:
                                url = pattern.format(id=property_id, neighborhood=neighborhood_en)
                                
                                if await self.test_and_validate_property_url(page, url, neighborhood_greek):
                                    found_properties += 1
                                    logger.info(f"✅ FOUND PROPERTY {found_properties}: {url}")
                                
                                await asyncio.sleep(1)  # Respectful delay
                                
                                if found_properties >= target_properties:
                                    break
            
            logger.info(f"🎯 Pattern discovery complete: {found_properties} properties found")
        
        except Exception as e:
            logger.error(f"❌ Pattern discovery failed: {e}")
    
    async def test_and_validate_property_url(self, page, url: str, neighborhood: str) -> bool:
        """Test URL and validate it contains real property data"""
        try:
            response = await page.goto(url, wait_until="load", timeout=15000)
            
            if response and response.status == 200:
                await asyncio.sleep(2)
                
                # Get page content for validation
                content = await page.content()
                page_text = await page.inner_text('body')
                
                # Enhanced validation: must contain real property indicators
                property_indicators = [
                    'τιμή', 'price', 'τ.μ', 'm²', 'ενοικίαση', 'πώληση',
                    'διαμέρισμα', 'apartment', 'ενεργειακή', 'δωμάτια'
                ]
                
                indicator_count = sum(1 for indicator in property_indicators 
                                    if indicator.lower() in content.lower())
                
                # Location validation: must mention Athens or the specific neighborhood
                location_indicators = [
                    'αθήνα', 'athens', neighborhood.lower(),
                    'attiki', 'αττική', 'ελλάδα', 'greece'
                ]
                
                has_location = any(loc.lower() in content.lower() for loc in location_indicators)
                
                # Content validation: must be substantial property page
                is_substantial = len(page_text) > 3000  # Real property pages are detailed
                
                # Price validation: must contain realistic price patterns
                price_patterns = [
                    r'€\s*\d{2,6}',  # Euro prices
                    r'\d{2,6}\s*€',  # Prices with euro
                    r'\d{1,3}(?:\.\d{3})*\s*€'  # Formatted prices
                ]
                
                has_price = any(re.search(pattern, content) for pattern in price_patterns)
                
                # Area validation: must mention square meters
                area_patterns = [
                    r'\d+\s*τ\.?μ\.?',
                    r'\d+\s*m²',
                    r'\d+\s*sqm'
                ]
                
                has_area = any(re.search(pattern, content, re.IGNORECASE) for pattern in area_patterns)
                
                # Property is valid if it meets multiple criteria
                validation_score = sum([
                    indicator_count >= 4,  # Has property terms
                    has_location,          # Has location info
                    is_substantial,        # Substantial content
                    has_price,            # Has pricing
                    has_area              # Has area info
                ])
                
                if validation_score >= 3:  # Must meet at least 3/5 criteria
                    logger.info(f"✅ VALIDATED PROPERTY: {url} (score: {validation_score}/5)")
                    
                    self.extracted_properties.append({
                        'url': url,
                        'neighborhood': neighborhood,
                        'validation_score': validation_score,
                        'indicator_count': indicator_count,
                        'has_location': has_location,
                        'has_price': has_price,
                        'has_area': has_area,
                        'content_length': len(page_text),
                        'discovery_method': 'intelligence_pattern',
                        'discovered_at': datetime.now().isoformat()
                    })
                    
                    return True
                else:
                    logger.debug(f"❌ Invalid property: {url} (score: {validation_score}/5)")
            
            return False
            
        except Exception as e:
            logger.debug(f"❌ URL test failed {url}: {e}")
            return False
    
    async def analyze_and_expand_patterns(self, page):
        """Analyze successful URLs to discover new patterns"""
        try:
            logger.info("🔍 Analyzing successful URLs for pattern expansion...")
            
            if not self.extracted_properties:
                logger.warning("⚠️ No properties found for pattern analysis")
                return
            
            # Analyze successful URL patterns
            successful_urls = [prop['url'] for prop in self.extracted_properties]
            
            # Extract ID patterns from successful URLs
            successful_ids = []
            for url in successful_urls:
                id_match = re.search(r'/(\d{6,8})/', url)
                if id_match:
                    successful_ids.append(int(id_match.group(1)))
            
            if successful_ids:
                # Find ID clusters and test nearby IDs
                logger.info(f"🎯 Found {len(successful_ids)} successful IDs, testing nearby ranges...")
                
                target_additional = 10
                found_additional = 0
                
                for base_id in successful_ids[:3]:  # Test around first 3 successful IDs
                    if found_additional >= target_additional:
                        break
                    
                    # Test IDs around successful ones (±20 range)
                    for offset in range(-20, 21, 5):
                        if found_additional >= target_additional:
                            break
                        
                        test_id = base_id + offset
                        if test_id <= 0:
                            continue
                        
                        # Test this ID with all neighborhoods and patterns
                        for neighborhood_greek, variants in list(self.neighborhoods.items())[:3]:
                            if found_additional >= target_additional:
                                break
                            
                            for variant in variants[:1]:  # Test primary variant
                                for pattern in self.property_url_patterns[:2]:  # Test main patterns
                                    test_url = pattern.format(id=test_id, neighborhood=variant)
                                    
                                    # Skip if we already tested this URL
                                    if test_url in [prop['url'] for prop in self.extracted_properties]:
                                        continue
                                    
                                    if await self.test_and_validate_property_url(page, test_url, neighborhood_greek):
                                        found_additional += 1
                                        logger.info(f"✅ PATTERN EXPANSION: Found property {found_additional}")
                                    
                                    await asyncio.sleep(1)
                
                logger.info(f"🔍 Pattern expansion found {found_additional} additional properties")
        
        except Exception as e:
            logger.error(f"❌ Pattern analysis failed: {e}")
    
    async def extract_verified_properties(self, page):
        """Extract detailed data from all verified properties"""
        try:
            logger.info(f"📊 Extracting detailed data from {len(self.extracted_properties)} verified properties...")
            
            for i, property_info in enumerate(self.extracted_properties):
                url = property_info['url']
                logger.info(f"📋 Extracting {i+1}/{len(self.extracted_properties)}: {url}")
                
                try:
                    response = await page.goto(url, wait_until="networkidle", timeout=20000)
                    
                    if response and response.status == 200:
                        await asyncio.sleep(3)
                        
                        # Extract comprehensive property data
                        property_data = await self.extract_comprehensive_data(page, url, property_info)
                        
                        if property_data:
                            # Update the property info with extracted data
                            property_info.update(property_data)
                            logger.info(f"✅ Extracted: {property_data.get('title', 'No title')[:50]}...")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract {url}: {e}")
                    continue
                
                await asyncio.sleep(2)  # Respectful delay
        
        except Exception as e:
            logger.error(f"❌ Property data extraction failed: {e}")
    
    async def extract_comprehensive_data(self, page, url: str, existing_info: Dict) -> Optional[Dict]:
        """Extract comprehensive property data"""
        try:
            page_text = await page.inner_text('body')
            title = await page.title()
            
            property_data = {
                'title': title,
                'raw_text_length': len(page_text),
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            # Enhanced price extraction
            price_patterns = [
                r'(\d{1,3}(?:\.\d{3})*)\s*€',
                r'€\s*(\d{1,3}(?:\.\d{3})*)',
                r'τιμή[:\s]*(\d{1,3}(?:\.\d{3})*)',
                r'Τιμή[:\s]*(\d{1,3}(?:\.\d{3})*)',
                r'ΤΙΜΗ[:\s]*(\d{1,3}(?:\.\d{3})*)'
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    try:
                        price_str = match.group(1).replace('.', '')
                        price = float(price_str)
                        if 50 <= price <= 10000000:  # Realistic price range
                            property_data['price'] = price
                            break
                    except ValueError:
                        continue
            
            # Enhanced SQM extraction
            sqm_patterns = [
                r'(\d+(?:[.,]\d+)?)\s*τ\.?μ\.?',
                r'(\d+(?:[.,]\d+)?)\s*m²',
                r'(\d+(?:[.,]\d+)?)\s*sq\.?m',
                r'εμβαδόν[:\s]*(\d+(?:[.,]\d+)?)',
                r'Εμβαδόν[:\s]*(\d+(?:[.,]\d+)?)'
            ]
            
            for pattern in sqm_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    try:
                        sqm = float(match.group(1).replace(',', '.'))
                        if 10 <= sqm <= 1000:  # Realistic area range
                            property_data['sqm'] = sqm
                            break
                    except ValueError:
                        continue
            
            # Enhanced energy class extraction
            energy_patterns = [
                r'ενεργειακή\s+κλάση[:\s]*([A-G][+\-]?)',
                r'Ενεργειακή\s+κλάση[:\s]*([A-G][+\-]?)',
                r'ΕΝΕΡΓΕΙΑΚΗ\s+ΚΛΑΣΗ[:\s]*([A-G][+\-]?)',
                r'energy\s+class[:\s]*([A-G][+\-]?)',
                r'Energy\s+Class[:\s]*([A-G][+\-]?)'
            ]
            
            for pattern in energy_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    energy_class = match.group(1).upper()
                    if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                        property_data['energy_class'] = energy_class
                        break
            
            # Address extraction
            address_patterns = [
                r'διεύθυνση[:\s]*([^,\n\.]{10,100})',
                r'Διεύθυνση[:\s]*([^,\n\.]{10,100})',
                r'περιοχή[:\s]*([^,\n\.]{10,100})',
                r'Περιοχή[:\s]*([^,\n\.]{10,100})',
                r'Αθήνα[,\s]*([^,\n\.]{5,80})'
            ]
            
            for pattern in address_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    address = match.group(1).strip()
                    if len(address) > 5 and 'αθήνα' in address.lower() or existing_info['neighborhood'].lower() in address.lower():
                        property_data['address'] = address
                        break
            
            # Property type extraction
            property_types = {
                'διαμέρισμα': 'Διαμέρισμα',
                'μονοκατοικία': 'Μονοκατοικία',
                'μεζονέτα': 'Μεζονέτα',
                'ρετιρέ': 'Ρετιρέ',
                'apartment': 'Διαμέρισμα',
                'house': 'Μονοκατοικία'
            }
            
            for type_key, type_value in property_types.items():
                if re.search(type_key, page_text, re.IGNORECASE):
                    property_data['property_type'] = type_value
                    break
            
            # Listing type
            if re.search(r'ενοικίαση|rental|rent|προς ενοικίαση', page_text, re.IGNORECASE):
                property_data['listing_type'] = 'Ενοικίαση'
            elif re.search(r'πώληση|sale|sell|προς πώληση', page_text, re.IGNORECASE):
                property_data['listing_type'] = 'Πώληση'
            
            # Rooms extraction
            rooms_patterns = [
                r'(\d+)\s*δωμάτι',
                r'(\d+)\s*υπνοδωμάτι',
                r'(\d+)\s*room',
                r'(\d+)\s*bedroom'
            ]
            
            for pattern in rooms_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    try:
                        rooms = int(match.group(1))
                        if 1 <= rooms <= 10:
                            property_data['rooms'] = rooms
                            break
                    except ValueError:
                        continue
            
            # Floor extraction
            floor_patterns = [
                r'(\d+)ος\s*όροφος',
                r'όροφος[:\s]*(\d+)',
                r'Όροφος[:\s]*(\d+)',
                r'floor[:\s]*(\d+)'
            ]
            
            for pattern in floor_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    property_data['floor'] = f"{match.group(1)}ος"
                    break
            
            # Data completeness score
            key_fields = ['price', 'sqm', 'energy_class', 'address', 'property_type']
            filled_fields = sum(1 for field in key_fields if property_data.get(field))
            property_data['data_completeness'] = filled_fields / len(key_fields)
            
            # Must have at least price OR sqm to be valid
            if property_data.get('price') or property_data.get('sqm'):
                return property_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Comprehensive data extraction failed: {e}")
            return None
    
    async def export_intelligence_results(self):
        """Export intelligence-based extraction results"""
        try:
            logger.info("💾 Exporting intelligence results...")
            
            # Filter for properties with meaningful data
            valid_properties = [
                prop for prop in self.extracted_properties 
                if prop.get('price') or prop.get('sqm')
            ]
            
            if not valid_properties:
                logger.warning("⚠️ No valid properties extracted")
                return
            
            # Export to JSON
            json_file = f'outputs/xe_gr_intelligence_{self.session_id}.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'intelligence_metadata': {
                        'session_id': self.session_id,
                        'extraction_timestamp': datetime.now().isoformat(),
                        'total_properties': len(valid_properties),
                        'method': 'intelligence_pattern_analysis',
                        'url_patterns_tested': len(self.property_url_patterns),
                        'neighborhoods_tested': len(self.neighborhoods)
                    },
                    'properties': valid_properties
                }, f, indent=2, ensure_ascii=False)
            
            # Export to CSV
            csv_file = f'outputs/xe_gr_intelligence_{self.session_id}.csv'
            if valid_properties:
                fieldnames = [
                    'url', 'neighborhood', 'title', 'price', 'sqm', 'energy_class',
                    'address', 'property_type', 'listing_type', 'rooms', 'floor',
                    'validation_score', 'data_completeness', 'discovery_method',
                    'extraction_timestamp'
                ]
                
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for prop in valid_properties:
                        writer.writerow({key: prop.get(key, '') for key in fieldnames})
            
            # Generate intelligence report
            logger.info("\n" + "="*80)
            logger.info("🧠 XE.GR INTELLIGENCE EXTRACTION - FINAL REPORT")
            logger.info("="*80)
            logger.info(f"✅ REAL Properties Extracted: {len(valid_properties)}")
            
            # Data quality analysis
            with_price = sum(1 for p in valid_properties if p.get('price'))
            with_sqm = sum(1 for p in valid_properties if p.get('sqm'))
            with_energy = sum(1 for p in valid_properties if p.get('energy_class'))
            with_address = sum(1 for p in valid_properties if p.get('address'))
            
            logger.info(f"💰 Properties with Price: {with_price}")
            logger.info(f"📐 Properties with SQM: {with_sqm}")
            logger.info(f"⚡ Properties with Energy Class: {with_energy}")
            logger.info(f"📍 Properties with Address: {with_address}")
            
            # Validation score analysis
            if valid_properties:
                avg_validation = sum(p.get('validation_score', 0) for p in valid_properties) / len(valid_properties)
                avg_completeness = sum(p.get('data_completeness', 0) for p in valid_properties) / len(valid_properties)
                logger.info(f"📊 Average Validation Score: {avg_validation:.2f}/5")
                logger.info(f"📊 Average Data Completeness: {avg_completeness:.2f}")
            
            logger.info(f"\n💾 Results saved:")
            logger.info(f"   📄 JSON: {json_file}")
            logger.info(f"   📊 CSV: {csv_file}")
            
            # Show sample results
            if valid_properties:
                logger.info(f"\n🏠 SAMPLE PROPERTIES:")
                for i, prop in enumerate(valid_properties[:5], 1):
                    title = prop.get('title', 'No title')[:50]
                    price = prop.get('price', 'N/A')
                    sqm = prop.get('sqm', 'N/A')
                    energy = prop.get('energy_class', 'N/A')
                    neighborhood = prop.get('neighborhood', 'N/A')
                    logger.info(f"   {i}. {neighborhood} | {title}... | €{price} | {sqm}m² | Energy {energy}")
            
            logger.info("="*80)
            
        except Exception as e:
            logger.error(f"❌ Intelligence results export failed: {e}")

async def main():
    """Run intelligence-based extraction"""
    scraper = XEIntelligenceScraper()
    await scraper.run_intelligence_mission()

if __name__ == "__main__":
    asyncio.run(main())