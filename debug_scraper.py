#!/usr/bin/env python3
"""
Debug script to inspect the actual website structure
"""

import asyncio
import logging
from playwright.async_api import async_playwright

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def debug_website():
    """Debug the website to understand its current structure"""
    
    print("🔍 Debugging Spitogatos Website Structure")
    print("=" * 50)
    
    async with async_playwright() as p:
        # Launch browser in visible mode for debugging
        browser = await p.chromium.launch(headless=False)
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale='el-GR',
            timezone_id='Europe/Athens',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        try:
            # Go to main page first
            print("📝 Loading main page...")
            await page.goto("https://www.spitogatos.gr/", wait_until='domcontentloaded')
            await asyncio.sleep(3)
            
            print(f"✅ Main page loaded: {page.url}")
            print(f"📄 Page title: {await page.title()}")
            
            # Try a search
            search_url = "https://www.spitogatos.gr/search/apartments-for-sale/attica/athens"
            print(f"\n🔍 Loading search page: {search_url}")
            
            response = await page.goto(search_url, wait_until='domcontentloaded')
            print(f"📊 Response status: {response.status}")
            print(f"📄 Search page title: {await page.title()}")
            
            await asyncio.sleep(5)  # Wait for dynamic content
            
            # Check what selectors exist on the page
            print("\n🔍 Analyzing page structure...")
            
            selectors_to_check = [
                '[data-testid="ad-card"]',
                '.result-card',
                '.listing-item',
                '.property-card',
                '.listing',
                '.result',
                '[class*="card"]',
                '[class*="listing"]',
                '[class*="property"]'
            ]
            
            for selector in selectors_to_check:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    else:
                        print(f"❌ No elements found for selector: {selector}")
                except Exception as e:
                    print(f"⚠️  Error checking selector {selector}: {e}")
            
            # Get page content for manual inspection
            content = await page.content()
            
            # Look for common patterns
            if "property" in content.lower():
                print("✅ Found 'property' in page content")
            if "apartment" in content.lower():
                print("✅ Found 'apartment' in page content")
            if "listing" in content.lower():
                print("✅ Found 'listing' in page content")
            
            # Save screenshot for manual inspection
            await page.screenshot(path="debug_screenshot.png")
            print("📸 Screenshot saved as debug_screenshot.png")
            
            # Keep browser open for manual inspection
            print("\n⏳ Browser will stay open for 30 seconds for manual inspection...")
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_website())