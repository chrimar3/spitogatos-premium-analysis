#!/usr/bin/env python3
"""
Advanced Property Extraction Debugger
Analyzes real website structure to understand how to extract property data
"""

import asyncio
import logging
import json
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PropertyExtractionDebugger:
    """Professional property extraction analysis"""
    
    def __init__(self):
        self.discovered_patterns = []
        self.extraction_strategies = []
    
    async def analyze_website_structure(self):
        """Comprehensive analysis of Spitogatos structure"""
        
        print("🔬 PROPERTY EXTRACTION ANALYSIS")
        print("=" * 60)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Visible for analysis
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale='el-GR',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            try:
                # Strategy 1: Main page analysis
                print("\n📍 1. MAIN PAGE ANALYSIS")
                print("-" * 40)
                
                await page.goto("https://www.spitogatos.gr/", wait_until='domcontentloaded')
                await asyncio.sleep(3)
                
                print(f"✅ Main page loaded: {await page.title()}")
                
                # Look for search functionality
                search_elements = await page.query_selector_all('input[type="search"], input[placeholder*="search"], input[name*="location"]')
                print(f"🔍 Found {len(search_elements)} search elements")
                
                # Strategy 2: Try direct property URLs
                print("\n📍 2. DIRECT PROPERTY URL ANALYSIS")
                print("-" * 40)
                
                # Try common property URL patterns
                test_urls = [
                    "https://www.spitogatos.gr/property/",
                    "https://www.spitogatos.gr/search/sale/apartment/",
                    "https://www.spitogatos.gr/en/search/sale/apartment/",
                    "https://www.spitogatos.gr/listings/",
                    "https://www.spitogatos.gr/properties/",
                    "https://www.spitogatos.gr/search/apartments-for-sale/athens/",
                    "https://www.spitogatos.gr/search/sale/apartment/attica/athens/",
                ]
                
                successful_urls = []
                
                for url in test_urls:
                    try:
                        print(f"🧪 Testing: {url}")
                        response = await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                        await asyncio.sleep(2)
                        
                        title = await page.title()
                        
                        if response and response.status == 200:
                            print(f"  ✅ SUCCESS: {title}")
                            successful_urls.append((url, title))
                            
                            # Quick content analysis
                            content = await page.content()
                            if any(keyword in content.lower() for keyword in ['apartment', 'property', 'listing', 'διαμέρισμα']):
                                print(f"  🏠 Contains property-related content")
                            
                        else:
                            print(f"  ❌ Failed: Status {response.status if response else 'None'}")
                            
                    except Exception as e:
                        print(f"  ⚠️ Error: {e}")
                
                # Strategy 3: Detailed analysis of successful pages
                if successful_urls:
                    print(f"\n📍 3. DETAILED CONTENT ANALYSIS")
                    print("-" * 40)
                    
                    for url, title in successful_urls[:2]:  # Analyze first 2 successful URLs
                        print(f"\n🔍 Analyzing: {url}")
                        
                        await page.goto(url, wait_until='domcontentloaded')
                        await asyncio.sleep(5)  # Wait for dynamic content
                        
                        # Execute JavaScript to wait for any dynamic loading
                        await page.evaluate("""
                            new Promise(resolve => {
                                setTimeout(resolve, 3000);
                            });
                        """)
                        
                        await self._analyze_page_structure(page)
                
                # Strategy 4: Use search functionality if found
                print(f"\n📍 4. SEARCH FUNCTIONALITY TEST")
                print("-" * 40)
                
                await page.goto("https://www.spitogatos.gr/", wait_until='domcontentloaded')
                await asyncio.sleep(3)
                
                # Try to find and use search
                search_input = await page.query_selector('input[type="search"], input[placeholder*="περιοχή"], input[name*="location"]')
                
                if search_input:
                    print("🔍 Found search input, testing search...")
                    await search_input.fill("Κολωνάκι")  # Greek for Kolonaki
                    await asyncio.sleep(1)
                    
                    # Look for search button or submit
                    search_button = await page.query_selector('button[type="submit"], .search-button, [class*="search"]')
                    if search_button:
                        await search_button.click()
                        await asyncio.sleep(5)
                        
                        print(f"🎯 Search results: {await page.title()}")
                        await self._analyze_page_structure(page)
                
                # Keep browser open for manual inspection
                print(f"\n📍 5. MANUAL INSPECTION")
                print("-" * 40)
                print("🔍 Browser staying open for manual inspection...")
                print("   Check the page manually for property listings")
                print("   Look for:")
                print("   - Property cards/containers")  
                print("   - Price elements")
                print("   - Property links")
                print("   - Area/sqm information")
                
                await asyncio.sleep(30)  # 30 seconds for manual inspection
                
            except Exception as e:
                print(f"❌ Error in analysis: {e}")
                import traceback
                traceback.print_exc()
            
            finally:
                await browser.close()
    
    async def _analyze_page_structure(self, page):
        """Detailed page structure analysis"""
        
        try:
            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # 1. Look for common property-related elements
            print("   🏗️ Structure Analysis:")
            
            # Check for data attributes that might indicate properties
            data_attributes = []
            for element in soup.find_all(attrs={"data-testid": True}):
                data_attributes.append(element.get('data-testid'))
            
            if data_attributes:
                unique_attrs = list(set(data_attributes))[:10]
                print(f"   📊 Data attributes: {unique_attrs}")
            
            # Look for price indicators
            price_elements = soup.find_all(string=re.compile(r'€|euro|\d{1,3}[.,]\d{3}', re.I))
            if price_elements:
                print(f"   💰 Found {len(price_elements)} price-like elements")
                # Show first few examples
                for i, price in enumerate(price_elements[:3]):
                    print(f"     {i+1}. {price.strip()[:50]}")
            
            # Look for area/sqm indicators
            area_elements = soup.find_all(string=re.compile(r'\d+\s*(m²|τ\.μ\.|sqm)', re.I))
            if area_elements:
                print(f"   📐 Found {len(area_elements)} area-like elements")
                for i, area in enumerate(area_elements[:3]):
                    print(f"     {i+1}. {area.strip()}")
            
            # Look for links that might be property links
            property_links = soup.find_all('a', href=re.compile(r'property|listing|apartment|διαμέρισμα', re.I))
            if property_links:
                print(f"   🔗 Found {len(property_links)} property-like links")
                for i, link in enumerate(property_links[:3]):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)[:50]
                    print(f"     {i+1}. {href} - {text}")
            
            # 2. JavaScript execution to find dynamic content
            print("   🔧 Dynamic Content Analysis:")
            
            # Check if there are any loading indicators
            loading_elements = await page.query_selector_all('[class*="loading"], [class*="spinner"], [id*="loading"]')
            print(f"   ⏳ Loading indicators: {len(loading_elements)}")
            
            # Check for React/Vue components
            react_elements = await page.query_selector_all('[data-reactroot], [id^="app"], [class*="vue"]')
            print(f"   ⚛️ JS Framework elements: {len(react_elements)}")
            
            # Look for any containers that might hold properties
            containers = await page.query_selector_all('div[class*="list"], div[class*="grid"], div[class*="result"], section, article')
            print(f"   📦 Potential containers: {len(containers)}")
            
            # 3. Extract actual visible text for pattern recognition
            visible_text = await page.evaluate("""
                () => {
                    const walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        null,
                        false
                    );
                    
                    let text = '';
                    let node;
                    
                    while (node = walker.nextNode()) {
                        if (node.parentElement.offsetParent !== null) {
                            text += node.textContent + ' ';
                        }
                    }
                    
                    return text;
                }
            """)
            
            # Look for property-related patterns in visible text
            property_patterns = [
                r'\d+\s*€',           # Price in euros
                r'\d+\s*m²',          # Area in square meters
                r'\d+\s*τ\.μ\.',      # Greek area abbreviation
                r'\d+\s*bedroom',     # Bedrooms
                r'\d+\s*δωμάτια',     # Greek for rooms
                r'apartment|διαμέρισμα',  # Apartment
            ]
            
            found_patterns = []
            for pattern in property_patterns:
                matches = re.findall(pattern, visible_text, re.I)
                if matches:
                    found_patterns.append((pattern, len(matches), matches[:3]))
            
            if found_patterns:
                print("   🎯 Property patterns found:")
                for pattern, count, examples in found_patterns:
                    print(f"     {pattern}: {count} matches, e.g. {examples}")
            
        except Exception as e:
            print(f"   ❌ Error in structure analysis: {e}")

async def main():
    debugger = PropertyExtractionDebugger()
    await debugger.analyze_website_structure()

if __name__ == "__main__":
    asyncio.run(main())