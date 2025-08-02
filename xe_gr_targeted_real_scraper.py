#!/usr/bin/env python3
"""
XE.GR TARGETED REAL PROPERTY SCRAPER
Fast targeted approach to find ONLY authentic individual property listings
"""

import asyncio
import json
import logging
import re
import csv
import random
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XETargetedRealScraper:
    """Fast targeted scraper for real individual property listings"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.real_properties = []
        self.template_patterns_detected = set()
        
        # Focus on finding REAL INDIVIDUAL property listings
        # Start with property detail page patterns that might bypass category pages
        self.direct_property_patterns = [
            "https://xe.gr/property/apartment-for-rent/{id}",
            "https://xe.gr/property/apartment-for-sale/{id}",
            "https://www.xe.gr/property/apartment-for-rent/{id}",
            "https://www.xe.gr/property/apartment-for-sale/{id}",
            "https://xe.gr/listing/{id}",
            "https://www.xe.gr/listing/{id}",
            "https://xe.gr/ad/{id}",
            "https://www.xe.gr/ad/{id}"
        ]
        
        # Alternative: Use search with specific queries for individual listings
        self.search_queries = [
            "κολωνάκι διαμέρισμα",
            "παγκράτι διαμέρισμα", 
            "kolonaki apartment",
            "pangrati apartment"
        ]
        
        self.target_real_properties = 5
    
    async def run_targeted_real_extraction(self):
        """Fast targeted approach to find real properties"""
        logger.info("🎯 XE.GR TARGETED REAL PROPERTY EXTRACTION")
        logger.info("⚡ Strategy: Find individual listings, avoid category/template pages")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            try:
                page = await context.new_page()
                
                # Strategy 1: Direct search approach
                logger.info("🔍 STRATEGY 1: Direct search for individual listings")
                await self.search_individual_listings(page)
                
                # Strategy 2: Try alternative URL patterns
                if len(self.real_properties) < self.target_real_properties:
                    logger.info("🔍 STRATEGY 2: Testing alternative direct property URLs")
                    await self.test_direct_property_urls(page)
                
                # Strategy 3: Analyze what makes URLs authentic vs template
                logger.info("🔍 STRATEGY 3: URL pattern analysis")
                await self.analyze_url_authenticity()
                
                # Generate results
                await self.generate_targeted_results()
                
            except Exception as e:
                logger.error(f"❌ Targeted extraction failed: {e}")
            finally:
                await browser.close()
    
    async def search_individual_listings(self, page):
        """Search for individual property listings using search functionality"""
        try:
            # Start from search page
            logger.info("🔍 Accessing XE.gr search page...")
            response = await page.goto("https://xe.gr/search", wait_until="load", timeout=30000)
            
            if response and response.status == 200:
                await asyncio.sleep(3)
                
                # Look for search form
                try:
                    # Try to find and use search input
                    search_input = await page.query_selector('input[type="search"], input[name="search"], input[placeholder*="search"], input[placeholder*="αναζήτηση"]')
                    
                    if search_input:
                        for query in self.search_queries[:2]:  # Test first 2 queries
                            logger.info(f"🔍 Searching for: {query}")
                            
                            await search_input.fill(query)
                            await asyncio.sleep(1)
                            
                            # Try to submit search
                            await page.keyboard.press('Enter')
                            await asyncio.sleep(5)
                            
                            # Look for individual property links in results
                            await self.extract_individual_property_links(page)
                            
                            if len(self.real_properties) >= self.target_real_properties:
                                break
                    
                    else:
                        logger.info("⚠️ No search input found, trying alternative approach")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Search form interaction failed: {e}")
            
        except Exception as e:
            logger.error(f"❌ Search individual listings failed: {e}")
    
    async def extract_individual_property_links(self, page):
        """Extract links that appear to be individual property listings"""
        try:
            # Get all links on the page
            links = await page.query_selector_all('a[href]')
            
            for link in links:
                href = await link.get_attribute('href')
                if href:
                    # Look for patterns that suggest individual property listings
                    if self.is_individual_property_url(href):
                        text = await link.inner_text()
                        logger.info(f"🏠 Found potential individual property: {href}")
                        
                        # Test this URL for authenticity
                        is_real = await self.test_property_authenticity(page, href)
                        if is_real:
                            logger.info(f"✅ REAL PROPERTY CONFIRMED: {href}")
                            if len(self.real_properties) >= self.target_real_properties:
                                break
                
        except Exception as e:
            logger.error(f"❌ Extract individual property links failed: {e}")
    
    def is_individual_property_url(self, url: str) -> bool:
        """Check if URL pattern suggests individual property vs category/template"""
        # Patterns that suggest individual properties
        individual_indicators = [
            r'/property/\d+',  # Contains property ID
            r'/listing/\d+',   # Contains listing ID
            r'/ad/\d+',        # Contains ad ID
            r'-\d{6,}',        # Contains long ID numbers
            r'apartment-\d+',  # Specific apartment ID
            r'house-\d+',      # Specific house ID
        ]
        
        # Patterns that suggest category/template pages
        template_indicators = [
            r'/d/[^/]*/[^/]*/athens-',  # Our discovered template pattern
            r'enoikiaseis-katoikion',    # Category pages
            r'poliseis-katoikion',       # Category pages
            r'search',                   # Search pages
            r'category',                 # Category pages
        ]
        
        # Check for individual indicators
        for pattern in individual_indicators:
            if re.search(pattern, url, re.IGNORECASE):
                # But make sure it's not also a template
                for template_pattern in template_indicators:
                    if re.search(template_pattern, url, re.IGNORECASE):
                        return False
                return True
        
        return False
    
    async def test_property_authenticity(self, page, url: str) -> bool:
        """Test if a property URL contains authentic vs template data"""
        try:
            logger.info(f"🧪 Testing authenticity: {url}")
            
            # Navigate to the property page
            response = await page.goto(url, wait_until="load", timeout=15000)
            
            if response and response.status == 200:
                await asyncio.sleep(2)
                
                content = await page.content()
                page_text = await page.inner_text('body')
                
                # Check for authenticity indicators
                authenticity_score = 0
                
                # 1. Unique content hash (vs template duplicates)
                content_hash = hashlib.md5(page_text.encode()).hexdigest()
                if content_hash not in self.template_patterns_detected:
                    authenticity_score += 1
                    self.template_patterns_detected.add(content_hash)
                
                # 2. Contact information (real listings have contact info)
                contact_patterns = [
                    r'τηλέφωνο[:\s]*\d+',
                    r'κινητό[:\s]*\d+', 
                    r'phone[:\s]*\d+',
                    r'mobile[:\s]*\d+',
                    r'email',
                    r'@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                    r'\d{10,}',  # Phone number patterns
                ]
                
                for pattern in contact_patterns:
                    if re.search(pattern, page_text, re.IGNORECASE):
                        authenticity_score += 1
                        break
                
                # 3. Detailed description (vs generic template text)
                if len(page_text) > 1000 and not self.is_template_text(page_text):
                    authenticity_score += 1
                
                # 4. Multiple photos/images (real listings have photos)
                images = await page.query_selector_all('img[src]')
                if len(images) >= 3:
                    authenticity_score += 1
                
                # 5. Specific address details (not just neighborhood)
                address_patterns = [
                    r'\d+.*οδός',
                    r'\d+.*street',
                    r'όροφος',
                    r'floor',
                    r'τετραγωνικά',
                    r'square meters'
                ]
                
                for pattern in address_patterns:
                    if re.search(pattern, page_text, re.IGNORECASE):
                        authenticity_score += 1
                        break
                
                logger.info(f"🔍 Authenticity score: {authenticity_score}/5")
                
                # Require high authenticity score
                if authenticity_score >= 3:
                    property_data = await self.extract_real_property_data(page, url)
                    if property_data:
                        self.real_properties.append(property_data)
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Authenticity test failed for {url}: {e}")
            return False
    
    def is_template_text(self, text: str) -> bool:
        """Check if text appears to be template/generic vs real property description"""
        template_phrases = [
            "ς και ταυτοποίησης μέσω σάρωσης συσκευών",  # Known template phrase
            "generic property description",
            "template text",
            "sample description"
        ]
        
        for phrase in template_phrases:
            if phrase in text:
                return True
        return False
    
    async def extract_real_property_data(self, page, url: str) -> Optional[Dict]:
        """Extract data from confirmed real property"""
        try:
            page_text = await page.inner_text('body')
            title = await page.title()
            
            property_data = {
                'url': url,
                'title': title,
                'extraction_method': 'targeted_real_extraction',
                'extraction_timestamp': datetime.now().isoformat(),
                'verified_as_real': True
            }
            
            # Extract price
            price_patterns = [
                r'(\\d{1,3}(?:\\.\\d{3})+)\\s*€',
                r'€\\s*(\\d{1,3}(?:\\.\\d{3})+)',
                r'τιμή[:\\s]*(\\d{1,3}(?:\\.\\d{3})+)',
                r'price[:\\s]*(\\d{1,3}(?:\\.\\d{3})+)'
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
            
            # Extract SQM
            sqm_patterns = [
                r'(\\d+(?:[.,]\\d+)?)\\s*τ\\.?μ\\.?',
                r'(\\d+(?:[.,]\\d+)?)\\s*m²',
                r'(\\d+(?:[.,]\\d+)?)\\s*sq\\.?m'
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
            
            # Extract neighborhood
            for neighborhood in ["Κολωνάκι", "Παγκράτι", "kolonaki", "pangrati"]:
                if neighborhood.lower() in page_text.lower():
                    property_data['neighborhood'] = neighborhood
                    break
            
            logger.info(f"✅ Real property data extracted: {property_data.get('price', 'No price')} | {property_data.get('sqm', 'No SQM')}m²")
            
            return property_data
            
        except Exception as e:
            logger.error(f"❌ Real property data extraction failed: {e}")
            return None
    
    async def test_direct_property_urls(self, page):
        """Test direct property URL patterns"""
        try:
            logger.info("🧪 Testing direct property URL patterns...")
            
            # Test a range of property IDs
            test_ids = range(100000, 200000, 10000)  # Sample range
            
            for property_id in test_ids:
                if len(self.real_properties) >= self.target_real_properties:
                    break
                
                for pattern in self.direct_property_patterns[:4]:  # Test first 4 patterns
                    url = pattern.format(id=property_id)
                    
                    try:
                        response = await page.goto(url, wait_until="load", timeout=10000)
                        
                        if response and response.status == 200:
                            logger.info(f"✅ Found working URL pattern: {url}")
                            
                            is_real = await self.test_property_authenticity(page, url)
                            if is_real:
                                if len(self.real_properties) >= self.target_real_properties:
                                    return
                        
                    except Exception as e:
                        logger.debug(f"❌ URL failed: {url}")
                
                await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"❌ Direct URL testing failed: {e}")
    
    async def analyze_url_authenticity(self):
        """Analyze URL patterns to distinguish real vs template URLs"""
        logger.info("🔍 Analyzing URL authenticity patterns...")
        
        # Report findings
        logger.info(f"📊 Template patterns detected: {len(self.template_patterns_detected)}")
        logger.info(f"✅ Real properties found: {len(self.real_properties)}")
        
        if self.real_properties:
            logger.info("🏠 Real property URLs found:")
            for prop in self.real_properties:
                logger.info(f"   ✅ {prop['url']}")
    
    async def generate_targeted_results(self):
        """Generate results from targeted real extraction"""
        try:
            # Create outputs directory if it doesn't exist
            import os
            os.makedirs('outputs', exist_ok=True)
            
            # Save results
            results = {
                'extraction_metadata': {
                    'session_id': self.session_id,
                    'extraction_timestamp': datetime.now().isoformat(),
                    'method': 'targeted_real_property_extraction',
                    'real_properties_found': len(self.real_properties),
                    'template_patterns_detected': len(self.template_patterns_detected)
                },
                'real_properties': self.real_properties
            }
            
            json_file = f'outputs/xe_gr_targeted_real_{self.session_id}.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Generate report
            logger.info("\n" + "="*80)
            logger.info("🎯 XE.GR TARGETED REAL PROPERTY EXTRACTION - FINAL REPORT")
            logger.info("="*80)
            logger.info(f"✅ REAL Properties Found: {len(self.real_properties)}")
            logger.info(f"🚫 Template Patterns Detected: {len(self.template_patterns_detected)}")
            
            if self.real_properties:
                logger.info(f"\n🏠 VERIFIED REAL PROPERTIES:")
                for i, prop in enumerate(self.real_properties, 1):
                    price = f"€{prop.get('price', 'N/A')}"
                    sqm = f"{prop.get('sqm', 'N/A')}m²"
                    neighborhood = prop.get('neighborhood', 'N/A')
                    logger.info(f"   {i}. {neighborhood} | {price} | {sqm}")
                    logger.info(f"      {prop['url']}")
            else:
                logger.info("❌ NO REAL INDIVIDUAL PROPERTIES FOUND")
                logger.info("💡 All discovered properties appear to be category/template pages")
            
            logger.info(f"\n💾 Results saved: {json_file}")
            logger.info("="*80)
            
        except Exception as e:
            logger.error(f"❌ Results generation failed: {e}")

async def main():
    """Run targeted real property extraction"""
    scraper = XETargetedRealScraper()
    await scraper.run_targeted_real_extraction()

if __name__ == "__main__":
    asyncio.run(main())