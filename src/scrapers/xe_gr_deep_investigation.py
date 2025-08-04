#!/usr/bin/env python3
"""
XE.GR DEEP INVESTIGATION - TWO NEIGHBORHOODS
Focused extraction for Κολωνάκι and Παγκράτι using intelligence patterns
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

class XEDeepInvestigation:
    """Deep investigation of two key Athens neighborhoods"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.extracted_properties = []
        
        # Focus on two prime neighborhoods first
        self.target_neighborhoods = {
            "Κολωνάκι": ["kolonaki", "κολωνάκι", "kolwnaki"],  # Premium area
            "Παγκράτι": ["pangrati", "παγκράτι", "pagrati"]    # Up-and-coming area
        }
        
        # Enhanced URL patterns based on reconnaissance intelligence
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
        
        # Refined ID ranges based on reconnaissance findings
        self.id_ranges = [
            (871000, 872000),  # Most active range discovered
            (873000, 874000),  # Secondary active range
            (875000, 876000),  # Extended range
            (877000, 878000),  # Additional range
            (879000, 880000)   # Final range
        ]
        
        # Target: 20 properties per neighborhood = 40 total
        self.target_per_neighborhood = 20
    
    async def run_deep_investigation(self):
        """Execute deep investigation on two neighborhoods"""
        logger.info("🔍 XE.GR DEEP INVESTIGATION - TWO NEIGHBORHOODS")
        logger.info("🎯 Target: Κολωνάκι & Παγκράτι (40 properties total)")
        
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
                
                # Phase 1: Systematic pattern testing
                logger.info("🔮 PHASE 1: Systematic Pattern Testing")
                await self.systematic_pattern_testing(page)
                
                # Phase 2: Density-based ID exploration
                logger.info("🎯 PHASE 2: Density-Based ID Exploration")
                await self.density_based_exploration(page)
                
                # Phase 3: Enhanced data extraction
                logger.info("📊 PHASE 3: Enhanced Data Extraction")
                await self.enhanced_data_extraction(page)
                
                # Phase 4: Quality analysis and export
                logger.info("💎 PHASE 4: Quality Analysis & Export")
                await self.quality_analysis_and_export()
                
            except Exception as e:
                logger.error(f"❌ Deep investigation failed: {e}")
            finally:
                logger.info("🔍 Investigation complete - keeping browser open for review...")
                await asyncio.sleep(45)
                await browser.close()
    
    async def systematic_pattern_testing(self, page):
        """Systematically test all pattern combinations"""
        try:
            logger.info("🔮 Testing all pattern combinations systematically...")
            
            for neighborhood_greek, neighborhood_variants in self.target_neighborhoods.items():
                neighborhood_found = 0
                logger.info(f"🏘️ Investigating {neighborhood_greek} (target: {self.target_per_neighborhood})")
                
                for neighborhood_en in neighborhood_variants:
                    if neighborhood_found >= self.target_per_neighborhood:
                        break
                    
                    logger.info(f"🔍 Testing variant: {neighborhood_en}")
                    
                    for start_id, end_id in self.id_ranges:
                        if neighborhood_found >= self.target_per_neighborhood:
                            break
                        
                        logger.info(f"📋 ID Range: {start_id}-{end_id}")
                        
                        # Test every 50th ID for better coverage
                        for property_id in range(start_id, end_id, 50):
                            if neighborhood_found >= self.target_per_neighborhood:
                                break
                            
                            # Test all URL patterns for this specific ID
                            for pattern_idx, pattern in enumerate(self.property_url_patterns):
                                url = pattern.format(id=property_id, neighborhood=neighborhood_en)
                                
                                if await self.test_and_store_property(page, url, neighborhood_greek):
                                    neighborhood_found += 1
                                    logger.info(f"✅ {neighborhood_greek} [{neighborhood_found}/{self.target_per_neighborhood}]: {url}")
                                    
                                    if neighborhood_found >= self.target_per_neighborhood:
                                        break
                                
                                await asyncio.sleep(0.8)  # Efficient testing pace
                
                logger.info(f"🎯 {neighborhood_greek} complete: {neighborhood_found} properties found")
                await asyncio.sleep(3)  # Neighborhood transition delay
            
            logger.info(f"📊 Systematic testing complete: {len(self.extracted_properties)} total properties")
        
        except Exception as e:
            logger.error(f"❌ Systematic testing failed: {e}")
    
    async def density_based_exploration(self, page):
        """Explore around successful IDs for higher density"""
        try:
            logger.info("🎯 Analyzing successful IDs for density exploration...")
            
            if not self.extracted_properties:
                logger.warning("⚠️ No successful properties for density analysis")
                return
            
            # Extract successful IDs
            successful_ids = []
            for prop in self.extracted_properties:
                id_match = re.search(r'/(\d{6,8})/', prop['url'])
                if id_match:
                    successful_ids.append(int(id_match.group(1)))
            
            if not successful_ids:
                logger.warning("⚠️ No IDs extracted for density analysis")
                return
            
            logger.info(f"🎯 Found {len(successful_ids)} successful IDs for density exploration")
            
            # Test around each successful ID
            additional_found = 0
            target_additional = 10  # Target additional properties
            
            for base_id in successful_ids[:5]:  # Test around top 5 successful IDs
                if additional_found >= target_additional:
                    break
                
                logger.info(f"🔍 Density exploration around ID {base_id}")
                
                # Test ±15 range around successful ID
                for offset in range(-15, 16, 3):
                    if additional_found >= target_additional:
                        break
                    
                    test_id = base_id + offset
                    if test_id <= 0:
                        continue
                    
                    # Test this ID with both neighborhoods
                    for neighborhood_greek, variants in self.target_neighborhoods.items():
                        if additional_found >= target_additional:
                            break
                        
                        for variant in variants[:1]:  # Test primary variant
                            for pattern in self.property_url_patterns[:3]:  # Test top 3 patterns
                                test_url = pattern.format(id=test_id, neighborhood=variant)
                                
                                # Skip if already found
                                if any(prop['url'] == test_url for prop in self.extracted_properties):
                                    continue
                                
                                if await self.test_and_store_property(page, test_url, neighborhood_greek):
                                    additional_found += 1
                                    logger.info(f"✅ DENSITY FIND {additional_found}: {test_url}")
                                
                                await asyncio.sleep(1)
                                
                                if additional_found >= target_additional:
                                    break
            
            logger.info(f"🎯 Density exploration found {additional_found} additional properties")
        
        except Exception as e:
            logger.error(f"❌ Density exploration failed: {e}")
    
    async def test_and_store_property(self, page, url: str, neighborhood: str) -> bool:
        """Test URL and store if valid property"""
        try:
            response = await page.goto(url, wait_until="load", timeout=12000)
            
            if response and response.status == 200:
                await asyncio.sleep(1.5)
                
                # Enhanced validation
                content = await page.content()
                page_text = await page.inner_text('body')
                
                # Multi-tier validation system
                validation_score = await self.calculate_validation_score(content, page_text, neighborhood)
                
                if validation_score >= 4:  # High-quality threshold
                    logger.info(f"✅ HIGH-QUALITY PROPERTY: {url} (score: {validation_score}/6)")
                    
                    self.extracted_properties.append({
                        'url': url,
                        'neighborhood': neighborhood,
                        'validation_score': validation_score,
                        'content_length': len(page_text),
                        'discovery_method': 'deep_investigation',
                        'discovered_at': datetime.now().isoformat(),
                        'status': 'validated'
                    })
                    
                    return True
                elif validation_score >= 3:  # Medium-quality
                    logger.info(f"🔶 MEDIUM-QUALITY PROPERTY: {url} (score: {validation_score}/6)")
                    
                    self.extracted_properties.append({
                        'url': url,
                        'neighborhood': neighborhood,
                        'validation_score': validation_score,
                        'content_length': len(page_text),
                        'discovery_method': 'deep_investigation',
                        'discovered_at': datetime.now().isoformat(),
                        'status': 'medium_quality'
                    })
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"❌ URL test failed {url}: {e}")
            return False
    
    async def calculate_validation_score(self, content: str, page_text: str, neighborhood: str) -> int:
        """Calculate comprehensive validation score (0-6)"""
        score = 0
        
        content_lower = content.lower()
        text_lower = page_text.lower()
        
        # 1. Property indicators (essential)
        property_indicators = ['τιμή', 'price', 'τ.μ', 'm²', 'ενοικίαση', 'πώληση', 'διαμέρισμα']
        if sum(1 for indicator in property_indicators if indicator in content_lower) >= 4:
            score += 1
        
        # 2. Location validation (essential)
        location_indicators = ['αθήνα', 'athens', neighborhood.lower()]
        if any(loc in content_lower for loc in location_indicators):
            score += 1
        
        # 3. Substantial content (quality indicator)
        if len(page_text) > 4000:  # Rich content
            score += 1
        
        # 4. Price information (data richness)
        price_patterns = [r'€\s*\d{2,6}', r'\d{2,6}\s*€', r'\d{1,3}(?:\.\d{3})*\s*€']
        if any(re.search(pattern, content) for pattern in price_patterns):
            score += 1
        
        # 5. Area information (data richness)
        area_patterns = [r'\d+\s*τ\.?μ\.?', r'\d+\s*m²', r'\d+\s*sqm']
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in area_patterns):
            score += 1
        
        # 6. Energy class (premium data)
        energy_patterns = [r'ενεργειακή\s+κλάση', r'energy\s+class', r'κλάση\s+[A-G]']
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in energy_patterns):
            score += 1
        
        return score
    
    async def enhanced_data_extraction(self, page):
        """Extract detailed data from all validated properties"""
        try:
            logger.info(f"📊 Extracting detailed data from {len(self.extracted_properties)} properties...")
            
            for i, property_info in enumerate(self.extracted_properties):
                url = property_info['url']
                logger.info(f"📋 Extracting {i+1}/{len(self.extracted_properties)}: {url}")
                
                try:
                    response = await page.goto(url, wait_until="networkidle", timeout=15000)
                    
                    if response and response.status == 200:
                        await asyncio.sleep(2)
                        
                        # Extract comprehensive data
                        extracted_data = await self.extract_property_details(page, url, property_info)
                        
                        if extracted_data:
                            # Merge extracted data with property info
                            property_info.update(extracted_data)
                            logger.info(f"✅ Extracted: {extracted_data.get('title', 'No title')[:40]}...")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract {url}: {e}")
                    property_info['extraction_error'] = str(e)
                
                await asyncio.sleep(1.5)  # Respectful extraction pace
        
        except Exception as e:
            logger.error(f"❌ Enhanced data extraction failed: {e}")
    
    async def extract_property_details(self, page, url: str, existing_info: Dict) -> Optional[Dict]:
        """Extract comprehensive property details"""
        try:
            page_text = await page.inner_text('body')
            title = await page.title()
            
            details = {
                'title': title,
                'extraction_timestamp': datetime.now().isoformat(),
                'data_quality': 'high' if existing_info['validation_score'] >= 4 else 'medium'
            }
            
            # Enhanced price extraction with multiple patterns
            price_patterns = [
                r'(\d{1,3}(?:\.\d{3})*)\s*€',
                r'€\s*(\d{1,3}(?:\.\d{3})*)',
                r'τιμή[:\s]*(\d{1,3}(?:\.\d{3})*)',
                r'Τιμή[:\s]*(\d{1,3}(?:\.\d{3})*)',
                r'ΤΙΜΗ[:\s]*(\d{1,3}(?:\.\d{3})*)',
                r'Αξία[:\s]*(\d{1,3}(?:\.\d{3})*)'
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    try:
                        price_str = match.group(1).replace('.', '')
                        price = float(price_str)
                        if 100 <= price <= 10000000:  # Realistic price range
                            details['price'] = price
                            details['price_currency'] = 'EUR'
                            break
                    except ValueError:
                        continue
            
            # Enhanced SQM extraction
            sqm_patterns = [
                r'(\d+(?:[.,]\d+)?)\s*τ\.?μ\.?',
                r'(\d+(?:[.,]\d+)?)\s*m²',
                r'(\d+(?:[.,]\d+)?)\s*sq\.?m',
                r'εμβαδόν[:\s]*(\d+(?:[.,]\d+)?)',
                r'Εμβαδόν[:\s]*(\d+(?:[.,]\d+)?)',
                r'τετραγωνικά[:\s]*(\d+(?:[.,]\d+)?)'
            ]
            
            for pattern in sqm_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    try:
                        sqm = float(match.group(1).replace(',', '.'))
                        if 15 <= sqm <= 800:  # Realistic area range
                            details['sqm'] = sqm
                            break
                    except ValueError:
                        continue
            
            # Enhanced energy class extraction
            energy_patterns = [
                r'ενεργειακή\s+κλάση[:\s]*([A-G][+\-]?)',
                r'Ενεργειακή\s+κλάση[:\s]*([A-G][+\-]?)',
                r'ΕΝΕΡΓΕΙΑΚΗ\s+ΚΛΑΣΗ[:\s]*([A-G][+\-]?)',
                r'energy\s+class[:\s]*([A-G][+\-]?)',
                r'Energy\s+Class[:\s]*([A-G][+\-]?)',
                r'κλάση\s+ενέργειας[:\s]*([A-G][+\-]?)'
            ]
            
            for pattern in energy_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    energy_class = match.group(1).upper()
                    if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                        details['energy_class'] = energy_class
                        break
            
            # Enhanced address extraction
            address_patterns = [
                r'διεύθυνση[:\s]*([^,\n\.]{15,120})',
                r'Διεύθυνση[:\s]*([^,\n\.]{15,120})',
                r'περιοχή[:\s]*([^,\n\.]{10,100})',
                r'Περιοχή[:\s]*([^,\n\.]{10,100})',
                r'τοποθεσία[:\s]*([^,\n\.]{10,100})',
                r'Αθήνα[,\s]*([^,\n\.]{8,80})'
            ]
            
            for pattern in address_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    address = match.group(1).strip()
                    if len(address) > 8:
                        details['address'] = address
                        break
            
            # Property type classification
            property_types = {
                'διαμέρισμα': 'Διαμέρισμα',
                'μονοκατοικία': 'Μονοκατοικία', 
                'μεζονέτα': 'Μεζονέτα',
                'ρετιρέ': 'Ρετιρέ',
                'penthouse': 'Ρετιρέ',
                'apartment': 'Διαμέρισμα',
                'house': 'Μονοκατοικία',
                'maisonette': 'Μεζονέτα'
            }
            
            for type_key, type_value in property_types.items():
                if re.search(type_key, page_text, re.IGNORECASE):
                    details['property_type'] = type_value
                    break
            
            # Listing type determination
            if re.search(r'ενοικίαση|rental|rent|προς ενοικίαση|for rent', page_text, re.IGNORECASE):
                details['listing_type'] = 'Ενοικίαση'
            elif re.search(r'πώληση|sale|sell|προς πώληση|for sale', page_text, re.IGNORECASE):
                details['listing_type'] = 'Πώληση'
            
            # Room count extraction
            rooms_patterns = [
                r'(\d+)\s*δωμάτι',
                r'(\d+)\s*υπνοδωμάτι',
                r'(\d+)\s*room',
                r'(\d+)\s*bedroom',
                r'(\d+)\s*χώρ'
            ]
            
            for pattern in rooms_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    try:
                        rooms = int(match.group(1))
                        if 1 <= rooms <= 10:
                            details['rooms'] = rooms
                            break
                    except ValueError:
                        continue
            
            # Floor extraction
            floor_patterns = [
                r'(\d+)ος\s*όροφος',
                r'όροφος[:\s]*(\d+)',
                r'Όροφος[:\s]*(\d+)',
                r'floor[:\s]*(\d+)',
                r'(\d+)(st|nd|rd|th)\s*floor'
            ]
            
            for pattern in floor_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    floor_num = match.group(1)
                    details['floor'] = f"{floor_num}ος"
                    break
            
            # Calculate data completeness
            key_fields = ['price', 'sqm', 'energy_class', 'address', 'property_type', 'rooms']
            filled_fields = sum(1 for field in key_fields if details.get(field))
            details['data_completeness'] = filled_fields / len(key_fields)
            
            # Must have critical data to be considered valid
            if details.get('price') or details.get('sqm'):
                return details
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Property details extraction failed: {e}")
            return None
    
    async def quality_analysis_and_export(self):
        """Analyze data quality and export results"""
        try:
            logger.info("💎 Performing quality analysis and export...")
            
            # Filter for properties with meaningful data
            valid_properties = [
                prop for prop in self.extracted_properties 
                if prop.get('price') or prop.get('sqm')
            ]
            
            if not valid_properties:
                logger.warning("⚠️ No valid properties with meaningful data found")
                return
            
            # Quality analysis
            high_quality = [p for p in valid_properties if p.get('validation_score', 0) >= 4]
            medium_quality = [p for p in valid_properties if p.get('validation_score', 0) == 3]
            
            with_price = [p for p in valid_properties if p.get('price')]
            with_sqm = [p for p in valid_properties if p.get('sqm')]
            with_energy = [p for p in valid_properties if p.get('energy_class')]
            with_address = [p for p in valid_properties if p.get('address')]
            with_rooms = [p for p in valid_properties if p.get('rooms')]
            
            # Neighborhood breakdown
            kolonaki_props = [p for p in valid_properties if p.get('neighborhood') == 'Κολωνάκι']
            pangrati_props = [p for p in valid_properties if p.get('neighborhood') == 'Παγκράτι']
            
            # Export to JSON
            json_file = f'outputs/xe_gr_investigation_{self.session_id}.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'investigation_metadata': {
                        'session_id': self.session_id,
                        'extraction_timestamp': datetime.now().isoformat(),
                        'neighborhoods_investigated': list(self.target_neighborhoods.keys()),
                        'total_properties': len(valid_properties),
                        'high_quality_properties': len(high_quality),
                        'medium_quality_properties': len(medium_quality),
                        'method': 'deep_investigation_two_neighborhoods'
                    },
                    'quality_metrics': {
                        'properties_with_price': len(with_price),
                        'properties_with_sqm': len(with_sqm),
                        'properties_with_energy_class': len(with_energy),
                        'properties_with_address': len(with_address),
                        'properties_with_rooms': len(with_rooms),
                        'average_data_completeness': sum(p.get('data_completeness', 0) for p in valid_properties) / len(valid_properties) if valid_properties else 0
                    },
                    'neighborhood_breakdown': {
                        'Κολωνάκι': len(kolonaki_props),
                        'Παγκράτι': len(pangrati_props)
                    },
                    'properties': valid_properties
                }, f, indent=2, ensure_ascii=False)
            
            # Export to CSV
            csv_file = f'outputs/xe_gr_investigation_{self.session_id}.csv'
            if valid_properties:
                fieldnames = [
                    'url', 'neighborhood', 'title', 'price', 'price_currency', 'sqm', 'energy_class',
                    'address', 'property_type', 'listing_type', 'rooms', 'floor',
                    'validation_score', 'data_completeness', 'data_quality',
                    'discovery_method', 'extraction_timestamp'
                ]
                
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for prop in valid_properties:
                        writer.writerow({key: prop.get(key, '') for key in fieldnames})
            
            # Generate comprehensive report
            logger.info("\n" + "="*80)
            logger.info("🔍 XE.GR DEEP INVESTIGATION - FINAL REPORT")
            logger.info("="*80)
            logger.info(f"✅ Total Properties Extracted: {len(valid_properties)}")
            logger.info(f"💎 High Quality (Score ≥4): {len(high_quality)}")
            logger.info(f"🔶 Medium Quality (Score =3): {len(medium_quality)}")
            
            logger.info(f"\n📊 DATA RICHNESS:")
            logger.info(f"💰 Properties with Price: {len(with_price)}")
            logger.info(f"📐 Properties with SQM: {len(with_sqm)}")
            logger.info(f"⚡ Properties with Energy Class: {len(with_energy)}")
            logger.info(f"📍 Properties with Address: {len(with_address)}")
            logger.info(f"🏠 Properties with Room Count: {len(with_rooms)}")
            
            logger.info(f"\n🏘️ NEIGHBORHOOD BREAKDOWN:")
            logger.info(f"🏛️ Κολωνάκι: {len(kolonaki_props)} properties")
            logger.info(f"🏢 Παγκράτι: {len(pangrati_props)} properties")
            
            if valid_properties:
                avg_completeness = sum(p.get('data_completeness', 0) for p in valid_properties) / len(valid_properties)
                logger.info(f"\n📈 QUALITY METRICS:")
                logger.info(f"📊 Average Data Completeness: {avg_completeness:.2f}")
                
                # Price analysis
                prices = [p['price'] for p in valid_properties if p.get('price')]
                if prices:
                    avg_price = sum(prices) / len(prices)
                    logger.info(f"💰 Average Price: €{avg_price:,.0f}")
                    logger.info(f"💰 Price Range: €{min(prices):,.0f} - €{max(prices):,.0f}")
                
                # Area analysis
                areas = [p['sqm'] for p in valid_properties if p.get('sqm')]
                if areas:
                    avg_area = sum(areas) / len(areas)
                    logger.info(f"📐 Average Area: {avg_area:.1f}m²")
                    logger.info(f"📐 Area Range: {min(areas):.0f} - {max(areas):.0f}m²")
            
            logger.info(f"\n💾 Results saved:")
            logger.info(f"   📄 JSON: {json_file}")
            logger.info(f"   📊 CSV: {csv_file}")
            
            # Show sample results
            if valid_properties:
                logger.info(f"\n🏠 SAMPLE PROPERTIES:")
                for i, prop in enumerate(valid_properties[:5], 1):
                    title = prop.get('title', 'No title')[:40]
                    price = f"€{prop.get('price', 'N/A')}"
                    sqm = f"{prop.get('sqm', 'N/A')}m²"
                    energy = prop.get('energy_class', 'N/A')
                    neighborhood = prop.get('neighborhood', 'N/A')
                    score = prop.get('validation_score', 0)
                    logger.info(f"   {i}. {neighborhood} | {title}... | {price} | {sqm} | Energy {energy} | Score {score}/6")
            
            logger.info("="*80)
            
        except Exception as e:
            logger.error(f"❌ Quality analysis and export failed: {e}")

async def main():
    """Run deep investigation on two neighborhoods"""
    scraper = XEDeepInvestigation()
    await scraper.run_deep_investigation()

if __name__ == "__main__":
    asyncio.run(main())