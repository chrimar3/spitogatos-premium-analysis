#!/usr/bin/env python3
"""
Main Page Deep Analysis
Analyze what's actually on the Spitogatos main page to understand navigation
"""

import asyncio
import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json

logging.basicConfig(level=logging.INFO)

async def analyze_main_page():
    """Deep analysis of the main page to understand site structure"""
    
    print("🔍 SPITOGATOS MAIN PAGE DEEP ANALYSIS")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale='el-GR',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        try:
            print("📍 Loading main page...")
            await page.goto("https://www.spitogatos.gr/", wait_until='domcontentloaded')
            await asyncio.sleep(10)  # Wait for any dynamic content
            
            title = await page.title()
            print(f"✅ Page loaded: {title}")
            
            # Get all links on the page
            links = await page.query_selector_all('a[href]')
            print(f"\n🔗 Found {len(links)} links on main page")
            
            real_links = []
            for link in links:
                href = await link.get_attribute('href')
                text = await link.text_content()
                
                if href and text:
                    real_links.append((href.strip(), text.strip()[:50]))
            
            # Filter for property-related links
            property_related = []
            property_keywords = ['αγγελ', 'search', 'property', 'διαμέρισμα', 'κατοικ', 'ενοικ', 'πωλ', 'listing']
            
            for href, text in real_links:
                text_lower = text.lower()
                href_lower = href.lower()
                
                if any(keyword in text_lower or keyword in href_lower for keyword in property_keywords):
                    property_related.append((href, text))
            
            print(f"\n🏠 Property-related links found: {len(property_related)}")
            for i, (href, text) in enumerate(property_related[:20]):  # Show first 20
                print(f"   {i+1}. {href} - {text}")
            
            # Look for navigation menu
            nav_elements = await page.query_selector_all('nav, .navigation, .menu, [class*="nav"], [class*="menu"]')
            print(f"\n🧭 Navigation elements found: {len(nav_elements)}")
            
            # Look for buttons/clickable elements
            buttons = await page.query_selector_all('button, [role="button"], .btn, [class*="button"]')
            print(f"\n🔘 Button elements found: {len(buttons)}")
            
            # Get page content for text analysis
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for form elements
            forms = soup.find_all('form')
            print(f"\n📝 Forms found: {len(forms)}")
            
            for i, form in enumerate(forms):
                print(f"   Form {i+1}:")
                inputs = form.find_all('input')
                for inp in inputs:
                    name = inp.get('name', '')
                    placeholder = inp.get('placeholder', '')
                    input_type = inp.get('type', '')
                    print(f"     Input: type='{input_type}', name='{name}', placeholder='{placeholder}'")
            
            # Look for specific text that might indicate functionality
            page_text = soup.get_text()
            
            # Check for property-related Greek text
            greek_indicators = [
                'διαμέρισμα', 'κατοικία', 'ενοικίαση', 'πώληση', 'αγγελίες',
                'ακίνητα', 'μ²', 'τιμή', 'περιοχή', 'αναζήτηση'
            ]
            
            found_indicators = []
            for indicator in greek_indicators:
                if indicator in page_text.lower():
                    found_indicators.append(indicator)
            
            print(f"\n🇬🇷 Greek property indicators found: {len(found_indicators)}")
            print(f"   {', '.join(found_indicators)}")
            
            # Execute JavaScript to see if there are dynamic elements
            print(f"\n⚡ JavaScript Analysis...")
            
            js_results = await page.evaluate("""
                () => {
                    const results = {
                        clickable_elements: 0,
                        data_attributes: [],
                        forms: 0,
                        inputs: 0
                    };
                    
                    // Count clickable elements
                    const clickable = document.querySelectorAll('a, button, [onclick], [role="button"]');
                    results.clickable_elements = clickable.length;
                    
                    // Find data attributes
                    const allElements = document.querySelectorAll('*');
                    const dataAttrs = new Set();
                    
                    allElements.forEach(el => {
                        for (let attr of el.attributes) {
                            if (attr.name.startsWith('data-')) {
                                dataAttrs.add(attr.name);
                            }
                        }
                    });
                    
                    results.data_attributes = Array.from(dataAttrs).slice(0, 20);
                    
                    // Count forms and inputs
                    results.forms = document.querySelectorAll('form').length;
                    results.inputs = document.querySelectorAll('input').length;
                    
                    return results;
                }
            """)
            
            print(f"   Clickable elements: {js_results['clickable_elements']}")
            print(f"   Forms: {js_results['forms']}")  
            print(f"   Inputs: {js_results['inputs']}")
            print(f"   Data attributes: {js_results['data_attributes'][:10]}")
            
            # Try to interact with search if we can find it
            print(f"\n🔍 Looking for search functionality...")
            
            # Try to find search input by various methods
            search_selectors = [
                'input[type="search"]',
                'input[name*="search"]',
                'input[placeholder*="αναζήτηση"]',
                'input[placeholder*="search"]',
                'input[placeholder*="περιοχή"]',
                'input[placeholder*="area"]',
                '.search-input',
                '[data-testid*="search"]'
            ]
            
            search_found = False
            for selector in search_selectors:
                try:
                    search_input = await page.query_selector(selector)
                    if search_input:
                        print(f"   ✅ Found search input: {selector}")
                        
                        # Try to interact with it
                        await search_input.fill("Κολωνάκι")
                        await asyncio.sleep(2)
                        
                        # Look for suggestions or results
                        suggestions = await page.query_selector_all('.suggestion, .dropdown, [class*="suggestion"]')
                        print(f"   Suggestions appeared: {len(suggestions)}")
                        
                        search_found = True
                        break
                except Exception as e:
                    print(f"   Failed with {selector}: {e}")
            
            if not search_found:
                print(f"   ❌ No search functionality found")
            
            # Save screenshot for manual analysis
            await page.screenshot(path="main_page_analysis.png", full_page=True)
            print(f"\n📸 Full page screenshot saved: main_page_analysis.png")
            
            # Keep browser open for manual inspection
            print(f"\n👀 Browser staying open for 30 seconds for manual inspection...")
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze_main_page())