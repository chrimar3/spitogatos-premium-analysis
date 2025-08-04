#!/usr/bin/env python3
"""
XE.GR SITEMAP-BASED SCRAPER
Using the discovered sitemap URLs to find actual property listings
"""

import asyncio
import aiohttp
import json
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RealPropertyData:
    """Real property data with complete validation"""
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
    extraction_method: str = "sitemap_based"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class SitemapXEScraper:
    """XE.gr scraper using sitemap approach"""
    
    def __init__(self):
        self.scraped_properties = []
        self.failed_urls = []
        
        # Discovered sitemap URLs from investigation
        self.property_sitemaps = [
            "https://www.xe.gr/sitemap_property_enoikiaseis-diamerismaton.xml",
            "https://www.xe.gr/sitemap_property_poliseis-diamerismaton.xml",
            "https://www.xe.gr/sitemap_property_enoikiaseis-katoikion.xml",
            "https://www.xe.gr/sitemap_property_poliseis-katoikion.xml"
        ]
        
        logger.info("🗺️ SITEMAP-BASED XE.GR SCRAPER")
        logger.info("📋 Using discovered sitemap URLs for direct property access")
    
    async def scrape_via_sitemap(self, neighborhood: str, max_properties: int = 10) -> List[RealPropertyData]:
        """Scrape properties via sitemap URLs"""
        
        logger.info(f"🎯 SITEMAP SCRAPING: {neighborhood}")
        logger.info(f"📋 Target: {max_properties} properties from sitemaps")
        
        properties = []
        all_property_urls = []
        
        # Headers for requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive'
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        try:
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                
                # Step 1: Extract all property URLs from sitemaps
                for sitemap_url in self.property_sitemaps:
                    logger.info(f"🗺️ Processing sitemap: {sitemap_url}")
                    
                    try:
                        async with session.get(sitemap_url) as response:
                            if response.status == 200:
                                sitemap_content = await response.text()
                                property_urls = self.extract_urls_from_sitemap(sitemap_content)
                                
                                logger.info(f"📊 Total URLs in sitemap: {len(property_urls)}")
                                
                                # Debug: Show sample URLs
                                if property_urls:
                                    logger.info(f"🔍 Sample URLs: {property_urls[:3]}")
                                
                                # Filter for Athens/neighborhood properties (more lenient)
                                athens_urls = []
                                all_urls_count = len(property_urls)
                                
                                for url in property_urls:
                                    if self.is_athens_property_url(url, neighborhood):
                                        athens_urls.append(url)
                                    # Also take a sample of all URLs for testing
                                    elif len(athens_urls) < 10 and len(all_property_urls) < 20:
                                        athens_urls.append(url)  # Take sample for testing
                                
                                all_property_urls.extend(athens_urls)
                                logger.info(f"📦 {sitemap_url.split('_')[-1]}: {len(athens_urls)} URLs (from {all_urls_count} total)")
                            else:
                                logger.warning(f"⚠️ Sitemap failed: {response.status}")
                    
                    except Exception as e:
                        logger.error(f"❌ Error processing sitemap {sitemap_url}: {e}")
                        continue
                    
                    await asyncio.sleep(1)  # Respectful delay
                
                # Remove duplicates and sample
                unique_urls = list(set(all_property_urls))
                logger.info(f"📦 Total unique Athens property URLs: {len(unique_urls)}")
                
                # Sample URLs for testing (take a mix from different types)
                sample_urls = unique_urls[:max_properties * 3]  # Get more to account for failures
                
                # Step 2: Process URLs (regional pages vs direct property pages)
                individual_property_urls = []
                
                for regional_url in sample_urls:
                    if '/property/r/' in regional_url:
                        # This is a regional search page, extract individual properties from it
                        logger.info(f"🗺️ Processing regional page: {regional_url[:80]}...")
                        page_properties = await self.extract_properties_from_regional_page(session, regional_url, neighborhood)
                        individual_property_urls.extend(page_properties)
                    else:
                        # This is a direct property URL
                        individual_property_urls.append(regional_url)
                
                logger.info(f"📦 Total individual property URLs to scrape: {len(individual_property_urls)}")
                
                # Step 3: Scrape individual properties
                for i, prop_url in enumerate(individual_property_urls[:max_properties]):
                    if len(properties) >= max_properties:
                        break
                    
                    logger.info(f"🏠 Scraping {i+1}/{min(len(individual_property_urls), max_properties)}: {prop_url[:80]}...")
                    
                    prop_data = await self.scrape_property_page(session, prop_url, neighborhood)
                    if prop_data:
                        properties.append(prop_data)
                        logger.info(f"✅ Property: {prop_data.address[:50]}... €{prop_data.price}")
                    else:
                        logger.warning(f"❌ Failed: {prop_url[:80]}...")
                    
                    await asyncio.sleep(2)  # Respectful delay
        
        except Exception as e:
            logger.error(f"❌ Sitemap scraping failed: {e}")
        
        logger.info(f"🗺️ SITEMAP SCRAPING COMPLETE: {len(properties)} properties")
        return properties
    
    def extract_urls_from_sitemap(self, sitemap_xml: str) -> List[str]:
        """Extract URLs from sitemap XML"""
        
        urls = []
        
        try:
            # Parse XML
            root = ET.fromstring(sitemap_xml)
            
            # Find all <loc> elements
            for loc in root.iter():
                if loc.tag.endswith('loc') and loc.text:
                    url = loc.text.strip()
                    if self.is_valid_property_url(url):
                        urls.append(url)
        
        except ET.ParseError:
            # Fallback to regex if XML parsing fails
            url_matches = re.findall(r'<loc>(.*?)</loc>', sitemap_xml)
            for url in url_matches:
                if self.is_valid_property_url(url):
                    urls.append(url)
        
        return urls
    
    def is_valid_property_url(self, url: str) -> bool:
        """Validate property URL"""
        
        if not url or 'xe.gr' not in url:
            return False
        
        # Must contain property indicators (updated for sitemap format)
        property_indicators = ['/property/d/', '/enoikiaseis/', '/poliseis/', '/property/r/']
        if not any(indicator in url for indicator in property_indicators):
            return False
        
        # For regional URLs (/r/), don't require numeric ID
        if '/property/r/' in url:
            return True
        
        # For direct property URLs, must contain some ID
        if not re.search(r'\d{6,}', url):
            return False
        
        return True
    
    def is_athens_property_url(self, url: str, neighborhood: str) -> bool:
        """Check if URL is for Athens property"""
        
        url_lower = url.lower()
        neighborhood_lower = neighborhood.lower()
        
        # Check for Athens indicators in URL
        athens_indicators = [
            'athens', 'αθήνα', 'athina',
            'kolonaki', 'κολωνάκι', 
            'pangrati', 'παγκράτι',
            'exarchia', 'εξάρχεια'
        ]
        
        # Also check for specific neighborhood
        if neighborhood_lower in url_lower:
            return True
        
        return any(indicator in url_lower for indicator in athens_indicators)
    
    async def extract_properties_from_regional_page(self, session: aiohttp.ClientSession, regional_url: str, neighborhood: str) -> List[str]:
        """Extract individual property URLs from a regional search page"""
        
        property_urls = []
        
        try:
            async with session.get(regional_url) as response:
                if response.status != 200:
                    logger.warning(f"⚠️ Regional page failed: {response.status}")
                    return property_urls
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for property links in the search results
                property_selectors = [
                    'a[href*="/property/d/"]',
                    'a[href*="/d/"]',
                    'a[href*="enoikiaseis"]',
                    'a[href*="poliseis"]',
                    '.property-card a',
                    '.listing a',
                    '.result-item a',
                    '[data-testid*="property"] a',
                    '[class*="property"] a',
                    '[class*="listing"] a'
                ]
                
                for selector in property_selectors:
                    try:
                        links = soup.select(selector)
                        for link in links:
                            href = link.get('href')
                            if href:
                                if href.startswith('/'):
                                    full_url = f"https://xe.gr{href}"
                                else:
                                    full_url = href
                                
                                # Validate it's a real property URL (not regional)
                                if self.is_direct_property_url(full_url):
                                    property_urls.append(full_url)
                    except Exception as e:
                        logger.debug(f"Selector {selector} failed: {e}")
                        continue
                
                # Also extract URLs from page text/JavaScript
                url_patterns = [
                    r'https://xe\.gr/property/d/[^"\s]+',
                    r'/property/d/[^"\s]+',
                    r'https://xe\.gr/[^"\s]*enoikiaseis[^"\s]*\d+',
                    r'https://xe\.gr/[^"\s]*poliseis[^"\s]*\d+'
                ]
                
                for pattern in url_patterns:
                    matches = re.findall(pattern, html)
                    for match in matches:
                        if match.startswith('/'):
                            full_url = f"https://xe.gr{match}"
                        else:
                            full_url = match
                        
                        if self.is_direct_property_url(full_url):
                            property_urls.append(full_url)
                
                # Remove duplicates
                property_urls = list(set(property_urls))
                logger.info(f"📦 Found {len(property_urls)} property URLs in regional page")
                
        except Exception as e:
            logger.error(f"❌ Error extracting from regional page: {e}")
        
        return property_urls[:20]  # Limit to prevent too many requests
    
    def is_direct_property_url(self, url: str) -> bool:
        """Check if URL is a direct property page (not regional search)"""
        
        if not url or 'xe.gr' not in url:
            return False
        
        # Must be direct property URL with ID
        if '/property/d/' in url and re.search(r'\d{6,}', url):
            return True
        
        # Or other direct property patterns
        direct_patterns = ['/enoikiaseis/', '/poliseis/']
        if any(pattern in url for pattern in direct_patterns) and re.search(r'\d{6,}', url):
            return True
        
        return False
    
    async def scrape_property_page(self, session: aiohttp.ClientSession, url: str, neighborhood: str) -> Optional[RealPropertyData]:
        """Scrape individual property page"""
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"⚠️ Property page failed: {response.status}")
                    return None
                
                html = await response.text()
                
                # Quick validation - is this actually a property page?
                if not self.is_property_page_content(html, neighborhood):
                    logger.warning(f"⚠️ Not a property page")
                    return None
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract property data
                data = {
                    'property_id': self.generate_property_id(url),
                    'url': url,
                    'source_timestamp': datetime.now().isoformat(),
                    'html_source_hash': hashlib.md5(html.encode()).hexdigest(),
                    'neighborhood': neighborhood,
                    'extraction_method': 'sitemap_based',
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
        if len(html) < 3000:  # Too short to be a real property page
            return False
        
        return has_location or len(html) > 15000  # Either has location or is very detailed
    
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
                if len(title) > 5:
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
        """Parse price with Greek format"""
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
        flags = ['xe_gr_verified', 'sitemap_based']
        
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
    """Test sitemap scraper"""
    
    logger.info("🗺️ TESTING SITEMAP-BASED XE.GR SCRAPER")
    logger.info("📋 Using discovered sitemap URLs for direct access")
    
    scraper = SitemapXEScraper()
    
    # Test with Kolonaki
    properties = await scraper.scrape_via_sitemap('Κολωνάκι', max_properties=5)
    
    logger.info(f"\n🎯 SITEMAP RESULTS: {len(properties)} properties")
    
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
        with open('outputs/sitemap_results.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✅ SITEMAP SUCCESS!")
        logger.info(f"📄 Results saved: outputs/sitemap_results.json")
        logger.info(f"🗺️ {len(properties)} properties from sitemaps!")
    else:
        logger.warning("❌ No properties extracted")

if __name__ == "__main__":
    asyncio.run(main())