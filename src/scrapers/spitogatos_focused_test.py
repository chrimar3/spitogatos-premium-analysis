#!/usr/bin/env python3
"""
SPITOGATOS.GR FOCUSED TEST
Quick test to extract real property data from target neighborhoods
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def extract_real_data_focused_test():
    """Focused test to extract real property data from Spitogatos.gr"""
    
    logger.info("🎯 SPITOGATOS.GR FOCUSED TEST - REAL DATA EXTRACTION")
    
    # Test URLs discovered from investigation
    test_urls = [
        "https://www.spitogatos.gr/en/for_sale-homes/athens-center",
        "https://www.spitogatos.gr/en/for_rent-homes/athens-center"
    ]
    
    # Target neighborhoods to search for
    target_neighborhoods = ["Kolonaki", "Pangrati", "Κολωνάκι", "Παγκράτι"]
    
    extracted_properties = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='el-GR'
        )
        
        # Add stealth script
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        
        page = await context.new_page()
        
        for test_url in test_urls:
            logger.info(f"🔍 Testing: {test_url}")
            
            try:
                await page.goto(test_url, wait_until='networkidle', timeout=30000)
                
                # Take screenshot
                timestamp = datetime.now().strftime("%H%M%S")
                await page.screenshot(path=f"outputs/spitogatos_focused_test_{timestamp}.png")
                
                # Look for property links
                property_links = await page.query_selector_all('a[href*="/property/"]')
                logger.info(f"✅ Found {len(property_links)} property links")
                
                # Extract first 5 property URLs for testing
                test_property_urls = []
                for i, link in enumerate(property_links[:5]):
                    href = await link.get_attribute('href')
                    if href and '/property/' in href:
                        if href.startswith('/'):
                            href = f"https://www.spitogatos.gr{href}"
                        test_property_urls.append(href)
                
                logger.info(f"📋 Testing {len(test_property_urls)} individual properties")
                
                # Test each property page
                for i, property_url in enumerate(test_property_urls):
                    logger.info(f"🏠 Testing property {i+1}: {property_url}")
                    
                    try:
                        await page.goto(property_url, wait_until='networkidle', timeout=30000)
                        
                        # Extract property data
                        title_element = await page.query_selector('h1')
                        title = await title_element.inner_text() if title_element else ""
                        
                        # Check if this property is in target neighborhoods
                        is_target_neighborhood = any(
                            neighborhood.lower() in title.lower() 
                            for neighborhood in target_neighborhoods
                        )
                        
                        if is_target_neighborhood:
                            logger.info(f"🎯 TARGET NEIGHBORHOOD FOUND: {title}")
                        
                        # Extract price
                        price = None
                        price_selectors = [
                            '.price', '.property-price', '[data-testid*="price"]',
                            'span:has-text("€")', 'div:has-text("€")'
                        ]
                        
                        for selector in price_selectors:
                            try:
                                price_element = await page.query_selector(selector)
                                if price_element:
                                    price_text = await price_element.inner_text()
                                    price_match = re.search(r'€\s*([0-9.,]+)', price_text.replace('.', '').replace(',', ''))
                                    if price_match:
                                        price = float(price_match.group(1).replace(',', ''))
                                        break
                            except:
                                continue
                        
                        # Extract square meters
                        sqm = None
                        sqm_selectors = [
                            '.sqm', '.area', '[data-testid*="area"]',
                            'span:has-text("m²")', 'span:has-text("τ.μ")'
                        ]
                        
                        for selector in sqm_selectors:
                            try:
                                sqm_element = await page.query_selector(selector)
                                if sqm_element:
                                    sqm_text = await sqm_element.inner_text()
                                    sqm_match = re.search(r'([0-9.,]+)\s*(?:m²|τ\.μ)', sqm_text)
                                    if sqm_match:
                                        sqm = float(sqm_match.group(1).replace(',', '.'))
                                        break
                            except:
                                continue
                        
                        # Extract energy class
                        energy_class = None
                        energy_selectors = [
                            '.energy-class', '[data-testid*="energy"]',
                            'span:has-text("Ενεργειακή")'
                        ]
                        
                        for selector in energy_selectors:
                            try:
                                energy_element = await page.query_selector(selector)
                                if energy_element:
                                    energy_text = await energy_element.inner_text()
                                    energy_match = re.search(r'([A-G][+]?)', energy_text)
                                    if energy_match:
                                        energy_class = energy_match.group(1)
                                        break
                            except:
                                continue
                        
                        # Create property data
                        property_data = {
                            "url": property_url,
                            "title": title,
                            "price": price,
                            "sqm": sqm,
                            "energy_class": energy_class,
                            "is_target_neighborhood": is_target_neighborhood,
                            "extracted_at": datetime.now().isoformat()
                        }
                        
                        extracted_properties.append(property_data)
                        
                        # Log extraction results
                        if price and sqm:
                            price_per_sqm = price / sqm
                            logger.info(f"✅ REAL DATA: €{price:,.0f}, {sqm}m², €{price_per_sqm:.0f}/m²")
                            
                            # Check for synthetic data patterns (from XE.gr analysis)
                            if price in [740, 3000] or sqm in [63, 270]:
                                logger.warning("⚠️ Potential synthetic data detected!")
                            else:
                                logger.info("🎉 AUTHENTIC REAL PROPERTY DATA!")
                        else:
                            logger.info(f"📊 Partial data: Price={price}, SQM={sqm}")
                        
                        # Random delay
                        await page.wait_for_timeout(2000)
                        
                    except Exception as e:
                        logger.error(f"❌ Error processing property {property_url}: {e}")
                
                # Delay between search pages
                await page.wait_for_timeout(3000)
                
            except Exception as e:
                logger.error(f"❌ Error processing search page {test_url}: {e}")
        
        await browser.close()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"outputs/spitogatos_focused_test_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_properties, f, indent=2, ensure_ascii=False)
    
    # Generate summary
    logger.info("📊 SPITOGATOS.GR FOCUSED TEST RESULTS")
    logger.info("=" * 50)
    logger.info(f"✅ Total properties tested: {len(extracted_properties)}")
    
    # Analyze data quality
    properties_with_price = [p for p in extracted_properties if p['price']]
    properties_with_sqm = [p for p in extracted_properties if p['sqm']]
    properties_with_energy = [p for p in extracted_properties if p['energy_class']]
    target_neighborhood_properties = [p for p in extracted_properties if p['is_target_neighborhood']]
    
    logger.info(f"💰 Properties with price: {len(properties_with_price)}")
    logger.info(f"📐 Properties with SQM: {len(properties_with_sqm)}")
    logger.info(f"⚡ Properties with energy class: {len(properties_with_energy)}")
    logger.info(f"🎯 Target neighborhood properties: {len(target_neighborhood_properties)}")
    
    if properties_with_price and properties_with_sqm:
        complete_properties = [p for p in extracted_properties if p['price'] and p['sqm']]
        avg_price = sum(p['price'] for p in complete_properties) / len(complete_properties)
        avg_sqm = sum(p['sqm'] for p in complete_properties) / len(complete_properties)
        avg_price_per_sqm = avg_price / avg_sqm
        
        logger.info(f"📈 Average price: €{avg_price:,.0f}")
        logger.info(f"📈 Average SQM: {avg_sqm:.0f}m²")
        logger.info(f"📈 Average price/m²: €{avg_price_per_sqm:.0f}")
    
    # Show sample properties
    if target_neighborhood_properties:
        logger.info("\n🎯 TARGET NEIGHBORHOOD PROPERTIES FOUND:")
        for prop in target_neighborhood_properties[:3]:
            logger.info(f"   • {prop['title']}")
            logger.info(f"     Price: €{prop['price']:,.0f}, SQM: {prop['sqm']}m²" if prop['price'] and prop['sqm'] else f"     Partial data")
    
    logger.info(f"\n📁 Results saved to: {output_file}")
    
    return extracted_properties

# Run focused test
if __name__ == "__main__":
    asyncio.run(extract_real_data_focused_test())