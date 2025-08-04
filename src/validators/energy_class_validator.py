#!/usr/bin/env python3
"""
ENERGY CLASS VALIDATION TEST
Quick test to validate enhanced energy class extraction
"""

import asyncio
import json
import logging
from datetime import datetime
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnergyClassValidator:
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    async def test_energy_extraction(self):
        """Test energy class extraction on specific properties"""
        logger.info("🔋 Testing enhanced energy class extraction...")
        
        # Test URLs with potential energy class data
        test_urls = [
            "https://www.spitogatos.gr/en/property/6385814",
            "https://www.spitogatos.gr/en/property/6385813", 
            "https://www.spitogatos.gr/en/property/6385812",
            "https://www.spitogatos.gr/en/search/results?category_selected=1&listing_type=1&sort_price=1&in_area_id=33&price_max=1000000",  # Athens search
        ]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            try:
                page = await context.new_page()
                results = []
                
                for url in test_urls:
                    logger.info(f"🧪 Testing: {url}")
                    
                    try:
                        response = await page.goto(url, wait_until="load", timeout=30000)
                        
                        if response and response.status == 200:
                            await asyncio.sleep(3)
                            
                            # Test our enhanced energy extraction
                            energy_result = await self.extract_energy_comprehensive(page, url)
                            results.append(energy_result)
                            
                            if energy_result['energy_class']:
                                logger.info(f"✅ Energy class found: {energy_result['energy_class']}")
                            else:
                                logger.info("❌ No energy class found")
                    
                    except Exception as e:
                        logger.error(f"❌ Test failed for {url}: {e}")
                        results.append({'url': url, 'error': str(e)})
                
                # Save results
                with open(f'outputs/energy_validation_{self.session_id}.json', 'w', encoding='utf-8') as f:
                    json.dump({
                        'test_timestamp': datetime.now().isoformat(),
                        'test_results': results
                    }, f, indent=2, ensure_ascii=False)
                
                logger.info(f"💾 Test results saved: outputs/energy_validation_{self.session_id}.json")
                
            finally:
                await browser.close()
    
    async def extract_energy_comprehensive(self, page, url: str) -> dict:
        """Comprehensive energy class extraction test"""
        import re
        
        result = {
            'url': url,
            'energy_class': None,
            'extraction_method': None,
            'page_title': None,
            'found_energy_keywords': [],
            'energy_context': []
        }
        
        try:
            # Get page info
            result['page_title'] = await page.title()
            page_content = await page.content()
            page_text = await page.inner_text('body')
            
            # Strategy 1: CSS selectors
            energy_selectors = [
                '.energy-class', '[data-testid*="energy"]',
                '.energy-rating', '.energy-efficiency', '.energy-certificate',
                'span:has-text("Ενεργειακή")', 'div:has-text("Ενεργειακή")',
                'span:has-text("Energy")', 'div:has-text("Energy")',
                '.property-energy', '.energy-info', '.certificate',
                '[class*="energy"]', '[id*="energy"]'
            ]
            
            for selector in energy_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        energy_text = await element.inner_text()
                        result['found_energy_keywords'].append(f"Selector {selector}: {energy_text}")
                        
                        energy_match = re.search(r'([A-G][+]?)', energy_text)
                        if energy_match:
                            result['energy_class'] = energy_match.group(1)
                            result['extraction_method'] = f"CSS selector: {selector}"
                            return result
                except:
                    continue
            
            # Strategy 2: Text pattern matching
            energy_patterns = [
                r'ενεργειακή\s+κλάση[:\s]*([A-G][+]?)',
                r'Ενεργειακή\s+κλάση[:\s]*([A-G][+]?)',
                r'ΕΝΕΡΓΕΙΑΚΗ\s+ΚΛΑΣΗ[:\s]*([A-G][+]?)',
                r'energy\s+class[:\s]*([A-G][+]?)',
                r'Energy\s+Class[:\s]*([A-G][+]?)',
                r'ENERGY\s+CLASS[:\s]*([A-G][+]?)',
                r'ενεργειακό\s+πιστοποιητικό[:\s]*([A-G][+]?)',
                r'κλάση\s+ενέργειας[:\s]*([A-G][+]?)',
                r'energy\s+rating[:\s]*([A-G][+]?)',
                r'energy\s+certificate[:\s]*([A-G][+]?)',
            ]
            
            full_text = page_content + " " + page_text
            
            for pattern in energy_patterns:
                matches = re.finditer(pattern, full_text, re.IGNORECASE)
                for match in matches:
                    potential_class = match.group(1).upper()
                    if potential_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                        result['energy_class'] = potential_class
                        result['extraction_method'] = f"Pattern: {pattern}"
                        result['energy_context'].append(match.group(0))
                        return result
            
            # Strategy 3: Look for any energy-related keywords
            energy_keywords = ['ενεργειακή', 'energy', 'ενεργειακό', 'certificate', 'πιστοποιητικό', 'κλάση']
            for keyword in energy_keywords:
                if keyword.lower() in page_text.lower():
                    # Find context around the keyword
                    pattern = rf'.{{0,50}}{re.escape(keyword)}.{{0,50}}'
                    matches = re.finditer(pattern, page_text, re.IGNORECASE)
                    for match in matches:
                        result['energy_context'].append(match.group(0))
            
            # Strategy 4: Check for property details sections
            details_selectors = [
                '.property-details', '.details', '.features', '.characteristics',
                '.property-info', '.listing-details', '.specs'
            ]
            
            for selector in details_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        text = await element.inner_text()
                        if any(keyword in text.lower() for keyword in ['energy', 'ενεργειακή']):
                            result['energy_context'].append(f"Details section: {text[:200]}...")
                            
                            # Look for energy class in this section
                            energy_match = re.search(r'([A-G][+]?)', text)
                            if energy_match:
                                potential_class = energy_match.group(1).upper()
                                if potential_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'G']:
                                    result['energy_class'] = potential_class
                                    result['extraction_method'] = f"Details section: {selector}"
                                    return result
                except:
                    continue
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result

async def main():
    validator = EnergyClassValidator()
    await validator.test_energy_extraction()

if __name__ == "__main__":
    asyncio.run(main())