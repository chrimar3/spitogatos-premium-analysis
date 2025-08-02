#!/usr/bin/env python3
"""
SPITOGATOS.GR RESEARCH INVESTIGATOR
Comprehensive analysis of site structure and data availability
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from playwright.async_api import async_playwright
import aiohttp

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpitogatosResearchInvestigator:
    """Research tool for analyzing Spitogatos.gr structure and capabilities"""
    
    def __init__(self):
        self.findings = {
            "timestamp": datetime.now().isoformat(),
            "website": "spitogatos.gr",
            "anti_bot_protection": {},
            "url_patterns": {},
            "search_functionality": {},
            "property_data_structure": {},
            "accessibility_analysis": {}
        }
        
        self.test_neighborhoods = [
            "Kolonaki", "Pangrati", "Κολωνάκι", "Παγκράτι"
        ]
        
        logger.info("🔍 SPITOGATOS.GR RESEARCH INVESTIGATOR INITIALIZED")
    
    async def test_basic_accessibility(self):
        """Test basic website accessibility and anti-bot measures"""
        
        logger.info("🌐 Testing basic accessibility...")
        
        test_urls = [
            "https://www.spitogatos.gr",
            "https://www.spitogatos.gr/en",
            "https://www.spitogatos.gr/search",
            "https://www.spitogatos.gr/for_sale-homes",
            "https://www.spitogatos.gr/for_rent-homes",
            "https://www.spitogatos.gr/en/for_sale-homes/athens-center"
        ]
        
        async with aiohttp.ClientSession() as session:
            for url in test_urls:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                    }
                    
                    async with session.get(url, headers=headers, timeout=30) as response:
                        content = await response.text()
                        
                        self.findings["accessibility_analysis"][url] = {
                            "status": response.status,
                            "headers": dict(response.headers),
                            "anti_bot_detected": "Pardon Our Interruption" in content,
                            "javascript_required": "noscript" in content.lower(),
                            "cloudflare_protection": "cloudflare" in content.lower(),
                            "content_size": len(content)
                        }
                        
                        logger.info(f"✅ {url}: Status {response.status}, Anti-bot: {'Yes' if 'Pardon Our Interruption' in content else 'No'}")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to access {url}: {e}")
                    self.findings["accessibility_analysis"][url] = {"error": str(e)}
    
    async def investigate_with_playwright(self):
        """Deep investigation using Playwright browser automation"""
        
        logger.info("🎭 Starting Playwright investigation...")
        
        async with async_playwright() as p:
            # Launch browser with stealth settings
            browser = await p.chromium.launch(
                headless=False,  # Visible for investigation
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-web-security'
                ]
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                locale='el-GR',
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Add stealth script
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = {runtime: {}};
            """)
            
            page = await context.new_page()
            
            # Test homepage
            await self.test_homepage(page)
            
            # Test search functionality
            await self.test_search_functionality(page)
            
            # Test property page structure
            await self.test_property_page_structure(page)
            
            await browser.close()
    
    async def test_homepage(self, page):
        """Analyze homepage structure and functionality"""
        
        logger.info("🏠 Testing homepage...")
        
        try:
            await page.goto("https://www.spitogatos.gr", wait_until='networkidle')
            
            # Take screenshot
            await page.screenshot(path="outputs/spitogatos_homepage_investigation.png")
            
            # Check for anti-bot protection
            content = await page.content()
            self.findings["anti_bot_protection"]["homepage"] = {
                "pardon_interruption": "Pardon Our Interruption" in content,
                "javascript_challenge": "challenge" in content.lower(),
                "cookie_requirements": "cookie" in content.lower()
            }
            
            # Analyze page structure
            title = await page.title()
            
            # Look for search forms
            search_forms = await page.query_selector_all('form, .search-form, [data-testid*="search"]')
            
            # Look for navigation links
            nav_links = await page.query_selector_all('nav a, .nav a, .menu a')
            
            self.findings["homepage_analysis"] = {
                "title": title,
                "search_forms_found": len(search_forms),
                "navigation_links": len(nav_links),
                "anti_bot_status": self.findings["anti_bot_protection"]["homepage"]
            }
            
            logger.info(f"✅ Homepage analysis: {title}, {len(search_forms)} search forms, Anti-bot: {self.findings['anti_bot_protection']['homepage']['pardon_interruption']}")
            
        except Exception as e:
            logger.error(f"❌ Homepage test failed: {e}")
            self.findings["homepage_analysis"] = {"error": str(e)}
    
    async def test_search_functionality(self, page):
        """Test search functionality for Athens neighborhoods"""
        
        logger.info("🔍 Testing search functionality...")
        
        search_strategies = [
            ("Direct URL", "https://www.spitogatos.gr/search?location=Athens"),
            ("Sale Properties", "https://www.spitogatos.gr/for_sale-homes"),
            ("Rent Properties", "https://www.spitogatos.gr/for_rent-homes"),
            ("English Version", "https://www.spitogatos.gr/en"),
            ("Athens Center", "https://www.spitogatos.gr/en/for_sale-homes/athens-center")
        ]
        
        for strategy_name, url in search_strategies:
            try:
                logger.info(f"Testing strategy: {strategy_name}")
                
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Take screenshot
                timestamp = datetime.now().strftime("%H%M%S")
                await page.screenshot(path=f"outputs/spitogatos_{strategy_name.lower().replace(' ', '_')}_{timestamp}.png")
                
                # Check if page loaded successfully
                content = await page.content()
                title = await page.title()
                
                # Look for property listings
                property_elements = await page.query_selector_all(
                    '.property, .listing, .property-card, [data-testid*="property"]'
                )
                
                # Look for property links
                property_links = await page.query_selector_all(
                    'a[href*="/property"], a[href*="/listing"], a[href*="/ad"]'
                )
                
                self.findings["search_functionality"][strategy_name] = {
                    "url": url,
                    "success": "Pardon Our Interruption" not in content,
                    "title": title,
                    "property_elements_found": len(property_elements),
                    "property_links_found": len(property_links),
                    "contains_listings": len(property_elements) > 0 or len(property_links) > 0
                }
                
                logger.info(f"✅ {strategy_name}: {'Success' if self.findings['search_functionality'][strategy_name]['success'] else 'Blocked'}, {len(property_elements)} properties, {len(property_links)} links")
                
                # If successful and found properties, extract sample URLs
                if self.findings["search_functionality"][strategy_name]["success"] and property_links:
                    sample_urls = []
                    for link in property_links[:5]:  # First 5 links
                        href = await link.get_attribute('href')
                        if href:
                            if href.startswith('/'):
                                href = f"https://www.spitogatos.gr{href}"
                            sample_urls.append(href)
                    
                    self.findings["search_functionality"][strategy_name]["sample_property_urls"] = sample_urls
                
                # Wait between requests
                await page.wait_for_timeout(3000)
                
            except Exception as e:
                logger.error(f"❌ {strategy_name} failed: {e}")
                self.findings["search_functionality"][strategy_name] = {"error": str(e)}
    
    async def test_property_page_structure(self, page):
        """Test individual property page structure"""
        
        logger.info("🏘️ Testing property page structure...")
        
        # Test with known property URL patterns
        test_property_urls = [
            "https://www.spitogatos.gr/en/properties/1234567",  # Generic pattern
            "https://www.spitogatos.gr/property/1234567",       # Alternative pattern
            "https://www.spitogatos.gr/listing/1234567",        # Another pattern
        ]
        
        # Also try to find real property URLs from search results
        try:
            await page.goto("https://www.spitogatos.gr/en/for_sale-homes/athens-center", timeout=30000)
            
            # Look for actual property links
            property_links = await page.query_selector_all('a[href*="/properties/"], a[href*="/property/"]')
            
            if property_links:
                # Test first real property URL found
                first_link = property_links[0]
                href = await first_link.get_attribute('href')
                if href:
                    if href.startswith('/'):
                        href = f"https://www.spitogatos.gr{href}"
                    test_property_urls.insert(0, href)  # Test real URL first
            
        except Exception as e:
            logger.warning(f"Could not find real property URLs: {e}")
        
        for test_url in test_property_urls[:2]:  # Test first 2 URLs
            try:
                logger.info(f"Testing property URL: {test_url}")
                
                await page.goto(test_url, wait_until='networkidle', timeout=30000)
                
                content = await page.content()
                title = await page.title()
                
                # Take screenshot
                timestamp = datetime.now().strftime("%H%M%S")
                await page.screenshot(path=f"outputs/spitogatos_property_{timestamp}.png")
                
                # Analyze property page structure
                price_elements = await page.query_selector_all('.price, [data-testid*="price"], .property-price')
                sqm_elements = await page.query_selector_all('.sqm, [data-testid*="area"], .area, .square-meters')
                energy_elements = await page.query_selector_all('.energy, [data-testid*="energy"], .energy-class')
                contact_elements = await page.query_selector_all('.contact, .phone, .agent-contact')
                
                self.findings["property_data_structure"][test_url] = {
                    "accessible": "404" not in title and "Pardon Our Interruption" not in content,
                    "title": title,
                    "price_elements": len(price_elements),
                    "sqm_elements": len(sqm_elements),
                    "energy_elements": len(energy_elements),
                    "contact_elements": len(contact_elements),
                    "has_property_data": len(price_elements) > 0 or len(sqm_elements) > 0
                }
                
                logger.info(f"✅ Property page test: {'Accessible' if self.findings['property_data_structure'][test_url]['accessible'] else 'Blocked'}")
                
                # If we found a working property page, break
                if self.findings["property_data_structure"][test_url]["accessible"]:
                    break
                
            except Exception as e:
                logger.error(f"❌ Property page test failed for {test_url}: {e}")
                self.findings["property_data_structure"][test_url] = {"error": str(e)}
    
    def save_findings(self):
        """Save investigation findings to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"outputs/spitogatos_investigation_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.findings, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Investigation results saved to: {output_file}")
        return output_file
    
    def generate_summary_report(self):
        """Generate human-readable summary report"""
        
        logger.info("📋 SPITOGATOS.GR INVESTIGATION SUMMARY")
        logger.info("=" * 50)
        
        # Anti-bot protection analysis
        anti_bot_detected = any(
            analysis.get("anti_bot_detected", False) 
            for analysis in self.findings.get("accessibility_analysis", {}).values()
            if isinstance(analysis, dict)
        )
        
        logger.info(f"🛡️ Anti-bot protection: {'DETECTED' if anti_bot_detected else 'MINIMAL'}")
        
        # Search functionality analysis
        successful_searches = sum(
            1 for strategy in self.findings.get("search_functionality", {}).values()
            if isinstance(strategy, dict) and strategy.get("success", False)
        )
        
        total_searches = len(self.findings.get("search_functionality", {}))
        
        logger.info(f"🔍 Search functionality: {successful_searches}/{total_searches} strategies successful")
        
        # Property data availability
        accessible_properties = sum(
            1 for prop in self.findings.get("property_data_structure", {}).values()
            if isinstance(prop, dict) and prop.get("accessible", False)
        )
        
        total_property_tests = len(self.findings.get("property_data_structure", {}))
        
        logger.info(f"🏠 Property pages: {accessible_properties}/{total_property_tests} accessible")
        
        # Data extraction potential
        properties_with_data = sum(
            1 for prop in self.findings.get("property_data_structure", {}).values()
            if isinstance(prop, dict) and prop.get("has_property_data", False)
        )
        
        logger.info(f"📊 Data extraction potential: {properties_with_data}/{total_property_tests} pages have property data")
        
        # Recommendations
        logger.info("\n💡 RECOMMENDATIONS:")
        
        if anti_bot_detected:
            logger.info("   • Use advanced browser automation with stealth techniques")
            logger.info("   • Implement random delays and human-like behavior")
            logger.info("   • Consider rotating IP addresses/proxies")
        
        if successful_searches > 0:
            logger.info("   • Search functionality is partially accessible")
            logger.info("   • Focus on successful search strategies")
        
        if accessible_properties > 0:
            logger.info("   • Individual property pages can be accessed")
            logger.info("   • Property data extraction is feasible")
        else:
            logger.info("   • Property pages may require special handling")
            logger.info("   • Consider alternative data discovery methods")

# Main execution
async def main():
    """Main investigation execution"""
    
    investigator = SpitogatosResearchInvestigator()
    
    # Create outputs directory
    Path("outputs").mkdir(exist_ok=True)
    
    # Run comprehensive investigation
    await investigator.test_basic_accessibility()
    await investigator.investigate_with_playwright()
    
    # Save findings and generate report
    output_file = investigator.save_findings()
    investigator.generate_summary_report()
    
    logger.info(f"🎯 Investigation completed! Results saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())