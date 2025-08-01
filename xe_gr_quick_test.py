#!/usr/bin/env python3
"""
XE.GR QUICK TEST - Focused approach to overcome current issues
"""

import asyncio
import logging
from playwright.async_api import async_playwright

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_xe_access():
    """Quick test to find working access method"""
    
    logger.info("🧪 QUICK XE.GR ACCESS TEST")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible for debugging
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='el-GR'
        )
        
        page = await context.new_page()
        
        try:
            # Step 1: Navigate to homepage
            logger.info("🏠 Loading XE.gr homepage...")
            await page.goto("https://xe.gr", wait_until="load", timeout=30000)
            await page.wait_for_timeout(3000)
            
            title = await page.title()
            logger.info(f"📄 Homepage title: {title}")
            
            # Step 2: Handle cookie consent
            logger.info("🍪 Looking for cookie consent...")
            cookie_buttons = [
                'button:has-text("ΣΥΜΦΩΝΩ")',
                'button:has-text("Συμφωνώ")', 
                'button:has-text("ΑΠΟΔΟΧΗ")',
                'button:has-text("OK")',
                'button[class*="accept"]',
                'button[class*="cookie"]'
            ]
            
            for selector in cookie_buttons:
                try:
                    element = await page.wait_for_selector(selector, timeout=2000)
                    if element and await element.is_visible():
                        await element.click()
                        logger.info(f"✅ Clicked cookie button: {selector}")
                        await page.wait_for_timeout(2000)
                        break
                except:
                    continue
            
            # Step 3: Look for property section navigation
            logger.info("🏡 Looking for property navigation...")
            
            # Take screenshot of homepage
            await page.screenshot(path='outputs/homepage_test.png')
            logger.info("📸 Homepage screenshot saved")
            
            # Try to find property links
            property_links = await page.query_selector_all('a')
            logger.info(f"📎 Found {len(property_links)} links on homepage")
            
            # Check first 20 links for property-related ones
            property_candidates = []
            for i, link in enumerate(property_links[:20]):
                try:
                    href = await link.get_attribute('href')
                    text = await link.inner_text()
                    if href and any(word in href.lower() for word in ['property', 'enoikias', 'polis', 'akinht']):
                        property_candidates.append((text.strip(), href))
                        logger.info(f"🎯 Property link found: {text.strip()} -> {href}")
                except:
                    continue
            
            # Step 4: Try clicking a property link if found
            if property_candidates:
                best_link = property_candidates[0]
                logger.info(f"🔗 Trying best property link: {best_link[0]}")
                
                try:
                    await page.goto(best_link[1], wait_until="load", timeout=30000)
                    await page.wait_for_timeout(3000)
                    
                    new_title = await page.title()
                    logger.info(f"📄 Property page title: {new_title}")
                    
                    # Take screenshot
                    await page.screenshot(path='outputs/property_page_test.png')
                    logger.info("📸 Property page screenshot saved")
                    
                    # Look for property listings on this page
                    all_links = await page.query_selector_all('a')
                    listing_links = []
                    
                    for link in all_links:
                        try:
                            href = await link.get_attribute('href')
                            text = await link.inner_text()
                            if href and '/d/' in href and any(word in href.lower() for word in ['enoikias', 'polis', 'diameris']):
                                listing_links.append((text.strip()[:50], href))
                        except:
                            continue
                    
                    logger.info(f"🏠 Found {len(listing_links)} potential property listings")
                    for text, url in listing_links[:5]:
                        logger.info(f"   📋 {text} -> {url[:80]}...")
                        
                    if listing_links:
                        # Test accessing one property listing
                        test_url = listing_links[0][1]
                        logger.info(f"🧪 Testing property URL: {test_url[:80]}...")
                        
                        await page.goto(test_url, wait_until="load", timeout=30000)
                        await page.wait_for_timeout(3000)
                        
                        prop_title = await page.title()
                        logger.info(f"📄 Property listing title: {prop_title}")
                        
                        # Check if it's a real property page
                        page_content = await page.content()
                        if any(indicator in page_content.lower() for indicator in ['τιμή', 'price', 'τ.μ', 'διαμέρισμα']):
                            logger.info("✅ SUCCESS! Found working property page")
                            
                            # Take final screenshot
                            await page.screenshot(path='outputs/successful_property.png')
                            
                            # Extract some basic info
                            try:
                                price_element = await page.query_selector('*:has-text("€")')
                                if price_element:
                                    price_text = await price_element.inner_text()
                                    logger.info(f"💰 Found price info: {price_text[:50]}")
                            except:
                                pass
                        else:
                            logger.warning("⚠️ Property page doesn't contain expected content")
                
                except Exception as e:
                    logger.error(f"❌ Property link navigation failed: {e}")
            
            else:
                logger.warning("⚠️ No property links found on homepage")
                
                # Try direct search
                logger.info("🔍 Trying direct search...")
                search_selectors = [
                    'input[type="search"]',
                    'input[name*="search"]',
                    'input[placeholder*="αναζήτηση"]',
                    'input[placeholder*="search"]'
                ]
                
                for selector in search_selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=2000)
                        if element:
                            await element.fill("Κολωνάκι διαμέρισμα")
                            await page.keyboard.press('Enter')
                            logger.info("✅ Submitted search")
                            await page.wait_for_timeout(5000)
                            
                            search_title = await page.title()
                            logger.info(f"📄 Search results title: {search_title}")
                            
                            await page.screenshot(path='outputs/search_results_test.png')
                            break
                    except:
                        continue
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
        
        finally:
            await browser.close()
        
        logger.info("🧪 Quick test completed - check outputs/ for screenshots")

if __name__ == "__main__":
    asyncio.run(test_xe_access())