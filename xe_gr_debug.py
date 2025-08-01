#!/usr/bin/env python3
"""
XE.GR DEBUG - Check current page structure
"""

import asyncio
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_xe_structure():
    """Debug current page structure"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='el-GR'
        )
        
        page = await context.new_page()
        
        try:
            # Navigate to homepage
            await page.goto("https://xe.gr", wait_until="load", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Handle cookies
            try:
                cookie_btn = await page.wait_for_selector('button:has-text("ΣΥΜΦΩΝΩ")', timeout=5000)
                if cookie_btn:
                    await cookie_btn.click()
                    await page.wait_for_timeout(2000)
            except:
                pass
            
            # Navigate to property section
            property_link = await page.wait_for_selector('a:has-text("Ακίνητα")', timeout=10000)
            await property_link.click()
            await page.wait_for_timeout(3000)
            
            # Fill location
            location_input = await page.wait_for_selector('input[placeholder*="Τοποθεσία"]', timeout=10000)
            await location_input.fill("Αθήνα, Κολωνάκι")
            
            # Take screenshot
            await page.screenshot(path='outputs/debug_filled_form.png')
            logger.info("📸 Screenshot saved after filling form")
            
            # Look for all buttons
            all_buttons = await page.query_selector_all('button')
            logger.info(f"🔘 Found {len(all_buttons)} buttons on page")
            
            for i, button in enumerate(all_buttons[:10]):  # Check first 10
                try:
                    text = await button.inner_text()
                    classes = await button.get_attribute('class')
                    type_attr = await button.get_attribute('type')
                    logger.info(f"   Button {i+1}: '{text}' | class='{classes}' | type='{type_attr}'")
                except:
                    continue
            
            # Try different search button selectors
            search_selectors = [
                'button:has-text("Αναζήτηση")',
                'button[type="submit"]',
                'input[type="submit"]',
                '.search-button',
                'button:has-text("Search")',
                'button:has-text("Εύρεση")',
                '[class*="search"] button',
                'form button'
            ]
            
            for selector in search_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=2000)
                    if element:
                        text = await element.inner_text()
                        logger.info(f"✅ Found search button: '{selector}' -> '{text}'")
                        
                        # Try clicking it
                        await element.click()
                        await page.wait_for_timeout(5000)
                        
                        # Take screenshot of results
                        await page.screenshot(path='outputs/debug_search_results.png')
                        logger.info("📸 Search results screenshot saved")
                        
                        # Check URL
                        current_url = page.url
                        logger.info(f"🔗 Results URL: {current_url}")
                        
                        # Look for property links
                        property_selectors = [
                            'a[href*="/d/"]',
                            'a[href*="property"]', 
                            'a[href*="enoikiaseis"]',
                            '.property a',
                            '.listing a',
                            '[class*="item"] a'
                        ]
                        
                        for prop_selector in property_selectors:
                            try:
                                prop_links = await page.query_selector_all(prop_selector)
                                if prop_links:
                                    logger.info(f"🏠 Found {len(prop_links)} links with selector: {prop_selector}")
                                    
                                    for j, link in enumerate(prop_links[:3]):
                                        href = await link.get_attribute('href')
                                        text = await link.inner_text()
                                        logger.info(f"   Link {j+1}: {text[:50]} -> {href}")
                                    break
                            except:
                                continue
                        
                        break
                except:
                    continue
            
        except Exception as e:
            logger.error(f"❌ Debug failed: {e}")
        
        finally:
            # Keep browser open for manual inspection
            logger.info("🔍 Browser kept open for manual inspection - close when done")
            await asyncio.sleep(60)  # Wait 1 minute
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_xe_structure())