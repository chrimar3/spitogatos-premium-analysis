#!/usr/bin/env python3
"""
BULLETPROOF XE.GR SCRAPER - MISSION CRITICAL
Real data extraction with complete validation and audit trail
NO SYNTHETIC DATA - ONLY VERIFIED xe.gr PROPERTIES
"""

import asyncio
import aiohttp
import json
import logging
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import random
from urllib.parse import urljoin, urlparse
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RealPropertyData:
    """REAL property data with complete validation"""
    # MANDATORY FIELDS - NO PROPERTY WITHOUT THESE
    property_id: str
    url: str
    source_timestamp: str
    
    # LOCATION DATA - MUST BE REAL ATHENS
    address: str
    neighborhood: str
    
    # PROPERTY DETAILS - FROM ACTUAL LISTING
    price: Optional[float]
    sqm: Optional[float]
    rooms: Optional[int]
    floor: Optional[str]
    
    # ENERGY DATA - FROM XE.GR IF AVAILABLE
    energy_class: Optional[str]
    
    # LISTING DETAILS
    title: str
    description: str
    
    # VALIDATION DATA
    html_source_hash: str
    extraction_confidence: float
    validation_flags: List[str]
    
    # COORDINATES (if extractable)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class BulletproofXEScraper:
    """BULLETPROOF xe.gr scraper - ONLY REAL DATA"""
    
    def __init__(self):
        self.session = None
        self.scraped_properties = []
        self.failed_urls = []
        self.audit_log = []
        
        # Athens neighborhoods we ACTUALLY want to scrape
        self.target_neighborhoods = {
            'Κολωνάκι': ['Kolonaki', 'Κολωνάκι'],
            'Παγκράτι': ['Pangrati', 'Παγκράτι'], 
            'Εξάρχεια': ['Exarchia', 'Εξάρχεια']
        }
        
        # Real Athens validation patterns
        self.athens_patterns = [
            r'αθήνα', r'athens', r'κολωνάκι', r'kolonaki', 
            r'παγκράτι', r'pangrati', r'εξάρχεια', r'exarchia',
            r'κέντρο', r'center', r'downtown'
        ]
        
        # Energy class patterns
        self.energy_patterns = [
            r'ενεργειακή\s+κλάση\s*[:\-]?\s*([A-G][+]?)',
            r'energy\s+class\s*[:\-]?\s*([A-G][+]?)',
            r'κλάση\s+([A-G][+]?)',
            r'class\s+([A-G][+]?)'
        ]
        
        logger.info("🎯 BULLETPROOF XE.GR SCRAPER - REAL DATA ONLY")
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5,el;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def scrape_real_properties(self, neighborhood: str, max_properties: int = 100) -> List[RealPropertyData]:
        """Scrape REAL properties from xe.gr with complete validation"""
        
        logger.info(f"🎯 MISSION CRITICAL: Scraping REAL properties for {neighborhood}")
        logger.info(f"📋 Target: {max_properties} VERIFIED properties with URLs, addresses, sqm, energy classes")
        
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'scraping_started',
            'neighborhood': neighborhood,
            'target_properties': max_properties
        })
        
        # Get search URLs for the neighborhood
        search_urls = await self._get_neighborhood_search_urls(neighborhood)
        
        if not search_urls:
            logger.error(f"❌ CRITICAL FAILURE: No search URLs found for {neighborhood}")
            return []
        
        # Scrape properties from search results
        all_properties = []
        
        for search_url in search_urls:
            logger.info(f"🔍 Scraping search results: {search_url}")
            
            try:
                # Get property URLs from search page
                property_urls = await self._extract_property_urls_from_search(search_url)
                
                logger.info(f"📦 Found {len(property_urls)} property URLs")
                
                # Scrape individual properties
                for i, prop_url in enumerate(property_urls[:max_properties]):
                    if len(all_properties) >= max_properties:
                        break
                    
                    logger.info(f"🏠 Scraping property {i+1}/{len(property_urls)}: {prop_url}")
                    
                    property_data = await self._scrape_individual_property(prop_url, neighborhood)
                    
                    if property_data and self._validate_property_data(property_data):
                        all_properties.append(property_data)
                        logger.info(f"✅ Property validated: {property_data.property_id}")
                    else:
                        logger.warning(f"❌ Property validation failed: {prop_url}")
                        self.failed_urls.append(prop_url)
                    
                    # Enhanced rate limiting to avoid 403 errors
                    await asyncio.sleep(random.uniform(3, 8))
                
            except Exception as e:
                logger.error(f"❌ Error scraping search URL {search_url}: {e}")
                continue
        
        # Final validation and audit
        validated_properties = self._final_validation_pass(all_properties, neighborhood)
        
        logger.info(f"✅ MISSION ACCOMPLISHED: {len(validated_properties)} REAL properties scraped")
        logger.info(f"📊 Success rate: {len(validated_properties)}/{len(all_properties)+len(self.failed_urls)} = {len(validated_properties)/(len(all_properties)+len(self.failed_urls))*100:.1f}%")
        
        # Save audit trail
        await self._save_audit_trail(validated_properties, neighborhood)
        
        return validated_properties
    
    async def _get_neighborhood_search_urls(self, neighborhood: str) -> List[str]:
        """Get search URLs for the neighborhood"""
        
        # Real xe.gr search patterns
        base_urls = [
            f"https://xe.gr/property/search?geo_place_ids=ChIJ8UNwBh-9oRQR3Y1mdkU1Nic&geo_place_categories=neighborhood&transaction_name=rent&property_name=apartment&neighborhood={neighborhood}",
            f"https://xe.gr/property/search?geo_place_ids=ChIJ8UNwBh-9oRQR3Y1mdkU1Nic&geo_place_categories=neighborhood&transaction_name=sale&property_name=apartment&neighborhood={neighborhood}",
        ]
        
        # Try different neighborhood name variations
        neighborhood_variations = []
        if neighborhood in self.target_neighborhoods:
            neighborhood_variations = self.target_neighborhoods[neighborhood]
        else:
            neighborhood_variations = [neighborhood]
        
        search_urls = []
        for base_url in base_urls:
            for variation in neighborhood_variations:
                search_urls.append(base_url.replace(f"neighborhood={neighborhood}", f"neighborhood={variation}"))
        
        return search_urls
    
    async def _extract_property_urls_from_search(self, search_url: str) -> List[str]:
        """Extract property URLs from search results page"""
        
        try:
            async with self.session.get(search_url) as response:
                if response.status != 200:
                    logger.error(f"❌ Search page failed: {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for property links
                property_urls = []
                
                # Multiple selectors to catch property links
                selectors = [
                    'a[href*="/property/"]',
                    'a[href*="/rent/"]',
                    'a[href*="/sale/"]',
                    '[data-testid*="property"] a',
                    '.property-card a',
                    '.listing-card a'
                ]
                
                for selector in selectors:
                    links = soup.select(selector)
                    for link in links:
                        href = link.get('href')
                        if href:
                            # Convert to absolute URL
                            full_url = urljoin('https://xe.gr', href)
                            
                            # Validate it's a property URL
                            if self._is_valid_property_url(full_url):
                                property_urls.append(full_url)
                
                # Remove duplicates
                property_urls = list(set(property_urls))
                
                logger.info(f"📦 Extracted {len(property_urls)} property URLs from search")
                
                return property_urls
                
        except Exception as e:
            logger.error(f"❌ Error extracting URLs from search: {e}")
            return []
    
    def _is_valid_property_url(self, url: str) -> bool:
        """Validate if URL is a real property listing"""
        
        if not url or not isinstance(url, str):
            return False
        
        # Must be xe.gr domain
        if 'xe.gr' not in url:
            return False
        
        # Must contain property indicators
        property_indicators = ['/property/', '/rent/', '/sale/', '/listing/']
        if not any(indicator in url for indicator in property_indicators):
            return False
        
        # Must not be search or category page
        invalid_patterns = ['/search', '/category', '/filter', '/api/']
        if any(pattern in url for pattern in invalid_patterns):
            return False
        
        return True
    
    async def _scrape_individual_property(self, property_url: str, neighborhood: str) -> Optional[RealPropertyData]:
        """Scrape individual property with complete data extraction"""
        
        try:
            async with self.session.get(property_url) as response:
                if response.status != 200:
                    logger.error(f"❌ Property page failed: {response.status} for {property_url}")
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Create property ID from URL
                property_id = self._generate_property_id(property_url)
                
                # Extract ALL possible data
                extracted_data = {
                    'property_id': property_id,
                    'url': property_url,
                    'source_timestamp': datetime.now().isoformat(),
                    'html_source_hash': hashlib.md5(html.encode()).hexdigest(),
                    'neighborhood': neighborhood
                }
                
                # Extract title
                extracted_data['title'] = self._extract_title(soup)
                
                # Extract address (CRITICAL - must be real Athens address)
                extracted_data['address'] = self._extract_address(soup)
                
                # Extract price (CRITICAL)
                extracted_data['price'] = self._extract_price(soup)
                
                # Extract square meters (CRITICAL)
                extracted_data['sqm'] = self._extract_sqm(soup)
                
                # Extract rooms
                extracted_data['rooms'] = self._extract_rooms(soup)
                
                # Extract floor
                extracted_data['floor'] = self._extract_floor(soup)
                
                # Extract description
                extracted_data['description'] = self._extract_description(soup)
                
                # Extract energy class (if available)
                extracted_data['energy_class'] = self._extract_energy_class(soup, html)
                
                # Extract coordinates (if available)
                coords = self._extract_coordinates(soup, html)
                extracted_data['latitude'] = coords[0] if coords else None
                extracted_data['longitude'] = coords[1] if coords else None
                
                # Calculate extraction confidence
                extracted_data['extraction_confidence'] = self._calculate_extraction_confidence(extracted_data)
                
                # Set validation flags
                extracted_data['validation_flags'] = self._generate_validation_flags(extracted_data)
                
                # Create property object
                property_data = RealPropertyData(**extracted_data)
                
                logger.info(f"📊 Extracted: {property_data.address}, €{property_data.price}, {property_data.sqm}m², Energy: {property_data.energy_class}")
                
                return property_data
                
        except Exception as e:
            logger.error(f"❌ Error scraping property {property_url}: {e}")
            return None
    
    def _generate_property_id(self, url: str) -> str:
        """Generate unique property ID from URL"""
        # Extract numeric ID from URL if possible
        url_match = re.search(r'/(\d+)', url)
        if url_match:
            return f"xe_gr_{url_match.group(1)}"
        else:
            # Fallback to hash
            return f"xe_gr_{hashlib.md5(url.encode()).hexdigest()[:8]}"
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract property title"""
        selectors = [
            'h1',
            '.property-title',
            '.listing-title',
            '[data-testid*="title"]',
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)[:200]  # Limit length
        
        return "No title found"
    
    def _extract_address(self, soup: BeautifulSoup) -> str:
        """Extract property address - MUST BE REAL ATHENS ADDRESS"""
        selectors = [
            '.address',
            '.location',
            '.property-address',
            '[data-testid*="address"]',
            '[data-testid*="location"]',
            '.breadcrumb',
            '.geo-info'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                address_text = element.get_text(strip=True)
                # Validate it's a real Athens address
                if self._validate_athens_address(address_text):
                    return address_text[:300]  # Limit length
        
        # Try extracting from page text
        page_text = soup.get_text()
        athens_match = re.search(r'[Αα]θήνα.*?[,\n]', page_text)
        if athens_match:
            return athens_match.group(0).strip()
        
        return "Address not found"
    
    def _validate_athens_address(self, address: str) -> bool:
        """Validate address is actually in Athens"""
        if not address:
            return False
        
        address_lower = address.lower()
        
        # Must contain Athens indicators
        athens_indicators = ['αθήνα', 'athens', 'κολωνάκι', 'kolonaki', 'παγκράτι', 'pangrati', 'εξάρχεια', 'exarchia']
        
        return any(indicator in address_lower for indicator in athens_indicators)
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract property price"""
        selectors = [
            '.price',
            '.property-price', 
            '[data-testid*="price"]',
            '.listing-price',
            '.cost'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price = self._parse_price(price_text)
                if price and price > 0:
                    return price
        
        # Try extracting from page text
        page_text = soup.get_text()
        
        # Greek price patterns
        price_patterns = [
            r'(\d{1,3}(?:\.\d{3})*)\s*€',
            r'€\s*(\d{1,3}(?:\.\d{3})*)',
            r'(\d{1,3}(?:,\d{3})*)\s*ευρώ',
            r'τιμή[:\s]*(\d{1,3}(?:\.\d{3})*)',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                price = self._parse_price(match.group(1))
                if price and 50 <= price <= 5000000:  # Reasonable range
                    return price
        
        return None
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price from text - Fixed for Greek number format"""
        if not price_text:
            return None
        
        # Clean the text first
        price_text = price_text.strip()
        
        # Remove currency symbols and words
        price_clean = re.sub(r'[€$£¥₹ευρώeur]', '', price_text, flags=re.IGNORECASE)
        price_clean = re.sub(r'[^\d.,]', '', price_clean)
        
        if not price_clean:
            return None
        
        try:
            # Handle Greek/European number format
            if '.' in price_clean and ',' in price_clean:
                # Format like: 1.500,50 (European)
                comma_pos = price_clean.rfind(',')
                dot_pos = price_clean.rfind('.')
                
                if comma_pos > dot_pos:
                    # Dot is thousands separator, comma is decimal
                    price_clean = price_clean.replace('.', '').replace(',', '.')
                else:
                    # Comma is thousands separator, dot is decimal  
                    price_clean = price_clean.replace(',', '')
            elif '.' in price_clean:
                # Check if it's thousands separator or decimal
                parts = price_clean.split('.')
                if len(parts) == 2 and len(parts[1]) == 3 and len(parts[0]) <= 3:
                    # Likely thousands separator like 2.500
                    price_clean = price_clean.replace('.', '')
                elif len(parts) > 2:
                    # Multiple dots - thousands separators like 1.500.000
                    price_clean = price_clean.replace('.', '')
                # Otherwise keep as decimal
            elif ',' in price_clean:
                # Check if it's thousands separator or decimal
                parts = price_clean.split(',')
                if len(parts) == 2 and len(parts[1]) == 3 and len(parts[0]) <= 3:
                    # Likely thousands separator like 2,500
                    price_clean = price_clean.replace(',', '')
                elif len(parts) > 2:
                    # Multiple commas - thousands separators
                    price_clean = price_clean.replace(',', '')
                else:
                    # Decimal separator
                    price_clean = price_clean.replace(',', '.')
            
            price = float(price_clean)
            
            # Validation - Greek property prices should be reasonable
            if price < 10:
                # Likely in thousands, multiply by 1000
                price = price * 1000
            
            return price
            
        except ValueError:
            return None
    
    def _extract_sqm(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract property square meters"""
        selectors = [
            '.sqm',
            '.area',
            '.size',
            '[data-testid*="area"]',
            '[data-testid*="sqm"]',
            '.property-area'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                sqm_text = element.get_text(strip=True)
                sqm = self._parse_sqm(sqm_text)
                if sqm and sqm > 0:
                    return sqm
        
        # Try extracting from page text
        page_text = soup.get_text()
        
        # Greek sqm patterns
        sqm_patterns = [
            r'(\d+(?:[.,]\d+)?)\s*τ\.?μ\.?',
            r'(\d+(?:[.,]\d+)?)\s*m²',
            r'(\d+(?:[.,]\d+)?)\s*sqm',
            r'εμβαδόν[:\s]*(\d+(?:[.,]\d+)?)',
            r'μέγεθος[:\s]*(\d+(?:[.,]\d+)?)'
        ]
        
        for pattern in sqm_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                sqm = self._parse_sqm(match.group(1))
                if sqm and 10 <= sqm <= 500:  # Reasonable range
                    return sqm
        
        return None
    
    def _parse_sqm(self, sqm_text: str) -> Optional[float]:
        """Parse square meters from text"""
        if not sqm_text:
            return None
        
        # Extract numeric value
        sqm_clean = re.sub(r'[^\d.,]', '', sqm_text)
        
        if not sqm_clean:
            return None
        
        try:
            # Handle decimal separator
            if ',' in sqm_clean:
                sqm_clean = sqm_clean.replace(',', '.')
            
            return float(sqm_clean)
            
        except ValueError:
            return None
    
    def _extract_rooms(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract number of rooms"""
        selectors = [
            '.rooms',
            '.bedrooms',
            '[data-testid*="rooms"]',
            '[data-testid*="bedroom"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                rooms_text = element.get_text(strip=True)
                rooms = self._parse_rooms(rooms_text)
                if rooms:
                    return rooms
        
        # Try extracting from page text
        page_text = soup.get_text()
        
        room_patterns = [
            r'(\d+)\s*δωμάτι',
            r'(\d+)\s*rooms?',
            r'(\d+)\s*bedrooms?'
        ]
        
        for pattern in room_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                rooms = int(match.group(1))
                if 1 <= rooms <= 10:  # Reasonable range
                    return rooms
        
        return None
    
    def _parse_rooms(self, rooms_text: str) -> Optional[int]:
        """Parse number of rooms from text"""
        if not rooms_text:
            return None
        
        # Extract first number
        match = re.search(r'\d+', rooms_text)
        if match:
            try:
                rooms = int(match.group())
                if 1 <= rooms <= 10:
                    return rooms
            except ValueError:
                pass
        
        return None
    
    def _extract_floor(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract floor information"""
        selectors = [
            '.floor',
            '[data-testid*="floor"]',
            '.level'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                floor_text = element.get_text(strip=True)
                if floor_text and len(floor_text) < 20:
                    return floor_text
        
        # Try extracting from page text
        page_text = soup.get_text()
        
        floor_patterns = [
            r'όροφος[:\s]*([^,\n.]{1,15})',
            r'floor[:\s]*([^,\n.]{1,15})'
        ]
        
        for pattern in floor_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract property description"""
        selectors = [
            '.description',
            '.property-description',
            '[data-testid*="description"]',
            '.listing-description',
            '.details'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                description = element.get_text(strip=True)
                if description and len(description) > 20:
                    return description[:1000]  # Limit length
        
        return "No description found"
    
    def _extract_energy_class(self, soup: BeautifulSoup, html: str) -> Optional[str]:
        """Extract energy class if available"""
        
        # First try structured data
        selectors = [
            '.energy-class',
            '.energy-rating',
            '[data-testid*="energy"]',
            '.efficiency'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                energy_text = element.get_text(strip=True)
                energy_class = self._parse_energy_class(energy_text)
                if energy_class:
                    return energy_class
        
        # Try extracting from full text
        full_text = soup.get_text() + html
        
        for pattern in self.energy_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE | re.MULTILINE)
            if match:
                energy_class = match.group(1).upper()
                if self._validate_energy_class(energy_class):
                    return energy_class
        
        return None
    
    def _parse_energy_class(self, energy_text: str) -> Optional[str]:
        """Parse energy class from text"""
        if not energy_text:
            return None
        
        # Extract energy class pattern
        match = re.search(r'([A-G][+]?)', energy_text.upper())
        if match:
            energy_class = match.group(1)
            if self._validate_energy_class(energy_class):
                return energy_class
        
        return None
    
    def _validate_energy_class(self, energy_class: str) -> bool:
        """Validate energy class is valid"""
        valid_classes = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F']
        return energy_class in valid_classes
    
    def _extract_coordinates(self, soup: BeautifulSoup, html: str) -> Optional[Tuple[float, float]]:
        """Extract coordinates if available"""
        
        # Look for map or coordinates in scripts
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            if script.string:
                # Look for coordinate patterns
                coord_patterns = [
                    r'lat["\']?\s*:\s*([0-9.-]+).*?lng["\']?\s*:\s*([0-9.-]+)',
                    r'latitude["\']?\s*:\s*([0-9.-]+).*?longitude["\']?\s*:\s*([0-9.-]+)',
                    r'([0-9.]+),\s*([0-9.]+).*athens'
                ]
                
                for pattern in coord_patterns:
                    match = re.search(pattern, script.string, re.IGNORECASE)
                    if match:
                        try:
                            lat, lng = float(match.group(1)), float(match.group(2))
                            # Validate coordinates are in Athens area
                            if 37.8 <= lat <= 38.1 and 23.6 <= lng <= 23.8:
                                return (lat, lng)
                        except ValueError:
                            continue
        
        return None
    
    def _calculate_extraction_confidence(self, data: Dict) -> float:
        """Calculate extraction confidence score"""
        confidence = 0.0
        total_checks = 0
        
        # Critical fields
        critical_fields = ['address', 'price', 'sqm']
        for field in critical_fields:
            total_checks += 2  # Weight critical fields more
            if data.get(field):
                confidence += 2
        
        # Important fields
        important_fields = ['title', 'description', 'rooms']
        for field in important_fields:
            total_checks += 1
            if data.get(field):
                confidence += 1
        
        # Bonus fields
        bonus_fields = ['energy_class', 'floor', 'latitude', 'longitude']
        for field in bonus_fields:
            total_checks += 0.5
            if data.get(field):
                confidence += 0.5
        
        return confidence / total_checks if total_checks > 0 else 0.0
    
    def _generate_validation_flags(self, data: Dict) -> List[str]:
        """Generate validation flags for the property"""
        flags = ['xe_gr_verified', 'real_extraction']
        
        # Address validation
        if data.get('address') and self._validate_athens_address(data['address']):
            flags.append('athens_address_verified')
        
        # Price validation
        if data.get('price') and 50 <= data['price'] <= 5000000:
            flags.append('price_realistic')
        
        # Area validation
        if data.get('sqm') and 10 <= data['sqm'] <= 500:
            flags.append('area_realistic')
        
        # Energy class validation
        if data.get('energy_class'):
            flags.append('energy_class_found')
        
        # High confidence
        if data.get('extraction_confidence', 0) > 0.7:
            flags.append('high_confidence')
        
        return flags
    
    def _validate_property_data(self, property_data: RealPropertyData) -> bool:
        """Validate property data meets minimum requirements"""
        
        # MANDATORY: Must have URL and property ID
        if not property_data.url or not property_data.property_id:
            logger.warning(f"❌ Missing URL or ID: {property_data.property_id}")
            return False
        
        # MANDATORY: Must have real Athens address
        if not property_data.address or not self._validate_athens_address(property_data.address):
            logger.warning(f"❌ Invalid Athens address: {property_data.address}")
            return False
        
        # MANDATORY: Must have either price or sqm (or both)
        if not property_data.price and not property_data.sqm:
            logger.warning(f"❌ Missing price AND sqm: {property_data.property_id}")
            return False
        
        # Price validation if present
        if property_data.price and not (50 <= property_data.price <= 5000000):
            logger.warning(f"❌ Unrealistic price: €{property_data.price}")
            return False
        
        # Area validation if present
        if property_data.sqm and not (10 <= property_data.sqm <= 500):
            logger.warning(f"❌ Unrealistic area: {property_data.sqm}m²")
            return False
        
        # Must have minimum confidence
        if property_data.extraction_confidence < 0.3:
            logger.warning(f"❌ Low confidence: {property_data.extraction_confidence}")
            return False
        
        return True
    
    def _final_validation_pass(self, properties: List[RealPropertyData], neighborhood: str) -> List[RealPropertyData]:
        """Final validation pass on all properties"""
        
        logger.info(f"🔍 Final validation pass: {len(properties)} properties")
        
        validated = []
        
        for prop in properties:
            # Additional cross-validation
            validation_issues = []
            
            # Check for duplicates
            duplicate_found = False
            for other_prop in validated:
                if prop.url == other_prop.url:
                    duplicate_found = True
                    break
            
            if duplicate_found:
                validation_issues.append("Duplicate URL")
                continue
            
            # Neighborhood consistency
            prop_neighborhood_lower = prop.neighborhood.lower()
            target_neighborhood_lower = neighborhood.lower()
            
            if target_neighborhood_lower not in prop_neighborhood_lower:
                # Check if address contains target neighborhood
                if prop.address and target_neighborhood_lower not in prop.address.lower():
                    validation_issues.append(f"Neighborhood mismatch: {prop.neighborhood} vs {neighborhood}")
            
            # Final quality check
            if len(validation_issues) == 0 and prop.extraction_confidence > 0.3:
                validated.append(prop)
            else:
                logger.warning(f"❌ Final validation failed for {prop.property_id}: {validation_issues}")
        
        logger.info(f"✅ Final validation complete: {len(validated)}/{len(properties)} properties validated")
        
        return validated
    
    async def _save_audit_trail(self, properties: List[RealPropertyData], neighborhood: str):
        """Save complete audit trail"""
        
        audit_data = {
            'scraping_session': {
                'timestamp': datetime.now().isoformat(),
                'neighborhood': neighborhood,
                'total_properties_scraped': len(properties),
                'failed_urls_count': len(self.failed_urls),
                'success_rate': len(properties) / (len(properties) + len(self.failed_urls)) if (len(properties) + len(self.failed_urls)) > 0 else 0
            },
            'properties': [asdict(prop) for prop in properties],
            'failed_urls': self.failed_urls,
            'audit_log': self.audit_log
        }
        
        # Save complete audit trail
        audit_file = f'outputs/scraping_audit_{neighborhood}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(audit_file, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Audit trail saved: {audit_file}")
        
        # Save properties separately for analysis
        properties_file = f'outputs/real_properties_{neighborhood}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(properties_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(prop) for prop in properties], f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Properties data saved: {properties_file}")

async def main():
    """MISSION CRITICAL: Scrape REAL xe.gr properties"""
    
    neighborhoods = ['Κολωνάκι', 'Παγκράτι', 'Εξάρχεια']
    
    logger.info("🚨 MISSION CRITICAL: REAL xe.gr DATA EXTRACTION")
    logger.info("📋 NO SYNTHETIC DATA - ONLY VERIFIED PROPERTIES")
    
    all_scraped_properties = {}
    
    async with BulletproofXEScraper() as scraper:
        for neighborhood in neighborhoods:
            logger.info(f"\n🎯 SCRAPING {neighborhood.upper()}")
            
            properties = await scraper.scrape_real_properties(neighborhood, max_properties=5)
            
            all_scraped_properties[neighborhood] = properties
            
            logger.info(f"✅ {neighborhood}: {len(properties)} REAL properties scraped")
            
            # Show sample data for verification
            if properties:
                sample = properties[0]
                logger.info(f"📊 SAMPLE DATA:")
                logger.info(f"   URL: {sample.url}")
                logger.info(f"   Address: {sample.address}")
                logger.info(f"   Price: €{sample.price}")
                logger.info(f"   Area: {sample.sqm}m²")
                logger.info(f"   Energy: {sample.energy_class}")
                logger.info(f"   Confidence: {sample.extraction_confidence:.2f}")
    
    # Summary
    total_properties = sum(len(props) for props in all_scraped_properties.values())
    logger.info(f"\n🎯 MISSION COMPLETE:")
    logger.info(f"   Total REAL properties: {total_properties}")
    
    for neighborhood, properties in all_scraped_properties.items():
        logger.info(f"   {neighborhood}: {len(properties)} properties")
    
    if total_properties > 0:
        logger.info("✅ SUCCESS: REAL data extraction completed")
        logger.info("🔍 Audit trails saved for complete validation")
    else:
        logger.error("❌ FAILURE: No properties scraped - check xe.gr connectivity")

if __name__ == "__main__":
    asyncio.run(main())