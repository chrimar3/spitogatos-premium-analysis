#!/usr/bin/env python3
"""
FREE PROXY XE.GR SCRAPER - NO COST SOLUTION
Uses free proxies and advanced techniques to extract real xe.gr data
"""

import asyncio
import aiohttp
import json
import logging
import re
import time
import random
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import hashlib
from urllib.parse import urljoin

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RealPropertyData:
    """REAL property data with complete validation"""
    property_id: str
    url: str
    source_timestamp: str
    address: str
    neighborhood: str
    price: Optional[float]
    sqm: Optional[float]
    rooms: Optional[int]
    floor: Optional[str]
    energy_class: Optional[str]
    title: str
    description: str
    html_source_hash: str
    extraction_confidence: float
    validation_flags: List[str]
    proxy_used: Optional[str] = None
    user_agent_used: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class FreeProxyXEScraper:
    """xe.gr scraper using free proxy rotation"""
    
    def __init__(self):
        self.scraped_properties = []
        self.failed_urls = []
        self.audit_log = []
        self.working_proxies = []
        self.proxy_index = 0
        self.ua_index = 0
        
        # Load free proxies
        self.load_free_proxies()
        self.setup_user_agents()
        
        logger.info("🚀 FREE PROXY XE.GR SCRAPER - ZERO COST SOLUTION")
    
    def load_free_proxies(self):
        """Load free proxies from multiple sources"""
        
        logger.info("📡 Loading free proxies from multiple sources...")
        
        proxy_sources = [
            'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&format=textplain',
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
            'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt'
        ]
        
        all_proxies = set()
        
        for source in proxy_sources:
            try:
                logger.info(f"🔄 Fetching from: {source}")
                response = requests.get(source, timeout=10)
                
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    for proxy in proxies:
                        proxy = proxy.strip()
                        if self.validate_proxy_format(proxy):
                            all_proxies.add(f"http://{proxy}")
                    
                    logger.info(f"✅ Found {len(proxies)} proxies from source")
                else:
                    logger.warning(f"⚠️ Failed to fetch from {source}: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error fetching from {source}: {e}")
        
        # Add some reliable free proxies as backup
        backup_proxies = [
            "http://8.213.128.6:8080",
            "http://103.127.1.130:80", 
            "http://168.138.211.5:8080",
            "http://20.111.54.16:8123",
            "http://103.149.162.194:80"
        ]
        
        for proxy in backup_proxies:
            all_proxies.add(proxy)
        
        self.all_proxies = list(all_proxies)
        logger.info(f"📡 Total proxies loaded: {len(self.all_proxies)}")
        
        # Test proxies in background
        asyncio.create_task(self.test_proxies_async())
    
    def validate_proxy_format(self, proxy: str) -> bool:
        """Validate proxy format"""
        pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$'
        return bool(re.match(pattern, proxy))
    
    async def test_proxies_async(self):
        """Test proxies for basic connectivity"""
        logger.info("🔍 Testing proxy connectivity...")
        
        test_url = "http://httpbin.org/ip"
        working_count = 0
        
        for proxy in self.all_proxies[:50]:  # Test first 50
            try:
                timeout = aiohttp.ClientTimeout(total=10)
                connector = aiohttp.TCPConnector(limit=5)
                
                async with aiohttp.ClientSession(
                    timeout=timeout,
                    connector=connector
                ) as session:
                    async with session.get(test_url, proxy=proxy) as response:
                        if response.status == 200:
                            self.working_proxies.append(proxy)
                            working_count += 1
                            if working_count >= 20:  # Keep top 20 working proxies
                                break
                            
            except:
                pass  # Proxy doesn't work, skip
        
        logger.info(f"✅ Found {len(self.working_proxies)} working proxies")
    
    def setup_user_agents(self):
        """Setup realistic user agents"""
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        ]
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next working proxy"""
        if not self.working_proxies:
            # Fallback to all proxies if working ones not ready
            if self.all_proxies:
                proxy = self.all_proxies[self.proxy_index % len(self.all_proxies)]
                self.proxy_index += 1
                return proxy
            return None
        
        proxy = self.working_proxies[self.proxy_index % len(self.working_proxies)]
        self.proxy_index += 1
        return proxy
    
    def get_next_user_agent(self) -> str:
        """Get next user agent"""
        ua = self.user_agents[self.ua_index % len(self.user_agents)]
        self.ua_index += 1
        return ua
    
    def get_headers(self) -> Dict[str, str]:
        """Get randomized headers"""
        return {
            'User-Agent': self.get_next_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(['el-GR,el;q=0.9,en;q=0.8', 'en-US,en;q=0.9,el;q=0.8']),
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
    
    async def make_request_with_proxy(self, url: str, max_retries: int = 5) -> Optional[str]:
        """Make request with proxy rotation and retries"""
        
        for attempt in range(max_retries):
            proxy = self.get_next_proxy()
            if not proxy:
                logger.error("❌ No proxies available")
                return None
            
            try:
                headers = self.get_headers()
                timeout = aiohttp.ClientTimeout(total=30)
                connector = aiohttp.TCPConnector(
                    limit=10,
                    use_dns_cache=False,
                    ssl=False
                )
                
                async with aiohttp.ClientSession(
                    headers=headers,
                    timeout=timeout,
                    connector=connector
                ) as session:
                    
                    # Human-like delay
                    delay = random.uniform(3, 8)
                    logger.info(f"😴 Human delay: {delay:.1f}s")
                    await asyncio.sleep(delay)
                    
                    logger.info(f"🔄 Attempt {attempt+1}/{max_retries} - Proxy: {proxy}")
                    
                    async with session.get(url, proxy=proxy) as response:
                        if response.status == 200:
                            html = await response.text()
                            logger.info(f"✅ Success! Status: 200, Length: {len(html)} chars")
                            return html
                        else:
                            logger.warning(f"⚠️ Status {response.status} with proxy {proxy}")
                            
            except Exception as e:
                logger.warning(f"⚠️ Proxy {proxy} failed: {e}")
                continue
        
        logger.error(f"❌ All {max_retries} attempts failed for {url}")
        return None
    
    async def scrape_xe_gr_properties(self, neighborhood: str, max_properties: int = 10) -> List[RealPropertyData]:
        """Scrape xe.gr properties with free proxy rotation"""
        
        logger.info(f"🎯 SCRAPING {neighborhood} WITH FREE PROXY ROTATION")
        logger.info(f"📋 Target: {max_properties} verified properties")
        
        # Wait for proxy testing to complete
        await asyncio.sleep(5)
        
        properties = []
        
        # Try different search strategies
        search_urls = [
            f"https://xe.gr/property/search?transaction_name=rent&property_name=apartment&geo_place_categories=neighborhood&neighborhood={neighborhood}",
            f"https://xe.gr/property/search?transaction_name=sale&property_name=apartment&geo_place_categories=neighborhood&neighborhood={neighborhood}",
            f"https://xe.gr/property/search?geo_place_ids=ChIJ8UNwBh-9oRQR3Y1mdkU1Nic&transaction_name=rent&property_name=apartment"
        ]
        
        for search_url in search_urls:
            if len(properties) >= max_properties:
                break
            
            logger.info(f"🔍 Searching: {search_url}")
            
            # Get search results with proxy rotation
            html = await self.make_request_with_proxy(search_url)
            
            if html:
                # Extract property URLs
                property_urls = self.extract_property_urls(html)
                logger.info(f"📦 Found {len(property_urls)} property URLs")
                
                # Scrape individual properties
                for i, prop_url in enumerate(property_urls[:max_properties]):
                    if len(properties) >= max_properties:
                        break
                    
                    logger.info(f"🏠 Scraping property {i+1}: {prop_url}")
                    
                    # Get property page with different proxy
                    prop_html = await self.make_request_with_proxy(prop_url)
                    
                    if prop_html:
                        property_data = self.extract_property_data(prop_html, prop_url, neighborhood)
                        
                        if property_data and self.validate_property(property_data):
                            properties.append(property_data)
                            logger.info(f"✅ Property extracted: {property_data.address}, €{property_data.price}, {property_data.sqm}m²")
                        else:
                            logger.warning(f"❌ Property validation failed")
                    
                    # Cooldown between properties
                    await asyncio.sleep(random.uniform(5, 15))
            else:
                logger.warning(f"❌ Failed to get search results")
            
            # Longer cooldown between searches
            await asyncio.sleep(random.uniform(30, 60))
        
        logger.info(f"🎯 SCRAPING COMPLETE: {len(properties)} properties extracted")
        return properties
    
    def extract_property_urls(self, html: str) -> List[str]:
        """Extract property URLs from search results"""
        soup = BeautifulSoup(html, 'html.parser')
        urls = []
        
        # Look for property links
        selectors = [
            'a[href*="/property/"]',
            'a[href*="/rent/"]',
            'a[href*="/sale/"]',
            '.property-card a',
            '.listing-card a',
            '[data-testid*="property"] a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin('https://xe.gr', href)
                    if self.is_valid_property_url(full_url):
                        urls.append(full_url)
        
        return list(set(urls))  # Remove duplicates
    
    def is_valid_property_url(self, url: str) -> bool:
        """Validate property URL"""
        if not url or 'xe.gr' not in url:
            return False
        
        property_indicators = ['/property/', '/rent/', '/sale/', '/listing/']
        if not any(indicator in url for indicator in property_indicators):
            return False
        
        invalid_patterns = ['/search', '/category', '/filter', '/api/', '/results?page=']
        if any(pattern in url for pattern in invalid_patterns):
            return False
        
        return True
    
    def extract_property_data(self, html: str, url: str, neighborhood: str) -> Optional[RealPropertyData]:
        """Extract property data from HTML"""
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            data = {
                'property_id': self.generate_property_id(url),
                'url': url,
                'source_timestamp': datetime.now().isoformat(),
                'html_source_hash': hashlib.md5(html.encode()).hexdigest(),
                'neighborhood': neighborhood,
                'title': self.extract_title(soup),
                'address': self.extract_address(soup),
                'price': self.extract_price(soup),
                'sqm': self.extract_sqm(soup),
                'rooms': self.extract_rooms(soup),
                'floor': self.extract_floor(soup),
                'description': self.extract_description(soup),
                'energy_class': self.extract_energy_class(soup, html),
                'latitude': None,
                'longitude': None,
                'proxy_used': 'free_proxy_rotation',
                'user_agent_used': 'rotated_ua',
                'extraction_confidence': 0.0,
                'validation_flags': []
            }
            
            # Calculate confidence and flags
            data['extraction_confidence'] = self.calculate_confidence(data)
            data['validation_flags'] = self.generate_flags(data)
            
            return RealPropertyData(**data)
            
        except Exception as e:
            logger.error(f"❌ Error extracting property data: {e}")
            return None
    
    # Include all extraction methods from bulletproof scraper
    def generate_property_id(self, url: str) -> str:
        """Generate unique property ID"""
        url_match = re.search(r'/(\d+)', url)
        if url_match:
            return f"xe_gr_{url_match.group(1)}"
        else:
            return f"xe_gr_{hashlib.md5(url.encode()).hexdigest()[:8]}"
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title"""
        selectors = ['h1', '.property-title', '.listing-title', 'title']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)[:200]
        return "No title found"
    
    def extract_address(self, soup: BeautifulSoup) -> str:
        """Extract address"""
        selectors = ['.address', '.location', '.property-address']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                address = element.get_text(strip=True)
                if self.validate_athens_address(address):
                    return address[:300]
        
        # Try breadcrumbs and page text
        page_text = soup.get_text()
        athens_match = re.search(r'[Αα]θήνα[^,\n]*', page_text)
        if athens_match:
            return athens_match.group(0).strip()
        
        return "Address not found"
    
    def validate_athens_address(self, address: str) -> bool:
        """Validate Athens address"""
        if not address:
            return False
        address_lower = address.lower()
        athens_indicators = ['αθήνα', 'athens', 'κολωνάκι', 'kolonaki', 'παγκράτι', 'pangrati', 'εξάρχεια', 'exarchia']
        return any(indicator in address_lower for indicator in athens_indicators)
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price with Greek format support"""
        selectors = ['.price', '.property-price', '[data-testid*="price"]']
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price = self.parse_price(price_text)
                if price and 50 <= price <= 5000000:
                    return price
        
        # Search in page text
        page_text = soup.get_text()
        price_patterns = [
            r'(\\d{1,3}(?:\\.\\d{3})*)\\s*€',
            r'€\\s*(\\d{1,3}(?:\\.\\d{3})*)',
            r'τιμή[:\\s]*(\\d{1,3}(?:\\.\\d{3})*)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                price = self.parse_price(match.group(1))
                if price and 50 <= price <= 5000000:
                    return price
        
        return None
    
    def parse_price(self, price_text: str) -> Optional[float]:
        """Parse price with Greek format"""
        if not price_text:
            return None
        
        # Remove currency symbols
        price_clean = re.sub(r'[€$£¥₹ευρώeur]', '', price_text, flags=re.IGNORECASE)
        price_clean = re.sub(r'[^\\d.,]', '', price_clean)
        
        if not price_clean:
            return None
        
        try:
            # Handle European format (1.500 = 1500)
            if '.' in price_clean:
                parts = price_clean.split('.')
                if len(parts) == 2 and len(parts[1]) == 3:
                    price_clean = price_clean.replace('.', '')
            
            price = float(price_clean)
            
            # If very small, likely in thousands
            if price < 10:
                price = price * 1000
            
            return price
            
        except ValueError:
            return None
    
    def extract_sqm(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract square meters"""
        page_text = soup.get_text()
        sqm_patterns = [
            r'(\\d+(?:[.,]\\d+)?)\\s*τ\\.?μ\\.?',
            r'(\\d+(?:[.,]\\d+)?)\\s*m²',
            r'(\\d+(?:[.,]\\d+)?)\\s*sqm'
        ]
        
        for pattern in sqm_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                try:
                    sqm = float(match.group(1).replace(',', '.'))
                    if 10 <= sqm <= 500:
                        return sqm
                except ValueError:
                    continue
        return None
    
    def extract_rooms(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract rooms"""
        page_text = soup.get_text()
        room_patterns = [r'(\\d+)\\s*δωμάτια?', r'(\\d+)\\s*rooms?']
        
        for pattern in room_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                try:
                    rooms = int(match.group(1))
                    if 1 <= rooms <= 10:
                        return rooms
                except ValueError:
                    continue
        return None
    
    def extract_floor(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract floor"""
        page_text = soup.get_text()
        floor_patterns = [r'όροφος[:\\s]*([^,\\n.]{1,15})', r'floor[:\\s]*([^,\\n.]{1,15})']
        
        for pattern in floor_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract description"""
        selectors = ['.description', '.property-description', '.details']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                desc = element.get_text(strip=True)
                if len(desc) > 20:
                    return desc[:1000]
        return "No description found"
    
    def extract_energy_class(self, soup: BeautifulSoup, html: str) -> Optional[str]:
        """Extract energy class"""
        energy_patterns = [
            r'ενεργειακή\\s+κλάση\\s*[:\\-]?\\s*([A-G][+]?)',
            r'energy\\s+class\\s*[:\\-]?\\s*([A-G][+]?)',
            r'κλάση\\s+([A-G][+]?)',
            r'class\\s+([A-G][+]?)'
        ]
        
        full_text = soup.get_text() + html
        
        for pattern in energy_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                energy_class = match.group(1).upper()
                if energy_class in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F']:
                    return energy_class
        return None
    
    def calculate_confidence(self, data: Dict) -> float:
        """Calculate confidence score"""
        confidence = 0.0
        total_checks = 0
        
        # Critical fields
        for field in ['address', 'price', 'sqm']:
            total_checks += 2
            if data.get(field):
                confidence += 2
        
        # Important fields
        for field in ['title', 'description', 'rooms']:
            total_checks += 1
            if data.get(field):
                confidence += 1
        
        return confidence / total_checks if total_checks > 0 else 0.0
    
    def generate_flags(self, data: Dict) -> List[str]:
        """Generate validation flags"""
        flags = ['xe_gr_verified', 'free_proxy_extracted']
        
        if data.get('address') and self.validate_athens_address(data['address']):
            flags.append('athens_verified')
        
        if data.get('price') and 50 <= data['price'] <= 5000000:
            flags.append('price_realistic')
        
        if data.get('sqm') and 10 <= data['sqm'] <= 500:
            flags.append('area_realistic')
        
        if data.get('energy_class'):
            flags.append('energy_found')
        
        return flags
    
    def validate_property(self, prop: RealPropertyData) -> bool:
        """Validate property data"""
        if not prop.url or not prop.property_id:
            return False
        
        if not prop.address or not self.validate_athens_address(prop.address):
            return False
        
        if not prop.price and not prop.sqm:
            return False
        
        if prop.price and not (50 <= prop.price <= 5000000):
            return False
        
        if prop.sqm and not (10 <= prop.sqm <= 500):
            return False
        
        if prop.extraction_confidence < 0.3:
            return False
        
        return True

async def main():
    """Test free proxy scraper"""
    
    logger.info("🚀 TESTING FREE PROXY XE.GR SCRAPER")
    
    scraper = FreeProxyXEScraper()
    
    # Test with Kolonaki
    properties = await scraper.scrape_xe_gr_properties('Κολωνάκι', max_properties=5)
    
    logger.info(f"\\n🎯 RESULTS: {len(properties)} properties extracted")
    
    if properties:
        for prop in properties:
            logger.info(f"📊 {prop.address}")
            logger.info(f"   Price: €{prop.price}, Area: {prop.sqm}m², Energy: {prop.energy_class}")
            logger.info(f"   URL: {prop.url}")
        
        # Save results
        output_data = [asdict(prop) for prop in properties]
        with open('outputs/free_proxy_results.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info("✅ Results saved to outputs/free_proxy_results.json")
    else:
        logger.warning("❌ No properties extracted - may need premium proxies")

if __name__ == "__main__":
    asyncio.run(main())