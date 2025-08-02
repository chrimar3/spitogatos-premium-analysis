#!/usr/bin/env python3
"""
SPITOGATOS KOLONAKI & PANGRATI FOCUSED SCRAPER
Fast, targeted extraction for energy class and URL data
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

class KolonakiPangratiScraper:
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.properties = []
        
        # Specific search URLs for target neighborhoods
        self.search_urls = {
            'kolonaki_sale': 'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/kolonaki-athens-center-athens',
            'kolonaki_rent': 'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/kolonaki-athens-center-athens',
            'pangrati_sale': 'https://www.spitogatos.gr/search/sale/apartment,flat,studio,duplex,house,villa,bungalow/pangrati-athens-center-athens',
            'pangrati_rent': 'https://www.spitogatos.gr/search/rent/apartment,flat,studio,duplex,house,villa,bungalow/pangrati-athens-center-athens',
        }
        
        self.target_properties = 20
    
    async def run_targeted_extraction(self):
        """Run targeted extraction for Kolonaki and Pangrati"""
        logger.info("🎯 SPITOGATOS KOLONAKI & PANGRATI FOCUSED SCRAPER")
        logger.info("🔋 Mission: Extract properties with energy class and URLs")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            try:
                page = await context.new_page()
                
                # Process each neighborhood search
                for search_name, search_url in self.search_urls.items():
                    if len(self.properties) >= self.target_properties:
                        break
                    
                    logger.info(f"🔍 Processing: {search_name}")
                    await self.process_search_results(page, search_url, search_name)
                
                # Generate results
                await self.generate_results()
                
            except Exception as e:
                logger.error(f"❌ Extraction failed: {e}")
            finally:
                await browser.close()
    
    async def process_search_results(self, page, search_url: str, search_name: str):
        """Process search results for a specific neighborhood"""
        try:
            logger.info(f"🌐 Accessing: {search_url}")
            
            response = await page.goto(search_url, wait_until="load", timeout=20000)
            
            if response and response.status == 200:
                await asyncio.sleep(3)
                
                # Find property links
                property_urls = await self.extract_property_urls(page)
                logger.info(f"📋 Found {len(property_urls)} property URLs for {search_name}")
                
                # Process each property (limit to prevent timeout)
                for i, property_url in enumerate(property_urls[:5]):  # Limit to 5 per search
                    if len(self.properties) >= self.target_properties:
                        break
                    
                    logger.info(f"🏠 Processing {i+1}/5: {property_url}")
                    
                    property_data = await self.extract_property_data_fast(page, property_url, search_name)
                    if property_data:
                        self.properties.append(property_data)
                        logger.info(f"✅ Extracted: {property_data.get('neighborhood', 'Unknown')} - {property_data.get('price', 'No price')} - {property_data.get('energy_class', 'No energy')}")
            
        except Exception as e:
            logger.error(f"❌ Search processing failed for {search_name}: {e}")
    
    async def extract_property_urls(self, page) -> List[str]:
        """Extract property URLs from search results"""
        try:
            # Common property link selectors
            link_selectors = [
                'a[href*="/property/"]',
                'a[href*="/en/property/"]', 
                '.property-link',
                '.listing-link',
                '.property-card a',
                '.result-item a'
            ]
            
            property_urls = set()
            
            for selector in link_selectors:
                try:
                    links = await page.query_selector_all(selector)
                    for link in links:
                        href = await link.get_attribute('href')
                        if href and '/property/' in href:
                            # Make sure it's a full URL
                            if href.startswith('/'):
                                href = 'https://www.spitogatos.gr' + href
                            property_urls.add(href)
                except:
                    continue
            
            return list(property_urls)[:10]  # Limit to 10 URLs per search
            
        except Exception as e:
            logger.error(f"❌ URL extraction failed: {e}")
            return []
    
    async def extract_property_data_fast(self, page, property_url: str, search_context: str) -> Optional[Dict]:
        """Fast property data extraction with energy class focus"""
        try:
            # Quick navigation with shorter timeout
            response = await page.goto(property_url, wait_until="load", timeout=15000)
            
            if not response or response.status != 200:
                return None
            
            await asyncio.sleep(2)  # Shorter wait
            
            # Extract basic data quickly
            property_data = {
                'url': property_url,
                'search_context': search_context,
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            # Extract title
            try:
                title = await page.title()
                property_data['title'] = title
            except:
                property_data['title'] = "Unknown"
            
            # Determine neighborhood from search context
            if 'kolonaki' in search_context.lower():
                property_data['neighborhood'] = 'Κολωνάκι'
            elif 'pangrati' in search_context.lower():
                property_data['neighborhood'] = 'Παγκράτι'
            else:
                property_data['neighborhood'] = 'Athens Center'
            
            # Determine listing type
            if 'rent' in search_context.lower():
                property_data['listing_type'] = 'rent'
            else:
                property_data['listing_type'] = 'sale'
            
            # Get page content for extraction
            page_text = await page.inner_text('body')
            
            # Extract price
            price = await self.extract_price_fast(page_text)
            if price:
                property_data['price'] = price
                property_data['price_currency'] = 'EUR'
            
            # Extract SQM
            sqm = await self.extract_sqm_fast(page_text)
            if sqm:
                property_data['sqm'] = sqm
            
            # Extract energy class - COMPREHENSIVE
            energy_class = await self.extract_energy_class_comprehensive(page, page_text)
            if energy_class:
                property_data['energy_class'] = energy_class
            
            # Calculate price per sqm
            if price and sqm and sqm > 0:
                property_data['price_per_sqm'] = round(price / sqm, 2)
            
            # Validate we have essential data
            if property_data.get('price') or property_data.get('sqm'):
                return property_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Fast extraction failed for {property_url}: {e}")
            return None
    
    async def extract_price_fast(self, page_text: str) -> Optional[float]:
        """Fast price extraction"""
        price_patterns = [
            r'€\s*([\d,]+)',
            r'([\d,]+)\s*€',
            r'Price:\s*€?\s*([\d,]+)',
            r'Τιμή:\s*€?\s*([\d,]+)',
            r'([\d,]+)\s*EUR'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                try:
                    price_str = match.group(1).replace(',', '')
                    price = float(price_str)
                    if 1000 <= price <= 10000000:  # Reasonable price range
                        return price
                except ValueError:
                    continue
        
        return None
    
    async def extract_sqm_fast(self, page_text: str) -> Optional[float]:
        """Fast SQM extraction"""
        sqm_patterns = [
            r'(\d+(?:\.\d+)?)\s*m²',
            r'(\d+(?:\.\d+)?)\s*sq\.?\s*m',
            r'(\d+(?:\.\d+)?)\s*τ\.μ',
            r'Size:\s*(\d+(?:\.\d+)?)',
            r'Εμβαδόν:\s*(\d+(?:\.\d+)?)'
        ]
        
        for pattern in sqm_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                try:
                    sqm = float(match.group(1))
                    if 10 <= sqm <= 1000:  # Reasonable sqm range
                        return sqm
                except ValueError:
                    continue
        
        return None
    
    async def extract_energy_class_comprehensive(self, page, page_text: str) -> Optional[str]:
        """Comprehensive energy class extraction"""
        try:
            # Strategy 1: CSS selectors
            energy_selectors = [
                '[class*="energy"]', '[id*="energy"]',
                '.energy-class', '.energy-rating', '.energy-certificate',
                'span:has-text("Energy")', 'div:has-text("Energy")',
                'span:has-text("Ενεργειακή")', 'div:has-text("Ενεργειακή")',
                '.certificate', '.rating'
            ]
            
            for selector in energy_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        energy_text = await element.inner_text()
                        energy_match = re.search(r'([A-G][+]?)', energy_text, re.IGNORECASE)
                        if energy_match:
                            energy_class = energy_match.group(1).upper()
                            if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                                logger.info(f"🔋 Energy class found via selector: {energy_class}")
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
                r'energy[:\s]*([A-G][+]?)',
                r'ενεργ[^:]*[:\s]*([A-G][+]?)'
            ]
            
            for pattern in energy_patterns:
                matches = re.finditer(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    energy_class = match.group(1).upper()
                    if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                        logger.info(f"🔋 Energy class found via pattern: {energy_class}")
                        return energy_class
            
            # Strategy 3: Look for standalone energy classes near keywords
            energy_keywords = ['energy', 'ενεργειακή', 'certificate', 'πιστοποιητικό', 'rating', 'κλάση']
            for keyword in energy_keywords:
                if keyword.lower() in page_text.lower():
                    # Look for energy classes within 100 characters of the keyword
                    keyword_pos = page_text.lower().find(keyword.lower())
                    if keyword_pos != -1:
                        context = page_text[max(0, keyword_pos-50):keyword_pos+50]
                        energy_match = re.search(r'([A-G][+]?)', context)
                        if energy_match:
                            energy_class = energy_match.group(1).upper()
                            if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                                logger.info(f"🔋 Energy class found near keyword '{keyword}': {energy_class}")
                                return energy_class
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Energy class extraction failed: {e}")
            return None
    
    async def generate_results(self):
        """Generate comprehensive results"""
        try:
            import os
            os.makedirs('outputs', exist_ok=True)
            
            # Analyze results
            with_energy = [p for p in self.properties if p.get('energy_class')]
            with_price = [p for p in self.properties if p.get('price')]
            with_sqm = [p for p in self.properties if p.get('sqm')]
            
            kolonaki_props = [p for p in self.properties if 'κολωνάκι' in p.get('neighborhood', '').lower()]
            pangrati_props = [p for p in self.properties if 'παγκράτι' in p.get('neighborhood', '').lower()]
            
            results = {
                'extraction_metadata': {
                    'session_id': self.session_id,
                    'extraction_timestamp': datetime.now().isoformat(),
                    'target_neighborhoods': ['Κολωνάκι', 'Παγκράτι'],
                    'total_properties': len(self.properties),
                    'properties_with_energy_class': len(with_energy),
                    'properties_with_price': len(with_price),
                    'properties_with_sqm': len(with_sqm),
                    'kolonaki_properties': len(kolonaki_props),
                    'pangrati_properties': len(pangrati_props)
                },
                'properties': self.properties
            }
            
            # Save JSON
            json_file = f'outputs/spitogatos_kolonaki_pangrati_{self.session_id}.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Save CSV
            csv_file = f'outputs/spitogatos_kolonaki_pangrati_{self.session_id}.csv'
            if self.properties:
                fieldnames = [
                    'url', 'neighborhood', 'title', 'listing_type', 'price', 'price_currency',
                    'sqm', 'price_per_sqm', 'energy_class', 'search_context', 'extraction_timestamp'
                ]
                
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for prop in self.properties:
                        writer.writerow({key: prop.get(key, '') for key in fieldnames})
            
            # Generate report
            logger.info("\\n" + "="*80)
            logger.info("🎯 KOLONAKI & PANGRATI EXTRACTION - FINAL REPORT")
            logger.info("="*80)
            logger.info(f"🏠 Total Properties: {len(self.properties)}")
            logger.info(f"🔋 With Energy Class: {len(with_energy)}")
            logger.info(f"💰 With Price: {len(with_price)}")
            logger.info(f"📐 With SQM: {len(with_sqm)}")
            logger.info(f"🏛️ Κολωνάκι: {len(kolonaki_props)}")
            logger.info(f"🏛️ Παγκράτι: {len(pangrati_props)}")
            
            if with_energy:
                logger.info(f"\\n🔋 ENERGY CLASS DISTRIBUTION:")
                energy_dist = {}
                for prop in with_energy:
                    energy = prop['energy_class']
                    energy_dist[energy] = energy_dist.get(energy, 0) + 1
                
                for energy, count in sorted(energy_dist.items()):
                    logger.info(f"   {energy}: {count} properties")
            
            if self.properties:
                logger.info(f"\\n🏠 SAMPLE PROPERTIES:")
                for i, prop in enumerate(self.properties[:5], 1):
                    neighborhood = prop.get('neighborhood', 'Unknown')
                    price = f"€{prop.get('price', 'N/A'):,}" if prop.get('price') else 'N/A'
                    sqm = f"{prop.get('sqm', 'N/A')}m²" if prop.get('sqm') else 'N/A'
                    energy = prop.get('energy_class', 'N/A')
                    logger.info(f"   {i}. {neighborhood} | {price} | {sqm} | Energy: {energy}")
                    logger.info(f"      URL: {prop['url']}")
            
            logger.info(f"\\n💾 Results saved:")
            logger.info(f"   📄 JSON: {json_file}")
            logger.info(f"   📊 CSV: {csv_file}")
            logger.info("="*80)
            
        except Exception as e:
            logger.error(f"❌ Results generation failed: {e}")

async def main():
    scraper = KolonakiPangratiScraper()
    await scraper.run_targeted_extraction()

if __name__ == "__main__":
    asyncio.run(main())