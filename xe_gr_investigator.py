#!/usr/bin/env python3
"""
XE.gr Real Estate Website Deep Investigation
Focused investigation of xe.gr to extract REAL property data
"""

import asyncio
import logging
import json
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class XEGRInvestigator:
    """Deep investigation of xe.gr for real property data extraction"""
    
    def __init__(self):
        self.findings = {}
        self.base_url = "https://www.xe.gr"
    
    async def comprehensive_xe_investigation(self):
        """Deep investigation of xe.gr website structure"""
        
        print("🔍 XE.GR COMPREHENSIVE INVESTIGATION")
        print("=" * 60)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,  # Visible for investigation
                args=['--no-first-run', '--no-default-browser-check']
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale='el-GR',
                timezone_id='Europe/Athens',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            try:
                # Step 1: Investigate main site
                await self._investigate_xe_main_site(page)
                
                # Step 2: Find property search functionality
                await self._find_xe_search_functionality(page)
                
                # Step 3: Test specific area searches
                await self._test_xe_area_searches(page)
                
                # Step 4: Analyze property listings structure
                await self._analyze_xe_property_structure(page)
                
                # Step 5: Extract real property data
                await self._extract_xe_real_data(page)
                
                # Generate report
                self._generate_xe_report()
                
            except Exception as e:
                print(f"❌ Investigation error: {e}")
                import traceback
                traceback.print_exc()
            
            finally:
                print("\n⏳ Keeping browser open for 30 seconds for manual inspection...")
                await asyncio.sleep(30)
                await browser.close()
    
    async def _investigate_xe_main_site(self, page):
        """Investigate xe.gr main site structure"""
        
        print("\n📍 1. XE.GR MAIN SITE INVESTIGATION")
        print("-" * 40)
        
        # Go to main page
        await page.goto(self.base_url, wait_until='domcontentloaded')
        await asyncio.sleep(5)
        
        title = await page.title()
        print(f"✅ Main page loaded: {title}")
        
        # Take screenshot
        await page.screenshot(path="xe_main_investigation.png", full_page=True)
        print(f"📸 Screenshot saved: xe_main_investigation.png")
        
        # Look for navigation menu and property links
        nav_links = await page.query_selector_all('nav a, .menu a, .navigation a, [class*="nav"] a')
        print(f"🧭 Found {len(nav_links)} navigation links")
        
        property_related_links = []
        for link in nav_links:
            href = await link.get_attribute('href')
            text = await link.text_content()
            
            if href and text:
                text_lower = text.lower()
                href_lower = href.lower()
                
                # Look for property-related Greek and English terms
                property_keywords = [
                    'ακίνητα', 'property', 'properties', 'real estate',
                    'διαμέρισμα', 'apartment', 'καταλόγου', 'πώληση', 'ενοικίαση',
                    'sale', 'rent', 'buy', 'listing', 'search'
                ]
                
                if any(keyword in text_lower or keyword in href_lower for keyword in property_keywords):
                    property_related_links.append((href, text.strip()))
        
        print(f"🏠 Property-related links found: {len(property_related_links)}")
        for i, (href, text) in enumerate(property_related_links[:10]):
            print(f"   {i+1}. {href} - {text}")
        
        self.findings['main_site'] = {
            'title': title,
            'property_links': property_related_links
        }
        
        return property_related_links
    
    async def _find_xe_search_functionality(self, page):
        """Find xe.gr search functionality"""
        
        print("\n📍 2. XE.GR SEARCH FUNCTIONALITY")
        print("-" * 40)
        
        # Look for search forms and inputs
        search_inputs = await page.query_selector_all(
            'input[type="search"], input[name*="search"], input[placeholder*="search"], '
            'input[name*="location"], input[placeholder*="περιοχή"], input[placeholder*="area"]'
        )
        
        print(f"🔍 Found {len(search_inputs)} search inputs")
        
        for i, input_elem in enumerate(search_inputs):
            name = await input_elem.get_attribute('name')
            placeholder = await input_elem.get_attribute('placeholder')
            id_attr = await input_elem.get_attribute('id')
            print(f"   Input {i+1}: name='{name}', id='{id_attr}', placeholder='{placeholder}'")
        
        # Look for search buttons
        search_buttons = await page.query_selector_all(
            'button[type="submit"], input[type="submit"], button:has-text("Αναζήτηση"), '
            'button:has-text("Search"), .search-button, [class*="search"] button'
        )
        
        print(f"🔘 Found {len(search_buttons)} search buttons")
        
        # Try to interact with search if available
        if search_inputs:
            try:
                print(f"\n🧪 Testing search interaction...")
                search_input = search_inputs[0]
                
                # Try to fill in a test location
                await search_input.fill("Κολωνάκι")
                await asyncio.sleep(2)
                
                # Check for autocomplete/suggestions
                suggestions = await page.query_selector_all(
                    '.suggestion, .dropdown, .autocomplete, [class*="suggestion"], [class*="dropdown"]'
                )
                print(f"   Suggestions appeared: {len(suggestions)}")
                
                if suggestions:
                    for i, suggestion in enumerate(suggestions[:5]):
                        text = await suggestion.text_content()
                        print(f"     {i+1}. {text.strip()}")
                
                # Try to submit search
                if search_buttons:
                    print(f"   🔘 Attempting search submission...")
                    await search_buttons[0].click()
                    await asyncio.sleep(5)
                    
                    # Check if we got to results page
                    current_url = page.url
                    print(f"   📍 After search: {current_url}")
                    
                    if current_url != self.base_url:
                        await page.screenshot(path="xe_search_results.png")
                        print(f"   📸 Search results screenshot: xe_search_results.png")
            
            except Exception as e:
                print(f"   ⚠️ Search interaction failed: {e}")
    
    async def _test_xe_area_searches(self, page):
        """Test specific area searches on xe.gr"""
        
        print("\n📍 3. XE.GR AREA SEARCH TESTING")
        print("-" * 40)
        
        # Test various URL patterns for xe.gr
        test_urls = [
            # Different potential URL structures
            f"{self.base_url}/property",
            f"{self.base_url}/properties",
            f"{self.base_url}/real-estate",
            f"{self.base_url}/search",
            f"{self.base_url}/listings",
            
            # Greek-specific URLs
            f"{self.base_url}/akinhta",
            f"{self.base_url}/katoikies",
            f"{self.base_url}/diamerismata",
            
            # Search with parameters
            f"{self.base_url}/search?area=athens",
            f"{self.base_url}/search?location=kolonaki",
            f"{self.base_url}/property/search?area=athens",
            
            # Category-based URLs
            f"{self.base_url}/category/real-estate",
            f"{self.base_url}/category/properties",
        ]
        
        working_urls = []
        
        for url in test_urls:
            try:
                print(f"\n🧪 Testing: {url}")
                
                response = await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                await asyncio.sleep(3)
                
                if response and response.status == 200:
                    title = await page.title()
                    content = await page.content()
                    
                    # Check for property-related content
                    property_indicators = [
                        'διαμέρισμα', 'apartment', 'property', 'ακίνητο',
                        'τ.μ.', 'm²', '€', 'ενοικίαση', 'πώληση',
                        'sale', 'rent', 'listing', 'real estate'
                    ]
                    
                    found_indicators = sum(1 for indicator in property_indicators 
                                         if indicator.lower() in content.lower())
                    
                    print(f"   ✅ SUCCESS: {title}")
                    print(f"   📊 Property indicators: {found_indicators}/{len(property_indicators)}")
                    
                    if found_indicators >= 5:  # Strong indication of property content
                        working_urls.append((url, title, found_indicators))
                        print(f"   🎯 PROMISING URL!")
                        
                        screenshot_name = f"xe_promising_{len(working_urls)}.png"
                        await page.screenshot(path=screenshot_name)
                        print(f"   📸 Screenshot: {screenshot_name}")
                
                else:
                    print(f"   ❌ Failed: Status {response.status if response else 'None'}")
                    
            except Exception as e:
                print(f"   ⚠️ Error: {str(e)[:100]}")
        
        print(f"\n🎉 WORKING XE.GR URLS: {len(working_urls)}")
        for i, (url, title, indicators) in enumerate(working_urls):
            print(f"   {i+1}. {url} (indicators: {indicators})")
        
        self.findings['working_urls'] = working_urls
        return working_urls
    
    async def _analyze_xe_property_structure(self, page):
        """Analyze xe.gr property listing structure"""
        
        print("\n📍 4. XE.GR PROPERTY STRUCTURE ANALYSIS")
        print("-" * 40)
        
        working_urls = self.findings.get('working_urls', [])
        
        if not working_urls:
            print("❌ No working URLs found for structure analysis")
            return
        
        # Use the best working URL
        best_url = working_urls[0][0]
        print(f"🎯 Analyzing structure from: {best_url}")
        
        await page.goto(best_url, wait_until='domcontentloaded')
        await asyncio.sleep(5)
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for property listing containers
        potential_containers = [
            '[data-testid*="listing"]', '[data-testid*="property"]',
            '.listing', '.property', '.card', '.item',
            '[class*="listing"]', '[class*="property"]', '[class*="card"]',
            'article', '.result', '[class*="result"]'
        ]
        
        found_containers = {}
        
        for selector in potential_containers:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    found_containers[selector] = len(elements)
                    print(f"✅ {selector}: {len(elements)} elements")
            except:
                pass
        
        # Analyze text for property data patterns
        print(f"\n📊 PROPERTY DATA ANALYSIS:")
        
        # Price analysis
        price_matches = re.findall(r'€\s*[\d.,]+|[\d.,]+\s*€|\d{3,}', content)
        print(f"   💰 Price patterns found: {len(price_matches)}")
        if price_matches:
            print(f"       Examples: {', '.join(price_matches[:5])}")
        
        # Area analysis
        area_matches = re.findall(r'\d+\s*(?:τ\.μ\.|m²|sqm)', content, re.I)
        print(f"   📐 Area patterns found: {len(area_matches)}")
        if area_matches:
            print(f"       Examples: {', '.join(area_matches[:5])}")
        
        # Energy class analysis
        energy_matches = re.findall(r'ενεργειακή|energy.*?[A-F]\+?|[A-F]\+?\s*(?:κλάση|class)', content, re.I)
        print(f"   ⚡ Energy patterns found: {len(energy_matches)}")
        if energy_matches:
            print(f"       Examples: {', '.join(energy_matches[:5])}")
        
        self.findings['structure_analysis'] = {
            'url': best_url,
            'containers': found_containers,
            'price_patterns': len(price_matches),
            'area_patterns': len(area_matches),
            'energy_patterns': len(energy_matches)
        }
    
    async def _extract_xe_real_data(self, page):
        """Extract real property data from xe.gr"""
        
        print("\n📍 5. XE.GR REAL DATA EXTRACTION")
        print("-" * 40)
        
        working_urls = self.findings.get('working_urls', [])
        
        if not working_urls:
            print("❌ No working URLs for data extraction")
            return []
        
        best_url = working_urls[0][0]
        print(f"🎯 Extracting real data from: {best_url}")
        
        await page.goto(best_url, wait_until='domcontentloaded')
        await asyncio.sleep(5)
        
        # Use JavaScript to extract detailed element information
        property_data = await page.evaluate("""
            () => {
                const properties = [];
                
                // Look for any elements that might contain property information
                const allElements = document.querySelectorAll('*');
                const processedTexts = new Set();
                
                for (let elem of allElements) {
                    const text = elem.textContent || '';
                    
                    // Skip if we've already processed this text or it's too short
                    if (text.length < 20 || processedTexts.has(text)) continue;
                    processedTexts.add(text);
                    
                    // Check if this element contains property-like information
                    const hasPrice = /€|euro|\\d{4,}/.test(text);
                    const hasArea = /\\d+\\s*(m²|τ\\.μ\\.|sqm)/i.test(text);
                    const hasEnergy = /(ενεργειακή|energy|[A-F]\\+?)/i.test(text);
                    const hasLocation = /(αθήνα|athens|περιοχή|area)/i.test(text);
                    
                    // If this looks like property data
                    if ((hasPrice && hasArea) || (hasPrice && hasEnergy) || (hasArea && hasEnergy)) {
                        
                        // Extract specific data
                        const priceMatch = text.match(/€\\s*([\\d.,]+)|([\\d.,]+)\\s*€|(\\d{4,})/);
                        const areaMatch = text.match(/(\\d+)\\s*(?:τ\\.μ\\.|m²|sqm)/i);
                        const energyMatch = text.match(/(?:ενεργειακή|energy).*?([A-F]\\+?)|([A-F]\\+?).*?(?:κλάση|class)/i);
                        
                        properties.push({
                            text: text.trim().substring(0, 200),
                            element: elem.tagName + (elem.className ? '.' + elem.className : ''),
                            price: priceMatch ? priceMatch[1] || priceMatch[2] || priceMatch[3] : null,
                            area: areaMatch ? parseInt(areaMatch[1]) : null,
                            energy_class: energyMatch ? (energyMatch[1] || energyMatch[2]) : null,
                            has_price: hasPrice,
                            has_area: hasArea,
                            has_energy: hasEnergy,
                            has_location: hasLocation
                        });
                    }
                }
                
                return properties.slice(0, 20); // Limit to first 20 potential properties
            }
        """)
        
        print(f"🏠 EXTRACTED PROPERTY DATA: {len(property_data)} items")
        
        real_properties = []
        
        for i, prop in enumerate(property_data):
            print(f"\n   Property {i+1}:")
            print(f"     Text: {prop['text'][:100]}...")
            print(f"     Element: {prop['element']}")
            
            if prop['price']:
                print(f"     💰 Price: €{prop['price']}")
            if prop['area']:
                print(f"     📐 Area: {prop['area']}m²")
            if prop['energy_class']:
                print(f"     ⚡ Energy: {prop['energy_class']}")
            
            # Count as real if it has at least price or area
            if prop['price'] or prop['area']:
                real_properties.append(prop)
                print(f"     ✅ REAL PROPERTY DATA FOUND")
            else:
                print(f"     ⚠️ Insufficient data")
        
        print(f"\n🎉 REAL PROPERTIES FOUND: {len(real_properties)}")
        
        self.findings['extracted_data'] = {
            'total_items': len(property_data),
            'real_properties': len(real_properties),
            'properties': real_properties
        }
        
        return real_properties
    
    def _generate_xe_report(self):
        """Generate comprehensive xe.gr investigation report"""
        
        print("\n" + "=" * 60)
        print("📋 XE.GR INVESTIGATION REPORT")
        print("=" * 60)
        
        main_site = self.findings.get('main_site', {})
        working_urls = self.findings.get('working_urls', [])
        structure = self.findings.get('structure_analysis', {})
        extracted = self.findings.get('extracted_data', {})
        
        print(f"\n🔍 INVESTIGATION SUMMARY:")
        print(f"   Main site analyzed: {main_site.get('title', 'N/A')}")
        print(f"   Property-related links: {len(main_site.get('property_links', []))}")
        print(f"   Working URLs found: {len(working_urls)}")
        
        if working_urls:
            print(f"   Best URL: {working_urls[0][0]}")
            print(f"   Property indicators: {working_urls[0][2]}")
        
        if structure:
            print(f"   Price patterns: {structure.get('price_patterns', 0)}")
            print(f"   Area patterns: {structure.get('area_patterns', 0)}")
            print(f"   Energy patterns: {structure.get('energy_patterns', 0)}")
        
        if extracted:
            print(f"   Total items analyzed: {extracted.get('total_items', 0)}")
            print(f"   Real properties found: {extracted.get('real_properties', 0)}")
        
        # Save detailed findings
        with open('xe_gr_investigation.json', 'w', encoding='utf-8') as f:
            json.dump(self.findings, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Detailed findings saved to: xe_gr_investigation.json")
        print(f"📸 Screenshots saved for manual analysis")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if extracted.get('real_properties', 0) > 0:
            print(f"   ✅ XE.GR HAS REAL PROPERTY DATA!")
            print(f"   1. Implement extraction based on successful patterns")
            print(f"   2. Use working URL: {working_urls[0][0] if working_urls else 'N/A'}")
            print(f"   3. Focus on elements with price and area data")
        else:
            print(f"   ⚠️ No real property data found")
            print(f"   1. Manual analysis of screenshots needed")
            print(f"   2. May need different navigation approach")
            print(f"   3. Consider other alternative sources")

async def main():
    investigator = XEGRInvestigator()
    await investigator.comprehensive_xe_investigation()

if __name__ == "__main__":
    asyncio.run(main())