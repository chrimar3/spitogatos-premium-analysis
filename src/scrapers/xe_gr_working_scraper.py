#!/usr/bin/env python3
"""
XE.GR WORKING SCRAPER - Using discovered navigation flow
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def scrape_xe_properties(neighborhood="Κολωνάκι", max_properties=5):
    """Working XE.gr scraper using discovered navigation"""
    
    logger.info(f"🏠 WORKING XE.GR SCRAPER - {neighborhood}")
    
    properties = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Keep visible for now
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='el-GR'
        )
        
        page = await context.new_page()
        
        try:
            # Step 1: Homepage and cookie consent
            logger.info("🏠 Loading homepage and handling cookies...")
            await page.goto("https://xe.gr", wait_until="load", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Handle cookies
            try:
                cookie_btn = await page.wait_for_selector('button:has-text("ΣΥΜΦΩΝΩ")', timeout=5000)
                if cookie_btn:
                    await cookie_btn.click()
                    logger.info("✅ Accepted cookies")
                    await page.wait_for_timeout(2000)
            except:
                logger.info("ℹ️ No cookie dialog found")
            
            # Step 2: Navigate to property section
            logger.info("🏡 Navigating to property section...")
            property_link = await page.wait_for_selector('a:has-text("Ακίνητα")', timeout=10000)
            await property_link.click()
            await page.wait_for_timeout(3000)
            
            logger.info("📄 Property section loaded")
            
            # Step 3: Use the search form
            logger.info(f"🔍 Searching for properties in {neighborhood}...")
            
            # Fill location field
            location_input = await page.wait_for_selector('input[placeholder*="Τοποθεσία"]', timeout=10000)
            await location_input.fill(f"Αθήνα, {neighborhood}")
            logger.info(f"✅ Filled location: Αθήνα, {neighborhood}")
            
            # Make sure "Ενοίκιση" (Rent) is selected
            try:
                rent_dropdown = await page.wait_for_selector('select', timeout=5000)
                await rent_dropdown.select_option(label='Ενοίκιση')
                logger.info("✅ Selected Ενοίκιση (Rent)")
            except:
                logger.info("ℹ️ Rent already selected or not found")
            
            # Click search
            search_btn = await page.wait_for_selector('button:has-text("Αναζήτηση")', timeout=10000)
            await search_btn.click()
            logger.info("✅ Clicked search button")
            
            # Wait for results to load
            await page.wait_for_timeout(5000)
            
            # Step 4: Extract property URLs from results
            logger.info("📦 Extracting property URLs...")
            
            # Take screenshot of results
            await page.screenshot(path='outputs/search_results_working.png')
            logger.info("📸 Search results screenshot saved")
            
            # Look for property links in various patterns
            property_links = []
            
            # Try multiple selectors for property links
            selectors_to_try = [
                'a[href*="/d/"]',
                'a[href*="property"]',
                'a[href*="enoikiaseis"]',
                '.property-item a',
                '.listing a',
                '.result a',
                '[data-testid*="listing"] a'
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        href = await element.get_attribute('href')
                        if href and 'xe.gr' in href and '/d/' in href:
                            title = await element.inner_text()
                            property_links.append((title.strip()[:100], href))
                            if len(property_links) >= max_properties * 2:  # Get extra for filtering
                                break
                except:
                    continue
                
                if property_links:
                    break
            
            # Remove duplicates
            unique_links = []
            seen_urls = set()
            for title, url in property_links:
                if url not in seen_urls:
                    unique_links.append((title, url))
                    seen_urls.add(url)
            
            logger.info(f"📦 Found {len(unique_links)} unique property URLs")
            
            # Step 5: Visit each property and extract data
            for i, (title, url) in enumerate(unique_links[:max_properties]):
                logger.info(f"🏠 Scraping property {i+1}/{min(len(unique_links), max_properties)}")
                logger.info(f"   📋 {title}")
                logger.info(f"   🔗 {url[:80]}...")
                
                try:
                    # Navigate to property page
                    await page.goto(url, wait_until="load", timeout=30000)
                    await page.wait_for_timeout(3000)
                    
                    # Extract property data
                    property_data = await extract_property_data(page, url, neighborhood)
                    if property_data:
                        properties.append(property_data)
                        logger.info(f"   ✅ Extracted: {property_data.get('address', 'N/A')} - €{property_data.get('price', 'N/A')}")
                    else:
                        logger.warning(f"   ❌ Failed to extract data")
                    
                    # Respectful delay
                    await page.wait_for_timeout(2000)
                    
                except Exception as e:
                    logger.error(f"   ❌ Error scraping property: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"❌ Scraping failed: {e}")
        
        finally:
            await browser.close()
    
    logger.info(f"🎯 SCRAPING COMPLETE: {len(properties)} properties extracted")
    return properties

async def extract_property_data(page, url, neighborhood):
    """Extract data from individual property page"""
    
    try:
        # Get page content
        content = await page.content()
        
        # Basic validation - is this a property page?
        if not any(indicator in content.lower() for indicator in ['τιμή', 'price', 'τ.μ', 'ενοικίαση', 'διαμέρισμα']):
            return None
        
        property_data = {
            'url': url,
            'neighborhood': neighborhood,
            'extraction_timestamp': datetime.now().isoformat(),
            'title': '',
            'address': '',
            'price': None,
            'sqm': None,
            'rooms': None,
            'description': ''
        }
        
        # Extract title
        try:
            title_element = await page.query_selector('h1, .property-title, .listing-title')
            if title_element:
                property_data['title'] = (await title_element.inner_text()).strip()[:200]
        except:
            pass
        
        # Extract price
        try:
            # Look for price patterns
            page_text = await page.inner_text('body')
            import re
            
            price_patterns = [
                r'(\d{1,3}(?:\.\d{3})*)\s*€',
                r'€\s*(\d{1,3}(?:\.\d{3})*)',
                r'τιμή[:\s]*(\d{1,3}(?:\.\d{3})*)',
                r'(\d{1,3}(?:\.\d{3})*)\s*ευρώ'
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    try:
                        price_str = match.group(1).replace('.', '')
                        price = float(price_str)
                        if 50 <= price <= 5000000:  # Reasonable range
                            property_data['price'] = price
                            break
                    except:
                        continue
        except:
            pass
        
        # Extract area (sqm)
        try:
            sqm_patterns = [
                r'(\d+(?:[.,]\d+)?)\s*τ\.?μ\.?',
                r'(\d+(?:[.,]\d+)?)\s*m²',
                r'εμβαδόν[:\s]*(\d+(?:[.,]\d+)?)'
            ]
            
            for pattern in sqm_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    try:
                        sqm = float(match.group(1).replace(',', '.'))
                        if 10 <= sqm <= 500:  # Reasonable range
                            property_data['sqm'] = sqm
                            break
                    except:
                        continue
        except:
            pass
        
        # Extract address/location
        try:
            location_selectors = ['.address', '.location', '.property-address', '[class*="location"]']
            for selector in location_selectors:
                element = await page.query_selector(selector)
                if element:
                    address = (await element.inner_text()).strip()
                    if len(address) > 5 and any(word in address.lower() for word in ['αθήνα', 'athens', neighborhood.lower()]):
                        property_data['address'] = address[:300]
                        break
        except:
            pass
        
        # If no specific address found, try to find Athens reference in page
        if not property_data['address']:
            try:
                if 'αθήνα' in page_text.lower() or 'athens' in page_text.lower():
                    property_data['address'] = f"Αθήνα, {neighborhood}"
            except:
                pass
        
        # Extract description
        try:
            desc_selectors = ['.description', '.property-description', '.details', '[class*="description"]']
            for selector in desc_selectors:
                element = await page.query_selector(selector)
                if element:
                    desc = (await element.inner_text()).strip()
                    if len(desc) > 20:
                        property_data['description'] = desc[:500]
                        break
        except:
            pass
        
        # Validation - must have at least title or address
        if property_data['title'] or property_data['address']:
            return property_data
        else:
            return None
            
    except Exception as e:
        logger.error(f"❌ Property data extraction failed: {e}")
        return None

async def main():
    """Test the working scraper"""
    
    logger.info("🚀 TESTING WORKING XE.GR SCRAPER")
    
    # Test with Kolonaki
    properties = await scrape_xe_properties("Κολωνάκι", max_properties=3)
    
    if properties:
        logger.info(f"\n✅ SUCCESS! Extracted {len(properties)} properties:")
        
        for i, prop in enumerate(properties, 1):
            logger.info(f"\n📊 PROPERTY {i}:")
            logger.info(f"   Title: {prop.get('title', 'N/A')}")
            logger.info(f"   Address: {prop.get('address', 'N/A')}")
            logger.info(f"   Price: €{prop.get('price', 'N/A')}")
            logger.info(f"   Area: {prop.get('sqm', 'N/A')}m²")
            logger.info(f"   URL: {prop['url'][:80]}...")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'outputs/xe_working_results_{timestamp}.json'
        
        os.makedirs('outputs', exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(properties, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📄 Results saved: {output_file}")
        logger.info("🎉 WORKING SCRAPER TEST SUCCESSFUL!")
        
    else:
        logger.error("❌ No properties extracted - check screenshots for debugging")

if __name__ == "__main__":
    asyncio.run(main())