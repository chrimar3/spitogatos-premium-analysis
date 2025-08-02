#!/usr/bin/env python3
"""
XE.GR ENERGY CLASS FOCUSED SCRAPER
Enhanced scraper specifically designed to find properties WITH energy class data
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

class XEEnergyFocusedScraper:
    """Specialized scraper targeting properties with energy class information"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.extracted_properties = []
        
        # Focus on two neighborhoods but with energy class requirement
        self.target_neighborhoods = {
            "Κολωνάκι": ["kolonaki", "κολωνάκι"],
            "Παγκράτι": ["pangrati", "παγκράτι"]
        }
        
        # Enhanced URL patterns - focusing on newer properties more likely to have energy data
        self.property_url_patterns = [
            "https://www.xe.gr/property/d/enoikiaseis-katoikion/{id}/athens-{neighborhood}",
            "https://www.xe.gr/property/d/poliseis-katoikion/{id}/athens-{neighborhood}",
            "https://xe.gr/property/d/enoikiaseis-katoikion/{id}/athens-{neighborhood}",
            "https://xe.gr/property/d/poliseis-katoikion/{id}/athens-{neighborhood}",
            "https://www.xe.gr/property/d/enoikiaseis-diamerismaton/{id}/athens-{neighborhood}",
            "https://www.xe.gr/property/d/poliseis-diamerismaton/{id}/athens-{neighborhood}",
            "https://xe.gr/property/d/enoikiaseis-diamerismaton/{id}/athens-{neighborhood}",
            "https://xe.gr/property/d/poliseis-diamerismaton/{id}/athens-{neighborhood}"
        ]
        
        # Expanded ID ranges - newer properties more likely to have energy data
        self.id_ranges = [
            (880000, 885000),  # Newer range more likely to have energy data
            (875000, 880000),  # Recent range
            (870000, 875000),  # Baseline range
            (885000, 890000),  # Very new range
            (865000, 870000)   # Secondary range
        ]
        
        # Target: Properties WITH energy class data
        self.target_properties_with_energy = 20
        self.min_energy_properties = 10  # Minimum acceptable
    
    async def run_energy_focused_mission(self):
        """Execute energy-class focused extraction"""
        logger.info("⚡ XE.GR ENERGY CLASS FOCUSED EXTRACTION")
        logger.info("🎯 Target: 20 properties WITH energy class data")
        
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
                
                # Phase 1: Energy-focused discovery
                logger.info("⚡ PHASE 1: Energy Class Discovery")
                await self.energy_focused_discovery(page)
                
                # Phase 2: Enhanced energy extraction
                logger.info("🔍 PHASE 2: Enhanced Energy Data Extraction")
                await self.enhanced_energy_extraction(page)
                
                # Phase 3: Energy validation and analysis
                logger.info("✅ PHASE 3: Energy Validation & Analysis")
                await self.energy_validation_analysis()
                
            except Exception as e:
                logger.error(f"❌ Energy-focused mission failed: {e}")
            finally:
                logger.info("⚡ Keeping browser open for energy class inspection...")
                await asyncio.sleep(60)
                await browser.close()
    
    async def energy_focused_discovery(self, page):
        """Discover properties specifically looking for energy class indicators"""
        try:
            logger.info("⚡ Searching for properties with energy class data...")
            
            energy_properties_found = 0
            total_tested = 0
            
            for neighborhood_greek, neighborhood_variants in self.target_neighborhoods.items():
                if energy_properties_found >= self.target_properties_with_energy:
                    break
                
                logger.info(f"🏘️ Energy search in {neighborhood_greek}")
                
                for neighborhood_en in neighborhood_variants[:1]:  # Focus on primary variant
                    if energy_properties_found >= self.target_properties_with_energy:
                        break
                    
                    for start_id, end_id in self.id_ranges:
                        if energy_properties_found >= self.target_properties_with_energy:
                            break
                        
                        logger.info(f"🔍 Energy search ID range: {start_id}-{end_id}")
                        
                        # Test every 25th ID for faster but thorough coverage
                        for property_id in range(start_id, end_id, 25):
                            if energy_properties_found >= self.target_properties_with_energy:
                                break
                            
                            total_tested += 1
                            
                            # Test selected patterns (focus on most promising)
                            for pattern in self.property_url_patterns[:4]:  # Test top 4 patterns
                                url = pattern.format(id=property_id, neighborhood=neighborhood_en)
                                
                                energy_data = await self.test_for_energy_class(page, url, neighborhood_greek)
                                if energy_data:
                                    energy_properties_found += 1
                                    logger.info(f"⚡ ENERGY FOUND [{energy_properties_found}/{self.target_properties_with_energy}]: {energy_data['energy_class']} | {url}")
                                    
                                    if energy_properties_found >= self.target_properties_with_energy:
                                        break
                                
                                await asyncio.sleep(1.2)  # Slightly slower for thorough analysis
                                
                                if total_tested % 50 == 0:
                                    logger.info(f"📊 Progress: {energy_properties_found} energy properties found in {total_tested} tests")
            
            logger.info(f"⚡ Energy discovery complete: {energy_properties_found} properties with energy class found")
            logger.info(f"📊 Success rate: {energy_properties_found}/{total_tested} ({100*energy_properties_found/total_tested:.1f}%)")
        
        except Exception as e:
            logger.error(f"❌ Energy discovery failed: {e}")
    
    async def test_for_energy_class(self, page, url: str, neighborhood: str) -> Optional[Dict]:
        """Test URL specifically for energy class data"""
        try:
            response = await page.goto(url, wait_until="load", timeout=15000)
            
            if response and response.status == 200:
                await asyncio.sleep(2)
                
                # Get full page content for analysis
                content = await page.content()
                page_text = await page.inner_text('body')
                
                # Enhanced energy class detection
                energy_class = await self.extract_energy_class_comprehensive(content, page_text)
                
                if energy_class:
                    # Also extract other essential data
                    property_data = await self.extract_essential_data(page, url, neighborhood, energy_class)
                    
                    if property_data:
                        self.extracted_properties.append(property_data)
                        return property_data
            
            return None
            
        except Exception as e:
            logger.debug(f"❌ Energy test failed {url}: {e}")
            return None
    
    async def extract_energy_class_comprehensive(self, content: str, page_text: str) -> Optional[str]:
        """Comprehensive energy class extraction with multiple strategies"""
        try:
            # Strategy 1: Direct energy class patterns (Greek)
            energy_patterns_greek = [
                r'ενεργειακή\s+κλάση[:\s]*([A-G][+\-]?)',
                r'Ενεργειακή\s+κλάση[:\s]*([A-G][+\-]?)',
                r'ΕΝΕΡΓΕΙΑΚΗ\s+ΚΛΑΣΗ[:\s]*([A-G][+\-]?)',
                r'ενεργειακό\s+πιστοποιητικό[:\s]*([A-G][+\-]?)',
                r'κλάση\s+ενέργειας[:\s]*([A-G][+\-]?)',
                r'κατηγορία\s+ενέργειας[:\s]*([A-G][+\-]?)'
            ]
            
            # Strategy 2: English energy patterns
            energy_patterns_english = [
                r'energy\s+class[:\s]*([A-G][+\-]?)',
                r'Energy\s+Class[:\s]*([A-G][+\-]?)',
                r'ENERGY\s+CLASS[:\s]*([A-G][+\-]?)',
                r'energy\s+rating[:\s]*([A-G][+\-]?)',
                r'energy\s+certificate[:\s]*([A-G][+\-]?)'
            ]
            
            # Strategy 3: HTML attribute patterns
            html_patterns = [
                r'data-energy["\']?\s*[:=]\s*["\']?([A-G][+\-]?)',
                r'energy["\']?\s*[:=]\s*["\']?([A-G][+\-]?)',
                r'class=["\']energy["\'][^>]*>([A-G][+\-]?)',
                r'<span[^>]*energy[^>]*>([A-G][+\-]?)</span>'
            ]
            
            # Strategy 4: Standalone class indicators
            standalone_patterns = [
                r'κλάση\s+([A-G][+\-]?)',
                r'Class\s+([A-G][+\-]?)',
                r'Rating\s+([A-G][+\-]?)',
                r'\b([A-G][+])\b(?=.*ενεργ)',  # A+ near energy terms
                r'\b([A-G])\b(?=.*ενεργ)'     # A near energy terms
            ]
            
            # Test all pattern groups
            all_patterns = [
                ('Greek patterns', energy_patterns_greek),
                ('English patterns', energy_patterns_english), 
                ('HTML patterns', html_patterns),
                ('Standalone patterns', standalone_patterns)
            ]
            
            full_text = content + " " + page_text
            
            for pattern_group_name, patterns in all_patterns:
                for pattern in patterns:
                    matches = re.finditer(pattern, full_text, re.IGNORECASE)
                    for match in matches:
                        energy_class = match.group(1).upper()
                        if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                            logger.info(f"⚡ Energy class found via {pattern_group_name}: {energy_class}")
                            return energy_class
            
            # Strategy 5: Look for energy-related images or icons
            energy_image_patterns = [
                r'energy[^>]*class[^>]*([A-G][+\-]?)',
                r'([A-G][+\-]?)[^>]*energy',
                r'img[^>]*alt=["\'][^"\']*([A-G][+\-]?)[^"\']*energy',
                r'energy[^>]*src=[^>]*([A-G][+\-]?)'
            ]
            
            for pattern in energy_image_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    energy_class = match.group(1).upper()
                    if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                        logger.info(f"⚡ Energy class found via image pattern: {energy_class}")
                        return energy_class
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Energy extraction failed: {e}")
            return None
    
    async def extract_essential_data(self, page, url: str, neighborhood: str, energy_class: str) -> Optional[Dict]:
        """Extract essential data including verified energy class"""
        try:
            page_text = await page.inner_text('body')
            title = await page.title()
            
            property_data = {
                'url': url,
                'neighborhood': neighborhood,
                'title': title,
                'energy_class': energy_class,  # Confirmed energy class
                'discovery_method': 'energy_focused',
                'discovered_at': datetime.now().isoformat(),
                'status': 'energy_verified'
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
                    try:
                        price_str = match.group(1).replace('.', '')
                        price = float(price_str)
                        if 100 <= price <= 10000000:
                            property_data['price'] = price
                            property_data['price_currency'] = 'EUR'
                            break
                    except ValueError:
                        continue
            
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
                    try:
                        sqm = float(match.group(1).replace(',', '.'))
                        if 15 <= sqm <= 800:
                            property_data['sqm'] = sqm
                            break
                    except ValueError:
                        continue
            
            # Property type
            property_types = {
                'διαμέρισμα': 'Διαμέρισμα',
                'μονοκατοικία': 'Μονοκατοικία',
                'μεζονέτα': 'Μεζονέτα',
                'ρετιρέ': 'Ρετιρέ'
            }
            
            for type_key, type_value in property_types.items():
                if re.search(type_key, page_text, re.IGNORECASE):
                    property_data['property_type'] = type_value
                    break
            
            # Listing type
            if re.search(r'ενοικίαση|rental|rent', page_text, re.IGNORECASE):
                property_data['listing_type'] = 'Ενοικίαση'
            elif re.search(r'πώληση|sale|sell', page_text, re.IGNORECASE):
                property_data['listing_type'] = 'Πώληση'
            
            # Validation: Must have energy class + either price or SQM
            if energy_class and (property_data.get('price') or property_data.get('sqm')):
                # Calculate data completeness
                key_fields = ['price', 'sqm', 'energy_class', 'property_type', 'listing_type']
                filled_fields = sum(1 for field in key_fields if property_data.get(field))
                property_data['data_completeness'] = filled_fields / len(key_fields)
                
                return property_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Essential data extraction failed: {e}")
            return None
    
    async def enhanced_energy_extraction(self, page):
        """Enhanced extraction focusing on energy data quality"""
        try:
            logger.info(f"🔍 Enhanced energy extraction for {len(self.extracted_properties)} properties...")
            
            for i, property_info in enumerate(self.extracted_properties):
                url = property_info['url']
                logger.info(f"⚡ Energy analysis {i+1}/{len(self.extracted_properties)}: {url}")
                
                try:
                    response = await page.goto(url, wait_until="networkidle", timeout=20000)
                    
                    if response and response.status == 200:
                        await asyncio.sleep(3)
                        
                        # Deep energy analysis
                        energy_details = await self.deep_energy_analysis(page)
                        
                        if energy_details:
                            property_info.update(energy_details)
                            logger.info(f"✅ Enhanced: {energy_details.get('energy_confidence', 'N/A')} confidence")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Enhanced extraction failed for {url}: {e}")
                    property_info['extraction_error'] = str(e)
                
                await asyncio.sleep(2)
        
        except Exception as e:
            logger.error(f"❌ Enhanced energy extraction failed: {e}")
    
    async def deep_energy_analysis(self, page) -> Optional[Dict]:
        """Deep analysis of energy class context and reliability"""
        try:
            content = await page.content()
            page_text = await page.inner_text('body')
            
            energy_details = {
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            # Look for energy certificate number
            cert_patterns = [
                r'πιστοποιητικό[^0-9]*([0-9]{4,})',
                r'certificate[^0-9]*([0-9]{4,})',
                r'αριθμός[^0-9]*([0-9]{4,})'
            ]
            
            for pattern in cert_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    energy_details['energy_certificate_number'] = match.group(1)
                    break
            
            # Look for energy consumption values
            consumption_patterns = [
                r'κατανάλωση[:\s]*(\d+(?:[.,]\d+)?)\s*kwh',
                r'consumption[:\s]*(\d+(?:[.,]\d+)?)\s*kwh',
                r'(\d+(?:[.,]\d+)?)\s*kwh'
            ]
            
            for pattern in consumption_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    try:
                        consumption = float(match.group(1).replace(',', '.'))
                        energy_details['energy_consumption_kwh'] = consumption
                        break
                    except ValueError:
                        continue
            
            # Energy class confidence based on context
            energy_context_indicators = [
                'ενεργειακό πιστοποιητικό',
                'energy certificate',
                'κατανάλωση ενέργειας',
                'energy consumption',
                'ενεργειακή απόδοση',
                'energy performance'
            ]
            
            context_count = sum(1 for indicator in energy_context_indicators 
                              if indicator in page_text.lower())
            
            if context_count >= 2:
                energy_details['energy_confidence'] = 'high'
            elif context_count == 1:
                energy_details['energy_confidence'] = 'medium'
            else:
                energy_details['energy_confidence'] = 'basic'
            
            return energy_details if energy_details.get('energy_confidence') else None
            
        except Exception as e:
            logger.error(f"❌ Deep energy analysis failed: {e}")
            return None
    
    async def energy_validation_analysis(self):
        """Validate and analyze energy class findings"""
        try:
            logger.info("✅ Performing energy validation and analysis...")
            
            # Filter for properties with confirmed energy class
            energy_properties = [
                prop for prop in self.extracted_properties 
                if prop.get('energy_class')
            ]
            
            if not energy_properties:
                logger.warning("❌ NO PROPERTIES WITH ENERGY CLASS FOUND!")
                return
            
            # Analyze energy distribution
            energy_distribution = {}
            for prop in energy_properties:
                energy_class = prop['energy_class']
                energy_distribution[energy_class] = energy_distribution.get(energy_class, 0) + 1
            
            # Quality analysis
            with_price = [p for p in energy_properties if p.get('price')]
            with_sqm = [p for p in energy_properties if p.get('sqm')]
            with_cert_number = [p for p in energy_properties if p.get('energy_certificate_number')]
            with_consumption = [p for p in energy_properties if p.get('energy_consumption_kwh')]
            
            high_confidence = [p for p in energy_properties if p.get('energy_confidence') == 'high']
            medium_confidence = [p for p in energy_properties if p.get('energy_confidence') == 'medium']
            
            # Export results
            json_file = f'outputs/xe_gr_energy_focused_{self.session_id}.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'energy_extraction_metadata': {
                        'session_id': self.session_id,
                        'extraction_timestamp': datetime.now().isoformat(),
                        'neighborhoods_investigated': list(self.target_neighborhoods.keys()),
                        'total_energy_properties': len(energy_properties),
                        'method': 'energy_class_focused_extraction'
                    },
                    'energy_analysis': {
                        'energy_class_distribution': energy_distribution,
                        'properties_with_price': len(with_price),
                        'properties_with_sqm': len(with_sqm),
                        'properties_with_certificate_number': len(with_cert_number),
                        'properties_with_consumption_data': len(with_consumption),
                        'high_confidence_energy': len(high_confidence),
                        'medium_confidence_energy': len(medium_confidence)
                    },
                    'properties': energy_properties
                }, f, indent=2, ensure_ascii=False)
            
            # Export to CSV
            csv_file = f'outputs/xe_gr_energy_focused_{self.session_id}.csv'
            if energy_properties:
                fieldnames = [
                    'url', 'neighborhood', 'title', 'energy_class', 'price', 'price_currency',
                    'sqm', 'property_type', 'listing_type', 'energy_confidence',
                    'energy_certificate_number', 'energy_consumption_kwh',
                    'data_completeness', 'discovery_method', 'extraction_timestamp'
                ]
                
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for prop in energy_properties:
                        writer.writerow({key: prop.get(key, '') for key in fieldnames})
            
            # Generate energy report
            logger.info("\n" + "="*80)
            logger.info("⚡ XE.GR ENERGY CLASS FOCUSED EXTRACTION - FINAL REPORT")
            logger.info("="*80)
            logger.info(f"✅ Properties WITH Energy Class: {len(energy_properties)}")
            
            if len(energy_properties) >= self.min_energy_properties:
                logger.info(f"🎯 SUCCESS: Found {len(energy_properties)} properties with energy data!")
            else:
                logger.info(f"⚠️ BELOW TARGET: Only {len(energy_properties)} properties (target: {self.min_energy_properties})")
            
            logger.info(f"\n⚡ ENERGY CLASS DISTRIBUTION:")
            for energy_class, count in sorted(energy_distribution.items()):
                logger.info(f"   {energy_class}: {count} properties")
            
            logger.info(f"\n📊 DATA COMPLETENESS:")
            logger.info(f"💰 With Price: {len(with_price)}")
            logger.info(f"📐 With SQM: {len(with_sqm)}")
            logger.info(f"📜 With Certificate Number: {len(with_cert_number)}")
            logger.info(f"⚡ With Consumption Data: {len(with_consumption)}")
            
            logger.info(f"\n🔍 CONFIDENCE LEVELS:")
            logger.info(f"🔥 High Confidence: {len(high_confidence)}")
            logger.info(f"🔶 Medium Confidence: {len(medium_confidence)}")
            
            logger.info(f"\n💾 Results saved:")
            logger.info(f"   📄 JSON: {json_file}")
            logger.info(f"   📊 CSV: {csv_file}")
            
            # Show sample results
            if energy_properties:
                logger.info(f"\n⚡ SAMPLE ENERGY PROPERTIES:")
                for i, prop in enumerate(energy_properties[:5], 1):
                    title = prop.get('title', 'No title')[:30]
                    energy = prop.get('energy_class', 'N/A')
                    price = f"€{prop.get('price', 'N/A')}"
                    sqm = f"{prop.get('sqm', 'N/A')}m²"
                    confidence = prop.get('energy_confidence', 'N/A')
                    logger.info(f"   {i}. Energy {energy} | {title}... | {price} | {sqm} | {confidence}")
            
            logger.info("="*80)
            
        except Exception as e:
            logger.error(f"❌ Energy validation analysis failed: {e}")

async def main():
    """Run energy-focused extraction"""
    scraper = XEEnergyFocusedScraper()
    await scraper.run_energy_focused_mission()

if __name__ == "__main__":
    asyncio.run(main())