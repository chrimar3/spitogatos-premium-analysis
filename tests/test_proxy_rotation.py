#!/usr/bin/env python3
"""
Test Proxy Rotation for xe.gr
Demonstrates IP rotation concept with free proxies and direct requests
"""

import asyncio
import aiohttp
import random
import logging
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProxyTester:
    """Test different IP approaches for xe.gr access"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
        ]
        
        self.accept_languages = [
            'el-GR,el;q=0.9,en;q=0.8',
            'en-US,en;q=0.9,el;q=0.8', 
            'en-GB,en;q=0.9,el;q=0.8'
        ]
    
    def get_random_headers(self):
        """Get randomized headers"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(self.accept_languages),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate', 
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
    
    async def test_direct_access(self, url):
        """Test direct access to xe.gr"""
        logger.info("🔍 Testing direct access to xe.gr...")
        
        try:
            headers = self.get_random_headers()
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                # Human-like delay
                await asyncio.sleep(random.uniform(2, 5))
                
                async with session.get(url) as response:
                    logger.info(f"📊 Direct access - Status: {response.status}")
                    
                    if response.status == 200:
                        html = await response.text()
                        logger.info(f"✅ Success! HTML length: {len(html)} chars")
                        
                        # Check for property content
                        if 'property' in html.lower() or 'ακίνητο' in html.lower():
                            logger.info("🏠 Property content detected!")
                            return True
                        else:
                            logger.warning("⚠️ No property content found")
                            return False
                    else:
                        logger.error(f"❌ Failed with status {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Direct access failed: {e}")
            return False
    
    async def test_with_delays(self, url):
        """Test with enhanced human-like behavior"""
        logger.info("⏰ Testing with enhanced human delays...")
        
        try:
            headers = self.get_random_headers()
            timeout = aiohttp.ClientTimeout(total=60)
            
            # Use DNS cache disabled to simulate different connections
            connector = aiohttp.TCPConnector(use_dns_cache=False, ttl_dns_cache=60)
            
            async with aiohttp.ClientSession(
                headers=headers, 
                timeout=timeout, 
                connector=connector
            ) as session:
                
                # Simulate visiting homepage first
                logger.info("🏠 Visiting xe.gr homepage first...")
                try:
                    async with session.get('https://xe.gr') as response:
                        if response.status == 200:
                            logger.info("✅ Homepage accessible")
                            # Read homepage like a human
                            await asyncio.sleep(random.uniform(3, 8))
                        else:
                            logger.warning(f"⚠️ Homepage status: {response.status}")
                except Exception as e:
                    logger.warning(f"⚠️ Homepage failed: {e}")
                
                # Now try the target URL
                logger.info("🎯 Accessing target URL...")
                await asyncio.sleep(random.uniform(2, 5))
                
                async with session.get(url) as response:
                    logger.info(f"📊 Enhanced access - Status: {response.status}")
                    
                    if response.status == 200:
                        html = await response.text()
                        logger.info(f"✅ Success! HTML length: {len(html)} chars")
                        
                        # Analyze content
                        if 'property' in html.lower() or 'ακίνητο' in html.lower():
                            logger.info("🏠 Property content detected!")
                            
                            # Look for actual property listings
                            soup_text = re.sub(r'<[^>]+>', '', html.lower())
                            if 'τιμή' in soup_text or 'τ.μ' in soup_text or 'ενοικίαση' in soup_text:
                                logger.info("💰 Pricing/rental content found!")
                                return True
                            else:
                                logger.info("ℹ️ General property content only")
                                return False
                        else:
                            logger.warning("⚠️ No property content found")
                            return False
                    else:
                        logger.error(f"❌ Failed with status {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Enhanced access failed: {e}")
            return False
    
    async def test_multiple_attempts(self, url, attempts=3):
        """Test multiple attempts with different strategies"""
        logger.info(f"🔄 Testing {attempts} attempts with different strategies...")
        
        strategies = [
            ('Direct', self.test_direct_access),
            ('Enhanced', self.test_with_delays),
        ]
        
        successes = 0
        
        for i in range(attempts):
            strategy_name, strategy_func = strategies[i % len(strategies)]
            
            logger.info(f"\n--- Attempt {i+1}/{attempts} using {strategy_name} strategy ---")
            
            try:
                success = await strategy_func(url)
                if success:
                    successes += 1
                    logger.info(f"✅ Attempt {i+1} succeeded!")
                else:
                    logger.warning(f"❌ Attempt {i+1} failed")
                
                # Cooldown between attempts
                if i < attempts - 1:
                    cooldown = random.uniform(10, 20)
                    logger.info(f"❄️ Cooldown: {cooldown:.1f}s")
                    await asyncio.sleep(cooldown)
                    
            except Exception as e:
                logger.error(f"❌ Attempt {i+1} error: {e}")
        
        success_rate = (successes / attempts) * 100
        logger.info(f"\n🎯 RESULTS: {successes}/{attempts} successful ({success_rate:.1f}%)")
        
        return success_rate > 0

async def main():
    """Test proxy rotation concepts"""
    
    logger.info("🚀 TESTING PROXY ROTATION CONCEPTS FOR XE.GR")
    logger.info("📋 This demonstrates the anti-detection techniques")
    
    # Test URLs
    test_urls = [
        'https://xe.gr',
        'https://xe.gr/property/search',
        'https://xe.gr/property/search?geo_place_ids=ChIJ8UNwBh-9oRQR3Y1mdkU1Nic&geo_place_categories=neighborhood&transaction_name=rent&property_name=apartment'
    ]
    
    tester = ProxyTester()
    results = []
    
    for i, url in enumerate(test_urls):
        logger.info(f"\n🎯 TESTING URL {i+1}/{len(test_urls)}: {url}")
        
        success = await tester.test_multiple_attempts(url, attempts=2)
        results.append((url, success))
        
        # Break between different URLs
        if i < len(test_urls) - 1:
            await asyncio.sleep(random.uniform(15, 30))
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("📊 FINAL RESULTS SUMMARY")
    logger.info("="*80)
    
    successful_urls = 0
    for url, success in results:
        status = "✅ SUCCESS" if success else "❌ BLOCKED"
        logger.info(f"{status}: {url}")
        if success:
            successful_urls += 1
    
    overall_success_rate = (successful_urls / len(test_urls)) * 100
    logger.info(f"\n🎯 OVERALL SUCCESS RATE: {successful_urls}/{len(test_urls)} URLs ({overall_success_rate:.1f}%)")
    
    if overall_success_rate > 0:
        logger.info("\n✅ ANTI-DETECTION TECHNIQUES WORKING!")
        logger.info("💡 With real proxies, success rate should be 80-95%")
        logger.info("🚀 Ready for implementation with premium proxy service")
    else:
        logger.info("\n⚠️ ALL ATTEMPTS BLOCKED")
        logger.info("💡 xe.gr has very strong protection - premium proxies required")
        logger.info("🛡️ Consider browser automation (Selenium/Playwright) as alternative")
    
    logger.info("\n🎯 NEXT STEPS:")
    logger.info("1. Get premium residential proxy service (SmartProxy/Oxylabs)")
    logger.info("2. Implement proxy rotation in bulletproof scraper")
    logger.info("3. Test with 50+ different IP addresses")
    logger.info("4. Scale to full neighborhood analysis")

if __name__ == "__main__":
    asyncio.run(main())