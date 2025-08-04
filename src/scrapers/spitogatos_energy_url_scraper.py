#!/usr/bin/env python3
"""
SPITOGATOS ENERGY CLASS & URL SCRAPER
Extract properties with energy class data and complete URLs
"""

import asyncio
import json
import logging
import re
import csv
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpitogatosEnergyURLScraper:
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.properties = []
        
        # Use working search URLs from previous successful extraction
        self.search_urls = {
            'athens_center_sale': 'https://www.spitogatos.gr/en/for_sale-homes/athens-center',
            'athens_center_rent': 'https://www.spitogatos.gr/en/for_rent-homes/athens-center',
            'athens_sale': 'https://www.spitogatos.gr/en/for_sale-homes/athens',
            'athens_rent': 'https://www.spitogatos.gr/en/for_rent-homes/athens'
        }
        
        self.target_properties = 15
    
    async def run_energy_url_extraction(self):
        """Extract properties with focus on energy class and URLs"""
        logger.info("🔋 SPITOGATOS ENERGY CLASS & URL EXTRACTION")
        logger.info("🎯 Mission: Extract properties with energy class data and complete URLs")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            try:
                page = await context.new_page()
                
                # Process each search URL
                for search_name, search_url in self.search_urls.items():
                    if len(self.properties) >= self.target_properties:
                        break
                    
                    logger.info(f"🔍 Processing: {search_name}")
                    await self.process_search_for_energy(page, search_url, search_name)
                
                # Generate comprehensive results
                await self.generate_energy_url_results()
                
            except Exception as e:
                logger.error(f"❌ Extraction failed: {e}")
            finally:
                await browser.close()
    
    async def process_search_for_energy(self, page, search_url: str, search_name: str):
        """Process search results with energy class focus"""
        try:
            logger.info(f"🌐 Accessing: {search_url}")
            
            response = await page.goto(search_url, wait_until="load", timeout=20000)
            
            if response and response.status == 200:
                await asyncio.sleep(3)
                
                # Extract property URLs
                property_urls = await self.extract_property_urls(page)
                logger.info(f"📋 Found {len(property_urls)} property URLs for {search_name}")
                
                # Process properties with energy focus
                for i, property_url in enumerate(property_urls[:4]):  # Limit to 4 per search
                    if len(self.properties) >= self.target_properties:
                        break
                    
                    logger.info(f"🏠 Processing {i+1}/4: {property_url}")
                    
                    property_data = await self.extract_property_with_energy_focus(page, property_url, search_name)
                    if property_data:
                        self.properties.append(property_data)
                        
                        # Log what we found
                        neighborhood = property_data.get('neighborhood', 'Unknown')
                        price = f"€{property_data.get('price', 'N/A'):,}" if property_data.get('price') else 'N/A'
                        sqm = f"{property_data.get('sqm', 'N/A')}m²" if property_data.get('sqm') else 'N/A'
                        energy = property_data.get('energy_class', 'No energy data')
                        
                        logger.info(f"✅ Extracted: {neighborhood} | {price} | {sqm} | Energy: {energy}")
                        
                        # Special highlight for target neighborhoods
                        if any(neighborhood.lower() in ['κολωνάκι', 'παγκράτι', 'kolonaki', 'pangrati']):
                            logger.info(f"🎯 TARGET NEIGHBORHOOD FOUND: {neighborhood}")
            
        except Exception as e:
            logger.error(f"❌ Search processing failed for {search_name}: {e}")
    
    async def extract_property_urls(self, page) -> List[str]:
        """Extract property URLs from search results"""
        try:
            # Enhanced property link detection
            link_selectors = [
                'a[href*="/property/"]',
                'a[href*="/en/property/"]',
                '.property-link',
                '.listing-link', 
                '.property-card a',
                '.result-item a',
                'a[href*="spitogatos.gr/property"]',
                'a[href*="spitogatos.gr/en/property"]'
            ]
            
            property_urls = set()
            
            # Try multiple selector strategies
            for selector in link_selectors:
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
            
            # Also try to find links in the page content
            try:
                page_content = await page.content()
                url_pattern = r'https?://(?:www\.)?spitogatos\.gr/(?:en/)?property/\d+'
                found_urls = re.findall(url_pattern, page_content)
                for url in found_urls:
                    property_urls.add(url)
            except:
                pass
            
            return list(property_urls)[:8]  # Limit to prevent timeout
            
        except Exception as e:
            logger.error(f"❌ URL extraction failed: {e}")
            return []
    
    async def extract_property_with_energy_focus(self, page, property_url: str, search_context: str) -> Optional[Dict]:
        """Extract property data with comprehensive energy class detection"""
        try:
            # Navigate with timeout handling
            response = await page.goto(property_url, wait_until="load", timeout=12000)
            
            if not response or response.status != 200:
                logger.warning(f"⚠️ Failed to load: {property_url}")
                return None
            
            await asyncio.sleep(2)
            
            # Initialize property data
            property_data = {
                'url': property_url,
                'search_context': search_context,
                'extraction_timestamp': datetime.now().isoformat(),
                'data_source': 'spitogatos.gr'
            }
            
            # Extract title and basic info
            try:
                title = await page.title()
                property_data['title'] = title
            except:
                property_data['title'] = "Unknown Title"
            
            # Get page content for comprehensive extraction
            page_text = await page.inner_text('body')
            page_content = await page.content()
            
            # Extract neighborhood (prioritize target neighborhoods)
            neighborhood = await self.extract_neighborhood_comprehensive(page_text, title)
            property_data['neighborhood'] = neighborhood
            
            # Extract listing type
            if 'rent' in search_context.lower() or 'ενοικίαση' in page_text.lower():
                property_data['listing_type'] = 'rent'
            else:
                property_data['listing_type'] = 'sale'
            
            # Extract price
            price = await self.extract_price_comprehensive(page_text)
            if price:
                property_data['price'] = price
                property_data['price_currency'] = 'EUR'
            
            # Extract SQM
            sqm = await self.extract_sqm_comprehensive(page_text)
            if sqm:
                property_data['sqm'] = sqm
            
            # **COMPREHENSIVE ENERGY CLASS EXTRACTION**
            energy_class = await self.extract_energy_class_ultimate(page, page_text, page_content)
            if energy_class:
                property_data['energy_class'] = energy_class
                property_data['has_energy_data'] = True
            else:
                property_data['has_energy_data'] = False
            
            # Calculate derived metrics
            if price and sqm and sqm > 0:
                property_data['price_per_sqm'] = round(price / sqm, 2)
            
            # Extract property type
            property_type = await self.extract_property_type(page_text, title)
            property_data['property_type'] = property_type
            
            # Validate we have meaningful data
            if property_data.get('price') or property_data.get('sqm') or property_data.get('energy_class'):
                return property_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Property extraction failed for {property_url}: {e}")
            return None
    
    async def extract_neighborhood_comprehensive(self, page_text: str, title: str) -> str:
        """Extract neighborhood with focus on target areas"""
        
        # Target neighborhoods (priority)
        target_neighborhoods = {
            'Κολωνάκι': ['κολωνάκι', 'kolonaki', 'κολονάκι'],
            'Παγκράτι': ['παγκράτι', 'pangrati', 'pagrati'],
        }
        
        # Check for target neighborhoods first
        full_text = (page_text + " " + title).lower()
        
        for neighborhood, variants in target_neighborhoods.items():
            for variant in variants:
                if variant in full_text:
                    return neighborhood
        
        # General Athens areas
        athens_areas = {
            'Εξάρχεια': ['εξάρχεια', 'exarchia'],
            'Πλάκα': ['πλάκα', 'plaka'], 
            'Ψυρρή': ['ψυρρή', 'psirri'],
            'Μοναστηράκι': ['μοναστηράκι', 'monastiraki'],
            'Κέντρο': ['κέντρο', 'center', 'centre'],
            'Αθήνα': ['αθήνα', 'athens']
        }
        
        for area, variants in athens_areas.items():
            for variant in variants:
                if variant in full_text:
                    return area
        
        return 'Athens'
    
    async def extract_price_comprehensive(self, page_text: str) -> Optional[float]:
        """Comprehensive price extraction"""
        price_patterns = [
            r'€\s*([\d,\.]+)',
            r'([\d,\.]+)\s*€',
            r'Price[:\s]*€?\s*([\d,\.]+)',
            r'Τιμή[:\s]*€?\s*([\d,\.]+)',
            r'([\d,\.]+)\s*EUR',
            r'([\d,\.]+)\s*euro',
            r'€([\d,\.]+)',
            r'\$([\d,\.]+)',  # Sometimes in USD
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
    
    async def extract_sqm_comprehensive(self, page_text: str) -> Optional[float]:
        """Comprehensive SQM extraction"""
        sqm_patterns = [
            r'(\d+(?:\.\d+)?)\s*m²',
            r'(\d+(?:\.\d+)?)\s*sq\.?\s*m',
            r'(\d+(?:\.\d+)?)\s*τ\.μ',
            r'(\d+(?:\.\d+)?)\s*m2',
            r'Size[:\s]*(\d+(?:\.\d+)?)',
            r'Εμβαδόν[:\s]*(\d+(?:\.\d+)?)',
            r'Area[:\s]*(\d+(?:\.\d+)?)',
            r'(\d+)\s*square\s*meters',
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
        """ULTIMATE comprehensive energy class extraction"""
        try:
            # Strategy 1: Advanced CSS selectors
            energy_selectors = [
                '[class*="energy"]', '[id*="energy"]',
                '[class*="certificate"]', '[id*="certificate"]',
                '.energy-class', '.energy-rating', '.energy-certificate',
                '.energy-efficiency', '.energy-performance',
                'span:has-text("Energy")', 'div:has-text("Energy")',
                'span:has-text("Ενεργειακή")', 'div:has-text("Ενεργειακή")',
                'span:has-text("Certificate")', 'div:has-text("Certificate")',
                '.certificate', '.rating', '.efficiency',
                '[data-testid*="energy"]', '[data-test*="energy"]',
                'dd:has-text("Energy")', 'dt:has-text("Energy")',
                'li:has-text("Energy")', 'p:has-text("Energy")'
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
                                logger.info(f"🔋 Energy class found via selector '{selector}': {energy_class}")
                                return energy_class
                except:
                    continue
            
            # Strategy 2: Comprehensive text patterns (Greek & English)
            energy_patterns = [
                r'ενεργειακή\s+κλάση[:\s]*([A-G][+]?)',
                r'Ενεργειακή\s+κλάση[:\s]*([A-G][+]?)',
                r'ΕΝΕΡΓΕΙΑΚΗ\s+ΚΛΑΣΗ[:\s]*([A-G][+]?)',
                r'energy\s+class[:\s]*([A-G][+]?)',
                r'Energy\s+Class[:\s]*([A-G][+]?)',
                r'ENERGY\s+CLASS[:\s]*([A-G][+]?)',
                r'energy\s+rating[:\s]*([A-G][+]?)',
                r'Energy\s+Rating[:\s]*([A-G][+]?)',
                r'ενεργειακό\s+πιστοποιητικό[:\s]*([A-G][+]?)',
                r'Ενεργειακό\s+πιστοποιητικό[:\s]*([A-G][+]?)',
                r'energy\s+certificate[:\s]*([A-G][+]?)',
                r'Energy\s+Certificate[:\s]*([A-G][+]?)',
                r'κλάση\s+ενέργειας[:\s]*([A-G][+]?)',
                r'κατηγορία\s+ενέργειας[:\s]*([A-G][+]?)',
                r'ενεργειακής\s+απόδοσης[:\s]*([A-G][+]?)',
                r'energy\s+performance[:\s]*([A-G][+]?)',
                r'energy\s+efficiency[:\s]*([A-G][+]?)',
                # Relaxed patterns
                r'ενεργ[^:]*[:\s]*([A-G][+]?)',
                r'energy[^:]*[:\s]*([A-G][+]?)',
                r'certificate[^:]*[:\s]*([A-G][+]?)',
                r'πιστοποιητικό[^:]*[:\s]*([A-G][+]?)',
                # HTML patterns
                r'>([A-G][+]?)</.*?energy',
                r'energy.*?>([A-G][+]?)<',
                r'data-energy["\']?\s*[:=]\s*["\']?([A-G][+]?)',
            ]
            
            full_text = page_content + " " + page_text
            
            for pattern in energy_patterns:
                matches = re.finditer(pattern, full_text, re.IGNORECASE)
                for match in matches:
                    energy_class = match.group(1).upper()
                    if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                        logger.info(f"🔋 Energy class found via pattern: {energy_class}")
                        return energy_class
            
            # Strategy 3: Context-based search
            energy_keywords = [
                'energy', 'ενεργειακή', 'ενεργειακό', 'certificate', 'πιστοποιητικό', 
                'κλάση', 'rating', 'efficiency', 'performance', 'απόδοση'
            ]
            
            for keyword in energy_keywords:
                keyword_positions = []
                text_lower = page_text.lower()
                start = 0
                while True:
                    pos = text_lower.find(keyword.lower(), start)
                    if pos == -1:
                        break
                    keyword_positions.append(pos)
                    start = pos + 1
                
                for pos in keyword_positions:
                    # Look within 100 characters around the keyword
                    context_start = max(0, pos - 50)
                    context_end = min(len(page_text), pos + 50)
                    context = page_text[context_start:context_end]
                    
                    energy_match = re.search(r'([A-G][+]?)', context)
                    if energy_match:
                        energy_class = energy_match.group(1).upper()
                        if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                            logger.info(f"🔋 Energy class found near keyword '{keyword}': {energy_class}")
                            return energy_class
            
            # Strategy 4: Image and attribute analysis
            try:
                # Check for energy-related images
                images = await page.query_selector_all('img')
                for img in images:
                    src = await img.get_attribute('src') or ""
                    alt = await img.get_attribute('alt') or ""
                    title = await img.get_attribute('title') or ""
                    
                    for attr in [src, alt, title]:
                        if any(keyword in attr.lower() for keyword in ['energy', 'ενεργειακή', 'certificate']):
                            energy_match = re.search(r'([A-G][+]?)', attr, re.IGNORECASE)
                            if energy_match:
                                energy_class = energy_match.group(1).upper()
                                if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                                    logger.info(f"🔋 Energy class found in image attribute: {energy_class}")
                                    return energy_class
            except:
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Ultimate energy extraction failed: {e}")
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
    
    async def generate_energy_url_results(self):
        """Generate comprehensive results with energy class focus"""
        try:
            import os
            os.makedirs('outputs', exist_ok=True)
            
            # Analyze energy class data
            with_energy = [p for p in self.properties if p.get('energy_class')]
            with_price = [p for p in self.properties if p.get('price')]
            with_sqm = [p for p in self.properties if p.get('sqm')]
            
            # Target neighborhood analysis
            kolonaki_props = [p for p in self.properties if 'κολωνάκι' in p.get('neighborhood', '').lower()]
            pangrati_props = [p for p in self.properties if 'παγκράτι' in p.get('neighborhood', '').lower()]
            
            # Energy class distribution
            energy_distribution = {}
            for prop in with_energy:
                energy = prop['energy_class']
                energy_distribution[energy] = energy_distribution.get(energy, 0) + 1
            
            # Price analysis
            prices = [p['price'] for p in with_price]
            price_stats = {}
            if prices:
                price_stats = {
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'avg_price': sum(prices) / len(prices)
                }
            
            results = {
                'extraction_metadata': {
                    'session_id': self.session_id,
                    'extraction_timestamp': datetime.now().isoformat(),
                    'extraction_focus': 'energy_class_and_urls',
                    'total_properties': len(self.properties),
                    'properties_with_energy_class': len(with_energy),
                    'properties_with_price': len(with_price),
                    'properties_with_sqm': len(with_sqm),
                    'kolonaki_properties': len(kolonaki_props),
                    'pangrati_properties': len(pangrati_props),
                    'energy_class_success_rate': f"{len(with_energy)}/{len(self.properties)} ({100*len(with_energy)/max(1,len(self.properties)):.1f}%)"
                },
                'energy_analysis': {
                    'energy_class_distribution': energy_distribution,
                    'properties_by_neighborhood': {
                        'Κολωνάκι': len(kolonaki_props),
                        'Παγκράτι': len(pangrati_props),
                        'Other': len(self.properties) - len(kolonaki_props) - len(pangrati_props)
                    }
                },
                'price_analysis': price_stats,
                'properties': self.properties
            }
            
            # Save JSON
            json_file = f'outputs/spitogatos_energy_urls_{self.session_id}.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Save CSV with all required fields
            csv_file = f'outputs/spitogatos_energy_urls_{self.session_id}.csv'
            if self.properties:
                fieldnames = [
                    'url', 'neighborhood', 'title', 'listing_type', 'property_type',
                    'price', 'price_currency', 'sqm', 'price_per_sqm', 
                    'energy_class', 'has_energy_data', 'search_context', 
                    'data_source', 'extraction_timestamp'
                ]
                
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for prop in self.properties:
                        writer.writerow({key: prop.get(key, '') for key in fieldnames})
            
            # Generate comprehensive report
            logger.info("\\n" + "="*90)
            logger.info("🔋 SPITOGATOS ENERGY CLASS & URL EXTRACTION - FINAL REPORT")
            logger.info("="*90)
            logger.info(f"🏠 Total Properties Extracted: {len(self.properties)}")
            logger.info(f"🔋 Properties WITH Energy Class: {len(with_energy)} ({100*len(with_energy)/max(1,len(self.properties)):.1f}%)")
            logger.info(f"💰 Properties with Price: {len(with_price)}")
            logger.info(f"📐 Properties with SQM: {len(with_sqm)}")
            logger.info(f"🎯 Target Neighborhoods Found:")
            logger.info(f"   🏛️ Κολωνάκι (Kolonaki): {len(kolonaki_props)} properties")
            logger.info(f"   🏛️ Παγκράτι (Pangrati): {len(pangrati_props)} properties")
            
            if energy_distribution:
                logger.info(f"\\n🔋 ENERGY CLASS DISTRIBUTION:")
                for energy_class, count in sorted(energy_distribution.items()):
                    logger.info(f"   Class {energy_class}: {count} properties")
            
            if price_stats:
                logger.info(f"\\n💰 PRICE ANALYSIS:")
                logger.info(f"   Min: €{price_stats['min_price']:,.0f}")
                logger.info(f"   Max: €{price_stats['max_price']:,.0f}")
                logger.info(f"   Avg: €{price_stats['avg_price']:,.0f}")
            
            if self.properties:
                logger.info(f"\\n🏠 SAMPLE PROPERTIES WITH COMPLETE DATA:")
                for i, prop in enumerate(self.properties[:5], 1):
                    neighborhood = prop.get('neighborhood', 'Unknown')
                    price = f"€{prop.get('price', 0):,.0f}" if prop.get('price') else 'N/A'
                    sqm = f"{prop.get('sqm', 0)}m²" if prop.get('sqm') else 'N/A'
                    energy = prop.get('energy_class', 'No energy data')
                    logger.info(f"   {i}. {neighborhood} | {price} | {sqm} | Energy: {energy}")
                    logger.info(f"      URL: {prop['url']}")
            
            logger.info(f"\\n💾 COMPLETE RESULTS SAVED:")
            logger.info(f"   📄 JSON: {json_file}")
            logger.info(f"   📊 CSV: {csv_file}")
            logger.info("="*90)
            
            # Special summary for energy class success
            if with_energy:
                logger.info(f"\\n🎉 SUCCESS: Found {len(with_energy)} properties with energy class data!")
                logger.info("🔋 Energy classes found: " + ", ".join(sorted(energy_distribution.keys())))
            else:
                logger.info("\\n⚠️ No energy class data found in extracted properties")
                logger.info("💡 Energy class information may not be publicly available or require authentication")
            
        except Exception as e:
            logger.error(f"❌ Results generation failed: {e}")

async def main():
    scraper = SpitogatosEnergyURLScraper()
    await scraper.run_energy_url_extraction()

if __name__ == "__main__":
    asyncio.run(main())