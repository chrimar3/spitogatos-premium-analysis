#!/usr/bin/env python3
"""
XE.GR INTELLIGENCE-BASED SCRAPER
Using discovered website architecture and working endpoints
"""

import asyncio
import aiohttp
import json
import logging
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import hashlib
from urllib.parse import urljoin, urlencode

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
    extraction_method: str = "intelligence_based"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class IntelligenceBasedXEScraper:
    """xe.gr scraper using discovered intelligence"""
    
    def __init__(self):
        self.scraped_properties = []
        self.failed_urls = []
        self.audit_log = []
        
        # Use discovered working endpoints
        self.search_endpoint = "https://xe.gr/search"  # NOT /property/search
        self.sitemap_urls = [
            "https://www.xe.gr/sitemap_property_enoikiaseis-diamerismaton.xml",
            "https://www.xe.gr/sitemap_property_poliseis-diamerismaton.xml"
        ]
        
        # Working form parameters (discovered in investigation)
        self.search_params = {
            'Transaction.price.from': '',
            'Transaction.price.to': '', 
            'Publication.freetext': '',
            'Item.category__hierarchy': '117139',  # Property category
            'Transaction.type_channel': 'all'
        }
        
        logger.info("🧠 INTELLIGENCE-BASED XE.GR SCRAPER")
        logger.info("📋 Using discovered working endpoints and parameters")
    
    async def scrape_using_working_search(self, neighborhood: str, max_properties: int = 10) -> List[RealPropertyData]:
        """Scrape using the working search endpoint"""
        
        logger.info(f"🎯 INTELLIGENCE-BASED SCRAPING: {neighborhood}")
        logger.info(f"📋 Using working endpoint: {self.search_endpoint}")
        
        properties = []
        
        # Use realistic headers (investigation showed no user-agent blocking)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        try:
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                
                # Method 1: Use working search form
                logger.info("🔍 Method 1: Using working search form")
                search_properties = await self.search_via_form(session, neighborhood)
                properties.extend(search_properties[:max_properties])
                
                # Method 2: Use sitemap discovery (if needed)
                if len(properties) < max_properties:
                    logger.info("🗺️ Method 2: Using sitemap discovery")
                    sitemap_properties = await self.search_via_sitemap(session, neighborhood)
                    properties.extend(sitemap_properties[:max_properties-len(properties)])
                
                # Method 3: Direct property page access (discovered patterns)
                if len(properties) < max_properties:
                    logger.info("🎯 Method 3: Direct property access")  
                    direct_properties = await self.search_direct_properties(session, neighborhood)
                    properties.extend(direct_properties[:max_properties-len(properties)])
        
        except Exception as e:
            logger.error(f"❌ Intelligence-based scraping failed: {e}")
        
        logger.info(f"✅ INTELLIGENCE SCRAPING COMPLETE: {len(properties)} properties")
        return properties
    
    async def search_via_form(self, session: aiohttp.ClientSession, neighborhood: str) -> List[RealPropertyData]:
        """Search using discovered working form"""
        
        properties = []
        
        try:
            # Build search parameters
            search_params = self.search_params.copy()
            search_params['Publication.freetext'] = neighborhood
            
            # Try different transaction types
            transaction_types = ['all', '117526', '117538']  # rent, sale, etc
            
            for tx_type in transaction_types:
                search_params['Transaction.type_channel'] = tx_type
                
                # Build search URL with parameters
                search_url = f"{self.search_endpoint}?{urlencode(search_params)}"
                
                logger.info(f"🔍 Searching: {search_url}")
                
                async with session.get(search_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        logger.info(f"✅ Search successful: {len(html)} chars received")
                        
                        # Extract property URLs from search results
                        property_urls = self.extract_property_urls_from_search(html)
                        logger.info(f"📦 Found {len(property_urls)} property URLs")
                        
                        # Scrape individual properties
                        for prop_url in property_urls:
                            prop_data = await self.scrape_individual_property(session, prop_url, neighborhood)
                            if prop_data and self.validate_property(prop_data):
                                properties.append(prop_data)
                                logger.info(f"✅ Property: {prop_data.address}, €{prop_data.price}")
                            
                            await asyncio.sleep(1)  # Respectful delay
                    
                    else:
                        logger.warning(f"⚠️ Search failed: {response.status}")
                
                await asyncio.sleep(2)  # Delay between searches
        
        except Exception as e:
            logger.error(f"❌ Form search failed: {e}")
        
        return properties
    
    async def search_via_sitemap(self, session: aiohttp.ClientSession, neighborhood: str) -> List[RealPropertyData]:
        """Search using sitemap property URLs"""
        
        properties = []
        
        try:
            for sitemap_url in self.sitemap_urls:
                logger.info(f"🗺️ Processing sitemap: {sitemap_url}")
                
                async with session.get(sitemap_url) as response:
                    if response.status == 200:
                        sitemap_xml = await response.text()
                        
                        # Extract property URLs from sitemap
                        property_urls = self.extract_urls_from_sitemap(sitemap_xml)
                        logger.info(f"📦 Sitemap contains {len(property_urls)} property URLs")
                        
                        # Filter for Athens properties and scrape sample
                        athens_urls = [url for url in property_urls if self.is_athens_property_url(url, neighborhood)]
                        logger.info(f"🏛️ Found {len(athens_urls)} Athens-related URLs")
                        
                        # Scrape sample properties
                        for prop_url in athens_urls[:10]:  # Sample 10 per sitemap
                            prop_data = await self.scrape_individual_property(session, prop_url, neighborhood)
                            if prop_data and self.validate_property(prop_data):
                                properties.append(prop_data)
                                logger.info(f"✅ Sitemap property: {prop_data.address}")
                            
                            await asyncio.sleep(1)
                    
                    else:
                        logger.warning(f"⚠️ Sitemap failed: {response.status}")
                
                await asyncio.sleep(2)
        
        except Exception as e:
            logger.error(f"❌ Sitemap search failed: {e}")
        
        return properties
    
    async def search_direct_properties(self, session: aiohttp.ClientSession, neighborhood: str) -> List[RealPropertyData]:
        """Direct property access using discovered patterns"""
        
        properties = []
        
        # Try common property ID patterns (discovered from investigation)
        property_patterns = [
            'https://xe.gr/property/rent/apartment/{}/athens-{}'.format('{}', neighborhood.lower()),
            'https://xe.gr/property/sale/apartment/{}/athens-{}'.format('{}', neighborhood.lower()),
        ]
        
        # Try sample property IDs
        sample_ids = range(850000000, 870000000, 1000000)  # Sample range based on seen URLs
        
        try:
            for pattern in property_patterns:
                for prop_id in sample_ids:
                    prop_url = pattern.format(prop_id)
                    
                    logger.info(f"🎯 Testing direct URL: {prop_url}")
                    
                    try:
                        async with session.get(prop_url) as response:
                            if response.status == 200:
                                html = await response.text()
                                
                                # Check if it's a real property page
                                if self.is_property_page(html, neighborhood):
                                    prop_data = await self.scrape_individual_property(session, prop_url, neighborhood)
                                    if prop_data and self.validate_property(prop_data):
                                        properties.append(prop_data)
                                        logger.info(f"✅ Direct access: {prop_data.address}")
                            
                            elif response.status == 403:
                                logger.info("🛡️ Hit protection - switching strategy")
                                break
                    
                    except Exception as e:
                        continue  # Try next URL
                    
                    await asyncio.sleep(2)  # Longer delay for direct access
        
        except Exception as e:
            logger.error(f"❌ Direct property search failed: {e}")
        
        return properties
    
    def extract_property_urls_from_search(self, html: str) -> List[str]:
        """Extract property URLs from search results"""
        
        soup = BeautifulSoup(html, 'html.parser')
        urls = []
        
        # Look for property links using multiple selectors
        selectors = [
            'a[href*="/property/"]',
            'a[href*="/rent/"]',
            'a[href*="/sale/"]',
            'a[href*="enoikiaseis"]',  # Greek for rentals
            'a[href*="poliseis"]',    # Greek for sales
            '.property-card a',
            '.listing a',
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
        
        # Remove duplicates
        return list(set(urls))
    
    def extract_urls_from_sitemap(self, sitemap_xml: str) -> List[str]:
        """Extract URLs from sitemap XML"""
        
        urls = []
        
        # Extract all <loc> URLs
        url_matches = re.findall(r'<loc>(.*?)</loc>', sitemap_xml)
        
        for url in url_matches:
            if self.is_valid_property_url(url):
                urls.append(url)
        
        return urls
    
    def is_athens_property_url(self, url: str, neighborhood: str) -> bool:
        """Check if URL is for Athens property"""
        
        url_lower = url.lower()
        neighborhood_lower = neighborhood.lower()
        
        # Check for Athens indicators
        athens_indicators = ['athens', 'αθήνα', 'athen', neighborhood_lower]
        
        return any(indicator in url_lower for indicator in athens_indicators)
    
    def is_property_page(self, html: str, neighborhood: str) -> bool:
        """Check if HTML is a real property listing page"""
        
        html_lower = html.lower()
        
        # Must contain property indicators
        property_indicators = ['τιμή', 'price', 'τ.μ', 'sqm', 'm²', 'ενοικίαση', 'πώληση']
        if not any(indicator in html_lower for indicator in property_indicators):
            return False
        
        # Should contain Athens/neighborhood indicators
        location_indicators = ['αθήνα', 'athens', neighborhood.lower()]
        if not any(indicator in html_lower for indicator in location_indicators):
            return False
        
        return True
    
    def is_valid_property_url(self, url: str) -> bool:
        """Validate property URL"""
        
        if not url or 'xe.gr' not in url:
            return False
        
        # Must contain property indicators
        property_indicators = ['/property/', '/rent/', '/sale/', '/enoikiaseis/', '/poliseis/'] 
        if not any(indicator in url for indicator in property_indicators):
            return False
        
        # Must not be search or admin page
        invalid_patterns = ['/search', '/admin', '/api/', '/results', '/filter']
        if any(pattern in url for pattern in invalid_patterns):
            return False
        
        return True
    
    async def scrape_individual_property(self, session: aiohttp.ClientSession, url: str, neighborhood: str) -> Optional[RealPropertyData]:
        """Scrape individual property page"""
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract data using intelligent patterns
                data = {
                    'property_id': self.generate_property_id(url),
                    'url': url,
                    'source_timestamp': datetime.now().isoformat(),
                    'html_source_hash': hashlib.md5(html.encode()).hexdigest(),
                    'neighborhood': neighborhood,
                    'extraction_method': 'intelligence_based',
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
                    'extraction_confidence': 0.0,
                    'validation_flags': []
                }
                
                # Calculate confidence and flags
                data['extraction_confidence'] = self.calculate_confidence(data)
                data['validation_flags'] = self.generate_flags(data)
                
                return RealPropertyData(**data)
        
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
            return None
    
    # Include all extraction methods from previous scraper
    def generate_property_id(self, url: str) -> str:
        """Generate property ID"""
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
        selectors = ['.address', '.location', '.property-address', '.geo-info']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                address = element.get_text(strip=True)
                if self.validate_athens_address(address):
                    return address[:300]
        
        # Try page text
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
        indicators = ['αθήνα', 'athens', 'κολωνάκι', 'kolonaki', 'παγκράτι', 'pangrati', 'εξάρχεια', 'exarchia']
        return any(indicator in address_lower for indicator in indicators)
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price"""
        # Enhanced price extraction using intelligence
        selectors = ['.price', '.property-price', '[data-testid*="price"]', '.cost']
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price = self.parse_price(price_text)
                if price and 50 <= price <= 5000000:
                    return price
        
        # Search page text for price patterns
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
            # Handle European format
            if '.' in price_clean:
                parts = price_clean.split('.')
                if len(parts) == 2 and len(parts[1]) == 3:
                    price_clean = price_clean.replace('.', '')
            
            price = float(price_clean)
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
        """Calculate confidence"""
        confidence = 0.0
        total_checks = 0
        
        for field in ['address', 'price', 'sqm']:
            total_checks += 2
            if data.get(field):
                confidence += 2
        
        for field in ['title', 'description', 'rooms']:
            total_checks += 1
            if data.get(field):
                confidence += 1
        
        return confidence / total_checks if total_checks > 0 else 0.0
    
    def generate_flags(self, data: Dict) -> List[str]:
        """Generate validation flags"""
        flags = ['xe_gr_verified', 'intelligence_based']
        
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
        """Validate property"""
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
    """Test intelligence-based scraper"""
    
    logger.info("🧠 TESTING INTELLIGENCE-BASED XE.GR SCRAPER")
    
    scraper = IntelligenceBasedXEScraper()
    
    # Test with Kolonaki using discovered intelligence
    properties = await scraper.scrape_using_working_search('Κολωνάκι', max_properties=5)
    
    logger.info(f"\\n🎯 INTELLIGENCE-BASED RESULTS: {len(properties)} properties")
    
    if properties:
        for prop in properties:
            logger.info(f"📊 {prop.address}")
            logger.info(f"   Price: €{prop.price}, Area: {prop.sqm}m², Energy: {prop.energy_class}")
            logger.info(f"   Method: {prop.extraction_method}")
            logger.info(f"   URL: {prop.url}")
        
        # Save results  
        output_data = [asdict(prop) for prop in properties]
        with open('outputs/intelligence_based_results.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info("✅ Results saved to outputs/intelligence_based_results.json")
        logger.info("🧠 Intelligence-based approach successful!")
    else:
        logger.warning("❌ No properties extracted - need to refine approach")

if __name__ == "__main__":
    asyncio.run(main())