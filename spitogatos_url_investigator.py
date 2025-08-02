#!/usr/bin/env python3
"""
SPITOGATOS URL STRUCTURE INVESTIGATOR
Research current working URL patterns for property discovery
"""

import asyncio
import logging
from playwright.async_api import async_playwright

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def investigate_spitogatos_urls():
    """Investigate current working Spitogatos URL patterns"""
    
    logger.info("🔍 INVESTIGATING SPITOGATOS URL PATTERNS")
    
    # Test URLs to investigate
    test_urls = [
        "https://www.spitogatos.gr",
        "https://www.spitogatos.gr/en",
        "https://www.spitogatos.gr/search",
        "https://www.spitogatos.gr/en/search",
        "https://www.spitogatos.gr/property",
        "https://www.spitogatos.gr/en/property",
        "https://www.spitogatos.gr/en/for_sale-homes/athens-center",
        "https://www.spitogatos.gr/for_sale-homes/athens-center",
        "https://www.spitogatos.gr/en/property/1117843683",  # Known working from our data
        "https://www.spitogatos.gr/listings",
        "https://www.spitogatos.gr/en/listings",
        "https://www.spitogatos.gr/en/real-estate",
        "https://www.spitogatos.gr/real-estate",
        "https://www.spitogatos.gr/en/properties",
        "https://www.spitogatos.gr/properties"
    ]
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    )
    page = await context.new_page()
    
    working_urls = []
    
    for url in test_urls:
        try:
            logger.info(f"🔍 Testing: {url}")
            
            await page.goto(url, wait_until='networkidle', timeout=15000)
            
            # Check if page loaded successfully
            title = await page.title()
            content = await page.content()
            
            if "404" not in title.lower() and len(content) > 1000:
                logger.info(f"✅ WORKING: {url} - Title: {title}")
                working_urls.append({
                    'url': url,
                    'title': title,
                    'content_length': len(content)
                })
                
                # Look for property links on this page
                property_links = await page.query_selector_all('a[href*="property"]')
                logger.info(f"   📦 Found {len(property_links)} property links")
                
                # Sample some property URLs
                for i, link in enumerate(property_links[:3]):
                    href = await link.get_attribute('href')
                    if href:
                        logger.info(f"   🏠 Property link {i+1}: {href}")
            else:
                logger.warning(f"❌ FAILED: {url} - {title}")
            
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.warning(f"❌ ERROR testing {url}: {e}")
            continue
    
    await browser.close()
    await playwright.stop()
    
    logger.info(f"\n📊 INVESTIGATION RESULTS:")
    logger.info(f"✅ Working URLs: {len(working_urls)}")
    for url_info in working_urls:
        logger.info(f"   {url_info['url']} - {url_info['title']}")
    
    return working_urls

if __name__ == "__main__":
    asyncio.run(investigate_spitogatos_urls())