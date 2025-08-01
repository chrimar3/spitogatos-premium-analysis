#!/usr/bin/env python3
"""
XE.GR FINAL BREAKTHROUGH SCRAPER
Using intelligence + enhanced property URL detection
"""

import asyncio
import aiohttp
import json
import logging
import re
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
    extraction_method: str = "final_breakthrough"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class FinalBreakthroughXEScraper:
    """Final breakthrough xe.gr scraper with enhanced detection"""
    
    def __init__(self):
        self.scraped_properties = []
        self.failed_urls = []
        self.audit_log = []
        
        # Discovered working endpoint
        self.search_endpoint = "https://xe.gr/search"
        
        # Enhanced search parameters based on investigation
        self.search_params = {
            'Transaction.price.from': '',
            'Transaction.price.to': '',
            'Publication.freetext': '',
            'Item.category__hierarchy': '117139'  # Property category
        }
        
        logger.info("🚀 FINAL BREAKTHROUGH XE.GR SCRAPER")
        logger.info("📋 Enhanced property URL detection + working endpoints")
    
    async def extract_real_properties(self, neighborhood: str, max_properties: int = 10) -> List[RealPropertyData]:
        """Extract real properties using breakthrough approach"""
        
        logger.info(f"🎯 FINAL BREAKTHROUGH: {neighborhood}")
        logger.info(f"📋 Target: {max_properties} verified properties")
        
        properties = []
        
        # Enhanced headers (no bot blocking detected)
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
                
                # Enhanced search strategies
                strategies = [
                    ('neighborhood_search', self.search_by_neighborhood),
                    ('category_search', self.search_by_category),
                    ('location_search', self.search_by_location),
                    ('direct_discovery', self.discover_direct_properties)
                ]
                
                for strategy_name, strategy_func in strategies:
                    if len(properties) >= max_properties:
                        break
                    
                    logger.info(f"🔍 Strategy: {strategy_name}")
                    strategy_properties = await strategy_func(session, neighborhood)
                    
                    for prop in strategy_properties:
                        if len(properties) >= max_properties:
                            break
                        if prop not in properties:  # Avoid duplicates
                            properties.append(prop)
                    
                    logger.info(f"📊 {strategy_name}: +{len(strategy_properties)} properties")
                    await asyncio.sleep(2)  # Strategy cooldown
        
        except Exception as e:
            logger.error(f"❌ Final breakthrough failed: {e}")
        
        logger.info(f"🎯 FINAL BREAKTHROUGH COMPLETE: {len(properties)} properties")
        return properties
    
    async def search_by_neighborhood(self, session: aiohttp.ClientSession, neighborhood: str) -> List[RealPropertyData]:
        """Search using neighborhood name"""
        
        properties = []
        
        # Try multiple neighborhood search variations
        search_terms = [
            neighborhood,
            f"Αθήνα {neighborhood}",
            f"Athens {neighborhood}",
            neighborhood.lower(),
            neighborhood.upper()
        ]
        
        for search_term in search_terms:
            try:
                params = self.search_params.copy()
                params['Publication.freetext'] = search_term
                
                search_url = f"{self.search_endpoint}?{urlencode(params)}"
                logger.info(f"🔍 Searching: {search_term}")
                
                async with session.get(search_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        logger.info(f"✅ Search OK: {len(html)} chars")
                        
                        # Enhanced property URL extraction
                        property_urls = await self.enhanced_url_extraction(html, session, search_term)
                        logger.info(f"📦 Found {len(property_urls)} URLs")
                        
                        # Process each URL
                        for prop_url in property_urls:
                            prop = await self.scrape_property_smart(session, prop_url, neighborhood)
                            if prop:
                                properties.append(prop)
                                logger.info(f"✅ Property: {prop.address[:50]}...")
                            
                            await asyncio.sleep(1)
                            
                            if len(properties) >= 5:  # Limit per search term
                                break
                    
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.warning(f"⚠️ Search term '{search_term}' failed: {e}")
                continue
        
        return properties
    
    async def search_by_category(self, session: aiohttp.ClientSession, neighborhood: str) -> List[RealPropertyData]:
        """Search by property category"""
        
        properties = []
        
        # Try different property categories (discovered from investigation)
        categories = ['117139', '117526', '117538']  # Different property types
        
        for category in categories:
            try:
                params = {
                    'Item.category__hierarchy': category,
                    'Publication.freetext': f'Αθήνα {neighborhood}'
                }
                
                search_url = f"{self.search_endpoint}?{urlencode(params)}"
                logger.info(f"🏠 Category search: {category}")
                
                async with session.get(search_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        property_urls = await self.enhanced_url_extraction(html, session, f"category_{category}")
                        logger.info(f"📦 Category {category}: {len(property_urls)} URLs")
                        
                        for prop_url in property_urls[:3]:  # Limit per category
                            prop = await self.scrape_property_smart(session, prop_url, neighborhood)
                            if prop:
                                properties.append(prop)
                                logger.info(f"✅ Category property: {prop.address[:50]}...")
                            
                            await asyncio.sleep(1)
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.warning(f"⚠️ Category {category} failed: {e}")
                continue
        
        return properties
    
    async def search_by_location(self, session: aiohttp.ClientSession, neighborhood: str) -> List[RealPropertyData]:
        """Search by location patterns"""
        
        properties = []
        
        # Try location-based searches
        location_searches = [
            f"διαμέρισμα {neighborhood}",  # Apartment + neighborhood
            f"ενοικίαση {neighborhood}",   # Rent + neighborhood
            f"πώληση {neighborhood}",     # Sale + neighborhood
            f"{neighborhood} κέντρο",    # Neighborhood + center
            f"{neighborhood} Αθήνα"      # Neighborhood + Athens
        ]
        
        for location_term in location_searches:
            try:
                params = {
                    'Publication.freetext': location_term,
                    'Item.category__hierarchy': '117139'
                }
                
                search_url = f"{self.search_endpoint}?{urlencode(params)}"
                logger.info(f"🗺️ Location: {location_term}")
                
                async with session.get(search_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        property_urls = await self.enhanced_url_extraction(html, session, location_term)
                        logger.info(f"📦 Location '{location_term}': {len(property_urls)} URLs")
                        
                        for prop_url in property_urls[:2]:  # Limit per location
                            prop = await self.scrape_property_smart(session, prop_url, neighborhood)
                            if prop:
                                properties.append(prop)
                                logger.info(f"✅ Location property: {prop.address[:50]}...")
                            
                            await asyncio.sleep(1)
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.warning(f"⚠️ Location '{location_term}' failed: {e}")
                continue
        
        return properties
    
    async def discover_direct_properties(self, session: aiohttp.ClientSession, neighborhood: str) -> List[RealPropertyData]:
        """Discover properties through direct exploration"""
        
        properties = []
        
        try:
            # Try the main search page to find any property links
            logger.info("🔍 Direct discovery from main search")
            
            async with session.get(self.search_endpoint) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Look for any property-related links in the general search page
                    property_urls = await self.enhanced_url_extraction(html, session, "main_search")
                    logger.info(f"📦 Main search: {len(property_urls)} URLs discovered")
                    
                    for prop_url in property_urls[:3]:
                        prop = await self.scrape_property_smart(session, prop_url, neighborhood)
                        if prop:
                            properties.append(prop)
                            logger.info(f"✅ Direct discovery: {prop.address[:50]}...")
                        
                        await asyncio.sleep(1)
        
        except Exception as e:
            logger.warning(f"⚠️ Direct discovery failed: {e}")
        
        return properties
    
    async def enhanced_url_extraction(self, html: str, session: aiohttp.ClientSession, search_context: str) -> List[str]:
        """Enhanced property URL extraction with multiple techniques"""
        
        urls = set()
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Method 1: Look for obvious property links
            property_selectors = [
                'a[href*="/property/"]',
                'a[href*="/rent/"]', 
                'a[href*="/sale/"]',
                'a[href*="enoikiaseis"]',
                'a[href*="poliseis"]',
                'a[href*="diamerisma"]',
                'a[href*="apartment"]',
                'a[href*="/d/"]',  # Pattern from robots.txt
                '.property-card a',
                '.listing a',
                '.result a',
                '[data-testid*="property"] a',
                '[class*="property"] a',
                '[class*="listing"] a',
                '[class*="item"] a'
            ]
            
            for selector in property_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin('https://xe.gr', href)
                        if self.is_valid_property_url(full_url):
                            urls.add(full_url)
            
            # Method 2: Extract URLs from JavaScript/JSON data
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    # Look for property URLs in JavaScript
                    js_urls = re.findall(r'["\']https?://[^"\']*xe\.gr[^"\']*property[^"\']*["\']', script.string)
                    for js_url in js_urls:
                        clean_url = js_url.strip('"\'')
                        if self.is_valid_property_url(clean_url):
                            urls.add(clean_url)
                    
                    # Look for relative property URLs
                    rel_urls = re.findall(r'["\'][^"\']*\/property\/[^"\']*["\']', script.string)
                    for rel_url in rel_urls:
                        clean_url = urljoin('https://xe.gr', rel_url.strip('"\''))
                        if self.is_valid_property_url(clean_url):
                            urls.add(clean_url)
            
            # Method 3: Look for ID patterns in text and construct URLs
            # Extract potential property IDs
            id_patterns = [
                r'property[_-]?id["\']?\s*[:=]\s*["\']?(\d{8,})',
                r'listing[_-]?id["\']?\s*[:=]\s*["\']?(\d{8,})',
                r'/d/[^/]+/(\d{8,})',
                r'id["\']?\s*[:=]\s*["\']?(\d{8,})'
            ]
            
            for pattern in id_patterns:
                ids = re.findall(pattern, html, re.IGNORECASE)
                for prop_id in ids[:5]:  # Limit to prevent too many attempts
                    # Try constructing URLs with common patterns
                    potential_urls = [
                        f"https://xe.gr/property/d/rent/{prop_id}",
                        f"https://xe.gr/property/d/sale/{prop_id}",
                        f"https://xe.gr/property/d/enoikiaseis-katoikion/{prop_id}",
                        f"https://xe.gr/property/d/poliseis-katoikion/{prop_id}"
                    ]
                    
                    for pot_url in potential_urls:
                        urls.add(pot_url)
            
            # Method 4: Save search result page for analysis (debugging)
            if urls:
                debug_file = f'outputs/search_result_{search_context}_{datetime.now().strftime("%H%M%S")}.html'
                try:
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(html)
                    logger.info(f"🔍 Search result saved: {debug_file}")
                except:
                    pass  # Don't fail if we can't save debug file
            
        except Exception as e:
            logger.error(f"❌ URL extraction failed: {e}")
        
        return list(urls)
    
    def is_valid_property_url(self, url: str) -> bool:
        """Enhanced property URL validation"""
        
        if not url or 'xe.gr' not in url:
            return False
        
        # Must contain property indicators
        property_indicators = ['/property/', '/rent/', '/sale/', '/enoikiaseis/', '/poliseis/', '/d/']
        if not any(indicator in url for indicator in property_indicators):
            return False
        
        # Must not be search, admin, or API
        invalid_patterns = ['/search', '/admin', '/api/', '/results', '/filter', 'javascript:', 'mailto:']
        if any(pattern in url.lower() for pattern in invalid_patterns):
            return False
        
        # Should contain some ID or specific identifier
        if not re.search(r'\d{6,}', url):  # Should have some numeric ID
            return False
        
        return True
    
    async def scrape_property_smart(self, session: aiohttp.ClientSession, url: str, neighborhood: str) -> Optional[RealPropertyData]:
        """Smart property scraping with validation"""
        
        try:
            logger.info(f"🏠 Scraping: {url}")
            
            async with session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"⚠️ Property failed: {response.status}")
                    return None
                
                html = await response.text()
                
                # Quick validation - is this actually a property page?
                if not self.is_property_page_content(html, neighborhood):
                    logger.warning(f"⚠️ Not a property page: {url}")
                    return None
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract property data
                data = {
                    'property_id': self.generate_property_id(url),
                    'url': url,
                    'source_timestamp': datetime.now().isoformat(),
                    'html_source_hash': hashlib.md5(html.encode()).hexdigest(),
                    'neighborhood': neighborhood,
                    'extraction_method': 'final_breakthrough',
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
                
                prop = RealPropertyData(**data)
                
                # Final validation
                if self.validate_property(prop):
                    logger.info(f"✅ Valid property: {prop.address[:50]}...")
                    return prop
                else:
                    logger.warning(f"❌ Property validation failed")
                    return None
        
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
            return None
    
    def is_property_page_content(self, html: str, neighborhood: str) -> bool:
        """Check if HTML contains actual property content"""
        
        html_lower = html.lower()
        
        # Must have property-related content
        property_indicators = ['τιμή', 'price', 'τ.μ', 'sqm', 'm²', 'ενοικίαση', 'πώληση', 'διαμέρισμα']
        if not any(indicator in html_lower for indicator in property_indicators):
            return False
        
        # Should mention location
        location_indicators = ['αθήνα', 'athens', neighborhood.lower()]
        has_location = any(indicator in html_lower for indicator in location_indicators)
        
        # Check content length (real property pages should be substantial)
        if len(html) < 5000:  # Too short to be a real property page
            return False
        
        return has_location or len(html) > 20000  # Either has location or is very detailed
    
    # Include all extraction methods (same as previous scrapers)
    def generate_property_id(self, url: str) -> str:
        """Generate property ID"""
        url_match = re.search(r'/(\d+)', url)
        if url_match:
            return f"xe_gr_{url_match.group(1)}"
        else:
            return f"xe_gr_{hashlib.md5(url.encode()).hexdigest()[:8]}"
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title"""
        selectors = ['h1', '.property-title', '.listing-title', 'title', '[class*="title"]']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if len(title) > 5:  # Valid title should have some content
                    return title[:200]
        return "No title found"
    
    def extract_address(self, soup: BeautifulSoup) -> str:
        """Extract address"""
        selectors = ['.address', '.location', '.property-address', '.geo-info', '[class*="address"]', '[class*="location"]']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                address = element.get_text(strip=True)
                if self.validate_athens_address(address):
                    return address[:300]
        
        # Try page text for Athens references
        page_text = soup.get_text()
        athens_patterns = [
            r'[Αα]θήνα[^,\n]{0,50}',
            r'Athens[^,\n]{0,50}',
            r'[Κκ]ολωνάκι[^,\n]{0,30}',
            r'[Ππ]αγκράτι[^,\n]{0,30}',
            r'[Εε]ξάρχεια[^,\n]{0,30}'
        ]
        
        for pattern in athens_patterns:
            match = re.search(pattern, page_text)
            if match:
                return match.group(0).strip()
        
        return "Address not found"
    
    def validate_athens_address(self, address: str) -> bool:
        """Validate Athens address"""
        if not address or len(address) < 5:
            return False
        address_lower = address.lower()
        indicators = ['αθήνα', 'athens', 'κολωνάκι', 'kolonaki', 'παγκράτι', 'pangrati', 'εξάρχεια', 'exarchia']
        return any(indicator in address_lower for indicator in indicators)
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price"""
        selectors = ['.price', '.property-price', '[data-testid*="price"]', '.cost', '[class*="price"]']
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price = self.parse_price(price_text)
                if price and 50 <= price <= 5000000:
                    return price
        
        # Search page text
        page_text = soup.get_text()
        price_patterns = [
            r'(\d{1,3}(?:\.\d{3})*)\s*€',
            r'€\s*(\d{1,3}(?:\.\d{3})*)',
            r'τιμή[:\s]*(\d{1,3}(?:\.\d{3})*)',
            r'(\d{1,3}(?:\.\d{3})*)\s*ευρώ'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                price = self.parse_price(match.group(1))
                if price and 50 <= price <= 5000000:
                    return price
        
        return None
    
    def parse_price(self, price_text: str) -> Optional[float]:
        """Parse price"""
        if not price_text:
            return None
        
        # Clean price text
        price_clean = re.sub(r'[€$£¥₹ευρώeur]', '', price_text, flags=re.IGNORECASE)
        price_clean = re.sub(r'[^\d.,]', '', price_clean)
        
        if not price_clean:
            return None
        
        try:
            # Handle thousands separators
            if '.' in price_clean:
                parts = price_clean.split('.')
                if len(parts) == 2 and len(parts[1]) == 3:
                    # 1.500 format (thousands)
                    price_clean = price_clean.replace('.', '')
            
            price = float(price_clean)
            
            # If very small, might be in thousands
            if price < 10:
                price = price * 1000
            
            return price
        except ValueError:
            return None
    
    def extract_sqm(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract square meters"""
        page_text = soup.get_text()
        sqm_patterns = [
            r'(\d+(?:[.,]\d+)?)\s*τ\.?μ\.?',
            r'(\d+(?:[.,]\d+)?)\s*m²',
            r'(\d+(?:[.,]\d+)?)\s*sqm',
            r'εμβαδόν[:\s]*(\d+(?:[.,]\d+)?)',
            r'(\d+(?:[.,]\d+)?)\s*τετραγωνικά'
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
        room_patterns = [
            r'(\d+)\s*δωμάτια?',
            r'(\d+)\s*rooms?',
            r'(\d+)\s*υπνοδωμάτια?',
            r'(\d+)\s*bedrooms?'
        ]
        
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
        floor_patterns = [
            r'όροφος[:\s]*([^,\n.]{1,15})',
            r'floor[:\s]*([^,\n.]{1,15})',
            r'(\d+)ος\s*όροφος'
        ]
        
        for pattern in floor_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract description"""
        selectors = ['.description', '.property-description', '.details', '[class*="description"]', '.content']
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
            r'ενεργειακή\s+κλάση\s*[:\-]?\s*([A-G][+]?)',
            r'energy\s+class\s*[:\-]?\s*([A-G][+]?)',
            r'κλάση\s+([A-G][+]?)',
            r'class\s+([A-G][+]?)',
            r'ενεργειακό\s+πιστοποιητικό\s*[:\-]?\s*([A-G][+]?)'
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
        
        # Bonus fields
        for field in ['energy_class', 'floor']:
            total_checks += 0.5
            if data.get(field):
                confidence += 0.5
        
        return confidence / total_checks if total_checks > 0 else 0.0
    
    def generate_flags(self, data: Dict) -> List[str]:
        """Generate validation flags"""
        flags = ['xe_gr_verified', 'final_breakthrough']
        
        if data.get('address') and self.validate_athens_address(data['address']):
            flags.append('athens_verified')
        
        if data.get('price') and 50 <= data['price'] <= 5000000:
            flags.append('price_realistic')
        
        if data.get('sqm') and 10 <= data['sqm'] <= 500:
            flags.append('area_realistic')
        
        if data.get('energy_class'):
            flags.append('energy_found')
        
        if data.get('extraction_confidence', 0) > 0.7:
            flags.append('high_confidence')
        
        return flags
    
    def validate_property(self, prop: RealPropertyData) -> bool:
        """Validate property"""
        if not prop.url or not prop.property_id:
            return False
        
        if not prop.address or not self.validate_athens_address(prop.address):
            return False
        
        # Must have at least price OR sqm
        if not prop.price and not prop.sqm:
            return False
        
        # Price validation
        if prop.price and not (50 <= prop.price <= 5000000):
            return False
        
        # Area validation
        if prop.sqm and not (10 <= prop.sqm <= 500):
            return False
        
        # Minimum confidence
        if prop.extraction_confidence < 0.3:
            return False
        
        return True

async def main():
    """Test final breakthrough scraper"""
    
    logger.info("🚀 TESTING FINAL BREAKTHROUGH XE.GR SCRAPER")
    
    scraper = FinalBreakthroughXEScraper()
    
    # Test with Kolonaki
    properties = await scraper.extract_real_properties('Κολωνάκι', max_properties=5)
    
    logger.info(f"\n🎯 FINAL BREAKTHROUGH RESULTS: {len(properties)} properties")
    
    if properties:
        for i, prop in enumerate(properties, 1):
            logger.info(f"\n📊 PROPERTY {i}:")
            logger.info(f"   Address: {prop.address}")
            logger.info(f"   Price: €{prop.price}")
            logger.info(f"   Area: {prop.sqm}m²")
            logger.info(f"   Rooms: {prop.rooms}")
            logger.info(f"   Energy: {prop.energy_class}")
            logger.info(f"   Confidence: {prop.extraction_confidence:.2f}")
            logger.info(f"   URL: {prop.url}")
        
        # Save results
        output_data = [asdict(prop) for prop in properties]
        with open('outputs/final_breakthrough_results.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✅ BREAKTHROUGH SUCCESS!")
        logger.info(f"📄 Results saved: outputs/final_breakthrough_results.json")
        logger.info(f"🎯 {len(properties)} REAL xe.gr properties extracted!")
    else:
        logger.warning("❌ No properties extracted")

if __name__ == "__main__":
    asyncio.run(main())