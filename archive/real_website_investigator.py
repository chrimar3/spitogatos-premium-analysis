#!/usr/bin/env python3
"""
Real Spitogatos Website Structure Investigator
Deep analysis of actual website to extract REAL property data
"""

import asyncio
import logging
import json
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RealWebsiteInvestigator:
    """Investigate actual Spitogatos website structure for real data extraction"""
    
    def __init__(self):
        self.findings = {}
    
    async def comprehensive_investigation(self):
        """Deep investigation of real website structure"""
        
        print("🔍 REAL SPITOGATOS WEBSITE INVESTIGATION")
        print("=" * 60)
        
        async with async_playwright() as p:
            # Use our proven anti-detection setup
            browser = await p.chromium.launch(
                headless=False,  # Visible for investigation
                args=[
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale='el-GR',
                timezone_id='Europe/Athens',
                viewport={'width': 1920, 'height': 1080},
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                }
            )
            
            page = await context.new_page()
            
            try:
                # Step 1: Investigate main site and search functionality
                await self._investigate_main_site(page)
                
                # Step 2: Find working search URLs
                await self._find_working_search_urls(page)
                
                # Step 3: Analyze search results structure
                await self._analyze_search_results(page)
                
                # Step 4: Deep dive into property listings
                await self._analyze_property_listings(page)
                
                # Step 5: Extract real data patterns
                await self._extract_real_data_patterns(page)
                
                # Final report
                self._generate_investigation_report()
                
            except Exception as e:
                print(f"❌ Investigation error: {e}")
                import traceback
                traceback.print_exc()
            
            finally:
                await browser.close()
    
    async def _investigate_main_site(self, page):
        """Investigate main site structure"""
        
        print("\n📍 1. MAIN SITE INVESTIGATION")
        print("-" * 40)
        
        # Go to main page
        await page.goto("https://www.spitogatos.gr/", wait_until='domcontentloaded')
        await asyncio.sleep(5)  # Wait for any dynamic content
        
        title = await page.title()
        print(f"✅ Main page loaded: {title}")
        
        # Check for search form
        search_forms = await page.query_selector_all('form')
        print(f"🔍 Found {len(search_forms)} forms on main page")
        
        # Look for search inputs
        search_inputs = await page.query_selector_all('input[type="search"], input[name*="search"], input[placeholder*="search"], input[name*="location"]')
        print(f"🔍 Found {len(search_inputs)} search-related inputs")
        
        for i, input_elem in enumerate(search_inputs):
            name = await input_elem.get_attribute('name')
            placeholder = await input_elem.get_attribute('placeholder')
            print(f"   Input {i+1}: name='{name}', placeholder='{placeholder}'")
        
        # Check current URL structure
        current_url = page.url
        print(f"📍 Current URL: {current_url}")
        
        # Take screenshot for manual analysis
        await page.screenshot(path="investigation_main.png")
        print(f"📸 Screenshot saved: investigation_main.png")
    
    async def _find_working_search_urls(self, page):
        """Find URLs that actually work for property search"""
        
        print("\n📍 2. SEARCH URL INVESTIGATION")
        print("-" * 40)
        
        # Test various URL patterns that might work
        test_urls = [
            # Different URL structures to try
            "https://www.spitogatos.gr/search",
            "https://www.spitogatos.gr/en/search",
            "https://www.spitogatos.gr/listing",
            "https://www.spitogatos.gr/properties",
            "https://www.spitogatos.gr/enoikiazetai",
            "https://www.spitogatos.gr/poleitai",
            "https://www.spitogatos.gr/map",
            
            # Try specific area searches
            "https://www.spitogatos.gr/aggelies/katoikies/enoikiazetai/attiki/athina",
            "https://www.spitogatos.gr/aggelies/katoikies/poleitai/attiki/athina",
            "https://www.spitogatos.gr/search/katoikies-pros-polisi/attiki/athina",
            
            # Try different formats
            "https://www.spitogatos.gr/search?category=residential&type=sale&area=athens",
            "https://www.spitogatos.gr/search?q=athens&type=apartment",
        ]
        
        working_urls = []
        
        for url in test_urls:
            try:
                print(f"\n🧪 Testing: {url}")
                
                response = await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                await asyncio.sleep(3)
                
                if response and response.status == 200:
                    title = await page.title()
                    
                    # Check if this looks like a property search page
                    content = await page.content()
                    
                    # Look for property-related keywords
                    property_indicators = [
                        'διαμέρισμα', 'apartment', 'property', 'ακίνητο',
                        'τ.μ.', 'm²', '€', 'euro', 'ενεργειακή', 'energy'
                    ]
                    
                    found_indicators = sum(1 for indicator in property_indicators if indicator.lower() in content.lower())
                    
                    print(f"   ✅ SUCCESS: {title}")
                    print(f"   📊 Property indicators found: {found_indicators}/{len(property_indicators)}")
                    
                    if found_indicators >= 3:  # At least 3 property-related terms
                        working_urls.append((url, title, found_indicators))
                        print(f"   🎯 PROMISING URL - has property content!")
                        
                        # Take screenshot of promising pages
                        screenshot_name = f"investigation_search_{len(working_urls)}.png"
                        await page.screenshot(path=screenshot_name)
                        print(f"   📸 Screenshot saved: {screenshot_name}")
                
                else:
                    print(f"   ❌ Failed: Status {response.status if response else 'None'}")
                    
            except Exception as e:
                print(f"   ⚠️ Error: {e}")
        
        print(f"\n🎉 WORKING URLS FOUND: {len(working_urls)}")
        for i, (url, title, indicators) in enumerate(working_urls):
            print(f"   {i+1}. {url} (indicators: {indicators})")
        
        self.findings['working_urls'] = working_urls
        return working_urls
    
    async def _analyze_search_results(self, page):
        """Analyze structure of search results pages"""
        
        print("\n📍 3. SEARCH RESULTS ANALYSIS")
        print("-" * 40)
        
        working_urls = self.findings.get('working_urls', [])
        
        if not working_urls:
            print("❌ No working URLs found, cannot analyze search results")
            return
        
        # Use the most promising URL
        best_url = working_urls[0][0]
        print(f"🎯 Analyzing search results from: {best_url}")
        
        await page.goto(best_url, wait_until='domcontentloaded')
        await asyncio.sleep(5)
        
        # Get page content for analysis
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for common property listing patterns
        potential_selectors = [
            # Common property card selectors
            '[data-testid*="listing"]', '[data-testid*="property"]', '[data-testid*="card"]',
            '.listing', '.property', '.card', '.result', '.item',
            '[class*="listing"]', '[class*="property"]', '[class*="card"]', '[class*="result"]',
            'article', 'section[class*="property"]',
            
            # Greek-specific selectors
            '[class*="aggelies"]', '[class*="katoikia"]', '[class*="diamerisma"]'
        ]
        
        found_elements = {}
        
        for selector in potential_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    found_elements[selector] = len(elements)
                    print(f"✅ {selector}: {len(elements)} elements")
            except:
                pass
        
        # Look for price indicators
        print(f"\n💰 PRICE ANALYSIS:")
        price_elements = soup.find_all(string=re.compile(r'€|euro|\d{1,3}[.,]\d{3}', re.I))
        print(f"   Found {len(price_elements)} price-like elements")
        
        if price_elements:
            for i, price in enumerate(price_elements[:5]):
                print(f"   {i+1}. {price.strip()[:50]}")
        
        # Look for area/sqm indicators  
        print(f"\n📐 AREA ANALYSIS:")
        area_elements = soup.find_all(string=re.compile(r'\d+\s*(m²|τ\.μ\.|sqm)', re.I))
        print(f"   Found {len(area_elements)} area-like elements")
        
        if area_elements:
            for i, area in enumerate(area_elements[:5]):
                print(f"   {i+1}. {area.strip()}")
        
        # Look for energy class indicators
        print(f"\n⚡ ENERGY CLASS ANALYSIS:")
        energy_elements = soup.find_all(string=re.compile(r'ενεργειακή|energy|class|[A-F]\+?', re.I))
        print(f"   Found {len(energy_elements)} energy-related elements")
        
        self.findings['search_results'] = {
            'url': best_url,
            'selectors_found': found_elements,
            'price_elements': len(price_elements),
            'area_elements': len(area_elements),
            'energy_elements': len(energy_elements)
        }
    
    async def _analyze_property_listings(self, page):
        """Deep analysis of individual property listings"""
        
        print("\n📍 4. PROPERTY LISTING ANALYSIS")
        print("-" * 40)
        
        # Look for links to individual properties
        property_links = await page.query_selector_all('a[href*="property"], a[href*="listing"], a[href*="aggelies"]')
        
        print(f"🔗 Found {len(property_links)} potential property links")
        
        if property_links:
            # Try to visit first few properties
            for i in range(min(3, len(property_links))):
                try:
                    link = property_links[i]
                    href = await link.get_attribute('href')
                    
                    if href:
                        # Make URL absolute
                        if href.startswith('/'):
                            full_url = f"https://www.spitogatos.gr{href}"
                        else:
                            full_url = href
                        
                        print(f"\n🏠 Analyzing property {i+1}: {full_url}")
                        
                        # Navigate to property
                        await page.goto(full_url, wait_until='domcontentloaded')
                        await asyncio.sleep(3)
                        
                        # Analyze property page structure
                        await self._analyze_single_property_page(page, i+1)
                        
                except Exception as e:
                    print(f"   ❌ Error analyzing property {i+1}: {e}")
    
    async def _analyze_single_property_page(self, page, property_num):
        """Analyze structure of individual property page"""
        
        title = await page.title()
        print(f"   📄 Property title: {title}")
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for key property data
        data_found = {}
        
        # Price extraction patterns
        price_patterns = [
            r'€\s*(\d{1,3}(?:[.,]\d{3})*)',
            r'(\d{1,3}(?:[.,]\d{3})*)\s*€',
            r'τιμή[:\s]*(\d{1,3}(?:[.,]\d{3})*)',
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, content, re.I)
            if matches:
                data_found['price'] = matches[:3]
                break
        
        # Area extraction patterns
        area_patterns = [
            r'(\d+)\s*τ\.μ\.',
            r'(\d+)\s*m²',
            r'εμβαδό[:\s]*(\d+)',
        ]
        
        for pattern in area_patterns:
            matches = re.findall(pattern, content, re.I)
            if matches:
                data_found['area'] = matches[:3]
                break
        
        # Energy class extraction
        energy_patterns = [
            r'ενεργειακή\s+κλάση[:\s]*([A-F]\+?)',
            r'energy\s+class[:\s]*([A-F]\+?)',
            r'κλάση[:\s]*([A-F]\+?)',
        ]
        
        for pattern in energy_patterns:
            matches = re.findall(pattern, content, re.I)
            if matches:
                data_found['energy_class'] = matches[:3]
                break
        
        # Report findings
        for key, values in data_found.items():
            print(f"   ✅ {key}: {values}")
        
        if not data_found:
            print(f"   ⚠️ No key property data found")
        
        # Save screenshot
        screenshot_name = f"investigation_property_{property_num}.png"
        await page.screenshot(path=screenshot_name)
        print(f"   📸 Screenshot saved: {screenshot_name}")
        
        return data_found
    
    async def _extract_real_data_patterns(self, page):
        """Extract patterns for real data extraction"""
        
        print("\n📍 5. REAL DATA PATTERN EXTRACTION")
        print("-" * 40)
        
        # This would analyze the successful findings and create extraction patterns
        working_urls = self.findings.get('working_urls', [])
        
        if working_urls:
            best_url = working_urls[0][0]
            await page.goto(best_url, wait_until='domcontentloaded')
            await asyncio.sleep(5)
            
            # Execute JavaScript to get more detailed element information
            element_info = await page.evaluate("""
                () => {
                    const results = [];
                    
                    // Look for elements containing price-like text
                    const allElements = document.querySelectorAll('*');
                    
                    for (let elem of allElements) {
                        const text = elem.textContent || '';
                        
                        // Check for price patterns
                        if (/€|euro|\d{1,3}[.,]\d{3}/.test(text)) {
                            results.push({
                                type: 'price',
                                text: text.trim().substring(0, 100),
                                tagName: elem.tagName,
                                className: elem.className,
                                id: elem.id
                            });
                        }
                        
                        // Check for area patterns
                        if (/\d+\s*(m²|τ\.μ\.)/.test(text)) {
                            results.push({
                                type: 'area',
                                text: text.trim().substring(0, 100),
                                tagName: elem.tagName,
                                className: elem.className,
                                id: elem.id
                            });
                        }
                        
                        // Check for energy class patterns
                        if (/ενεργειακή|energy|[A-F]\+?\s*(class|κλάση)/.test(text)) {
                            results.push({
                                type: 'energy',
                                text: text.trim().substring(0, 100),
                                tagName: elem.tagName,
                                className: elem.className,
                                id: elem.id
                            });
                        }
                    }
                    
                    return results.slice(0, 50); // Limit results
                }
            """)
            
            # Analyze the element information
            for elem in element_info:
                print(f"   {elem['type'].upper()}: {elem['tagName']}.{elem['className']} - {elem['text'][:50]}")
            
            self.findings['element_patterns'] = element_info
        
        print(f"\n✅ Found {len(element_info)} relevant elements")
    
    def _generate_investigation_report(self):
        """Generate comprehensive investigation report"""
        
        print("\n" + "=" * 60)
        print("📋 REAL WEBSITE INVESTIGATION REPORT")
        print("=" * 60)
        
        # Summary of findings
        working_urls = self.findings.get('working_urls', [])
        search_results = self.findings.get('search_results', {})
        
        print(f"\n🔍 INVESTIGATION SUMMARY:")
        print(f"   Working URLs found: {len(working_urls)}")
        
        if working_urls:
            print(f"   Best URL: {working_urls[0][0]}")
            print(f"   Property indicators: {working_urls[0][2]}/10")
        
        if search_results:
            print(f"   Price elements found: {search_results.get('price_elements', 0)}")
            print(f"   Area elements found: {search_results.get('area_elements', 0)}")
            print(f"   Energy elements found: {search_results.get('energy_elements', 0)}")
        
        # Save detailed findings
        with open('real_website_investigation.json', 'w', encoding='utf-8') as f:
            json.dump(self.findings, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed findings saved to: real_website_investigation.json")
        print(f"📸 Screenshots saved for manual analysis")
        
        # Recommendations
        print(f"\n💡 NEXT STEPS:")
        if working_urls:
            print(f"   1. Use working URL: {working_urls[0][0]}")
            print(f"   2. Implement selectors based on found patterns")
            print(f"   3. Test extraction on real property data")
        else:
            print(f"   1. Website may require different approach")
            print(f"   2. Consider alternative data sources")
            print(f"   3. Manual analysis of screenshots needed")

async def main():
    investigator = RealWebsiteInvestigator()
    await investigator.comprehensive_investigation()

if __name__ == "__main__":
    asyncio.run(main())