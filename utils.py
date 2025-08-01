"""
Utility functions for Spitogatos Premium Analysis
Advanced data processing, validation, and helper functions
"""

import os
import re
import time
import random
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from unidecode import unidecode
from fuzzywuzzy import fuzz, process
import json

@dataclass
class PropertyData:
    """Structured property data container"""
    id: str
    url: str
    title: str
    address: str
    price: Optional[float]
    sqm: Optional[float]
    energy_class: Optional[str]
    floor: Optional[int]
    rooms: Optional[int]
    latitude: Optional[float]
    longitude: Optional[float]
    description: str
    images: List[str]
    scraped_at: datetime
    confidence_score: float
    validation_flags: List[str]
    source: str = "spitogatos"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'address': self.address,
            'price': self.price,
            'sqm': self.sqm,
            'energy_class': self.energy_class,
            'floor': self.floor,
            'rooms': self.rooms,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'description': self.description,
            'images': self.images,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'confidence_score': self.confidence_score,
            'validation_flags': self.validation_flags,
            'source': self.source
        }

@dataclass 
class BuildingBlock:
    """Building block analysis container"""
    id: str
    name: str
    properties: List[PropertyData]
    center_lat: float
    center_lon: float
    weighted_energy_class: str
    confidence_interval: Dict[str, float]
    sample_size: int
    completeness_score: float
    validation_score: float
    analysis_timestamp: datetime
    
class AddressProcessor:
    """Advanced address processing and normalization"""
    
    def __init__(self):
        self.geocoder = Nominatim(user_agent="spitogatos_premium_analysis")
        self.address_cache = {}
        
    @staticmethod
    def normalize_address(address: str) -> str:
        """Normalize Greek address for better matching"""
        if not address:
            return ""
            
        # Convert to lowercase and remove accents
        normalized = unidecode(address.lower())
        
        # Common Greek address patterns
        replacements = {
            'odos': 'οδός',
            'plateia': 'πλατεία', 
            'leoforos': 'λεωφόρος',
            'agiou': 'αγίου',
            'agias': 'αγίας',
            'str.': 'οδός',
            'ave.': 'λεωφόρος'
        }
        
        for eng, gr in replacements.items():
            normalized = normalized.replace(eng, gr)
            
        # Remove extra whitespace and punctuation
        normalized = re.sub(r'[,.-]+', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def extract_street_number(self, address: str) -> Tuple[str, Optional[int]]:
        """Extract street name and number from address"""
        # Pattern to match Greek addresses
        pattern = r'^(.+?)\s+(\d+)'
        match = re.match(pattern, address.strip())
        
        if match:
            street = match.group(1).strip()
            number = int(match.group(2))
            return street, number
        
        return address.strip(), None
    
    def geocode_address_cached(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode address with caching"""
        if address in self.address_cache:
            return self.address_cache[address]
            
        try:
            # Add Athens, Greece context for better results
            full_address = f"{address}, Athens, Greece"
            location = self.geocoder.geocode(full_address, timeout=10)
            
            if location:
                coords = (location.latitude, location.longitude)
                self.address_cache[address] = coords
                return coords
                
        except Exception as e:
            logging.warning(f"Geocoding failed for {address}: {e}")
            
        self.address_cache[address] = None
        return None
    
    def calculate_address_similarity(self, addr1: str, addr2: str) -> float:
        """Calculate similarity between two addresses"""
        norm1 = self.normalize_address(addr1)
        norm2 = self.normalize_address(addr2)
        
        # Use multiple similarity metrics
        ratio = fuzz.ratio(norm1, norm2)
        token_sort = fuzz.token_sort_ratio(norm1, norm2)
        token_set = fuzz.token_set_ratio(norm1, norm2)
        
        # Weighted average (token_set is most reliable for addresses)
        similarity = (ratio * 0.2 + token_sort * 0.3 + token_set * 0.5) / 100.0
        
        return similarity

class DataValidator:
    """Comprehensive data validation and quality assessment"""
    
    def __init__(self, config):
        self.config = config
        self.energy_patterns = config.ENERGY_CLASS_PATTERNS
        self.validation_patterns = config.VALIDATION_PATTERNS
        
    def validate_energy_class(self, energy_class: str) -> Tuple[bool, float, str]:
        """Validate and normalize energy class"""
        if not energy_class:
            return False, 0.0, ""
            
        energy_class = energy_class.strip().upper()
        
        # Check against known patterns
        for class_name, pattern in self.energy_patterns.items():
            if re.search(pattern, energy_class, re.IGNORECASE):
                confidence = 0.9 if class_name != 'Exempt' else 0.7
                return True, confidence, class_name
                
        # Check for partial matches
        valid_classes = ['A+', 'A', 'B+', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        best_match = process.extractOne(energy_class, valid_classes)
        
        if best_match and best_match[1] > 80:
            return True, 0.6, best_match[0]
            
        return False, 0.0, energy_class
    
    def validate_sqm(self, sqm_text: str) -> Tuple[bool, Optional[float], float]:
        """Validate and extract square meters"""
        if not sqm_text:
            return False, None, 0.0
            
        # Extract numeric value
        match = re.search(self.validation_patterns['sqm'], sqm_text)
        if not match:
            return False, None, 0.0
            
        try:
            sqm = float(match.group(1))
            
            # Reasonable range check (20-500 sqm)
            if 20 <= sqm <= 500:
                confidence = 0.9
            elif 10 <= sqm <= 1000:
                confidence = 0.7
            else:
                confidence = 0.3
                
            return True, sqm, confidence
            
        except ValueError:
            return False, None, 0.0
    
    def validate_price(self, price_text: str) -> Tuple[bool, Optional[float], float]:
        """Validate and extract price"""
        if not price_text:
            return False, None, 0.0
            
        # Clean price text
        price_text = price_text.replace('€', '').replace(',', '').replace('.', '')
        
        match = re.search(r'(\d+)', price_text)
        if not match:
            return False, None, 0.0
            
        try:
            price = float(match.group(1))
            
            # Reasonable range check (30k - 5M euros)
            if 30000 <= price <= 5000000:
                confidence = 0.9
            elif 10000 <= price <= 10000000:
                confidence = 0.7
            else:
                confidence = 0.3
                
            return True, price, confidence
            
        except ValueError:
            return False, None, 0.0
    
    def calculate_property_confidence(self, property_data: PropertyData) -> float:
        """Calculate overall confidence score for property data"""
        scores = []
        weights = []
        
        # Address confidence (always important)
        if property_data.address:
            scores.append(0.9)
            weights.append(0.3)
            
        # Energy class confidence
        if property_data.energy_class:
            is_valid, confidence, _ = self.validate_energy_class(property_data.energy_class)
            scores.append(confidence if is_valid else 0.0)
            weights.append(0.25)
            
        # Area confidence
        if property_data.sqm:
            is_valid, _, confidence = self.validate_sqm(str(property_data.sqm))
            scores.append(confidence if is_valid else 0.0)
            weights.append(0.2)
            
        # Price confidence
        if property_data.price:
            is_valid, _, confidence = self.validate_price(str(property_data.price))
            scores.append(confidence if is_valid else 0.0)
            weights.append(0.15)
            
        # Location confidence
        if property_data.latitude and property_data.longitude:
            scores.append(0.8)
            weights.append(0.1)
            
        if not scores:
            return 0.0
            
        # Calculate weighted average
        weighted_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        return min(1.0, max(0.0, weighted_score))

class StatisticalAnalyzer:
    """Advanced statistical analysis for building blocks"""
    
    @staticmethod
    def calculate_weighted_energy_class(properties: List[PropertyData]) -> Tuple[str, Dict[str, float]]:
        """Calculate weighted energy class for building block"""
        if not properties:
            return "Unknown", {"confidence": 0.0}
            
        # Count properties by energy class
        energy_counts = {}
        total_sqm = 0
        total_properties = 0
        
        for prop in properties:
            if prop.energy_class and prop.sqm:
                energy_counts[prop.energy_class] = energy_counts.get(prop.energy_class, 0) + prop.sqm
                total_sqm += prop.sqm
                total_properties += 1
        
        if not energy_counts:
            return "Unknown", {"confidence": 0.0}
            
        # Calculate weighted percentages
        energy_percentages = {k: v / total_sqm for k, v in energy_counts.items()}
        
        # Find dominant energy class
        dominant_class = max(energy_percentages.items(), key=lambda x: x[1])
        
        # Calculate confidence based on dominance and sample size
        dominance = dominant_class[1]
        sample_confidence = min(1.0, total_properties / 10)  # Confidence improves with sample size
        
        confidence = dominance * sample_confidence
        
        confidence_interval = {
            "lower": max(0.0, confidence - 0.1),
            "upper": min(1.0, confidence + 0.1),
            "confidence": confidence,
            "sample_size": total_properties,
            "coverage": total_properties / len(properties) if properties else 0
        }
        
        return dominant_class[0], confidence_interval
    
    @staticmethod
    def detect_outliers(values: List[float], method: str = "iqr") -> List[int]:
        """Detect outliers in numerical data"""
        if len(values) < 4:
            return []
            
        values_array = np.array(values)
        
        if method == "iqr":
            q1 = np.percentile(values_array, 25)
            q3 = np.percentile(values_array, 75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = [i for i, v in enumerate(values) if v < lower_bound or v > upper_bound]
            
        elif method == "zscore":
            mean = np.mean(values_array)
            std = np.std(values_array)
            z_scores = np.abs((values_array - mean) / std)
            outliers = [i for i, z in enumerate(z_scores) if z > 3]
            
        return outliers

class CacheManager:
    """Intelligent caching system for requests and data"""
    
    def __init__(self, cache_dir: str = "cache", max_age_hours: int = 24):
        self.cache_dir = cache_dir
        self.max_age_hours = max_age_hours
        os.makedirs(cache_dir, exist_ok=True)
        
    def _get_cache_path(self, key: str) -> str:
        """Get cache file path for key"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.json")
        
    def get(self, key: str) -> Optional[Any]:
        """Get cached data if valid"""
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                
            # Check if cache is still valid
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cached_time > timedelta(hours=self.max_age_hours):
                os.remove(cache_path)
                return None
                
            return cached_data['data']
            
        except (json.JSONDecodeError, OSError, KeyError):
            return None
            
    def set(self, key: str, data: Any) -> None:
        """Cache data with timestamp"""
        cache_path = self._get_cache_path(key)
        
        cache_content = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_content, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logging.warning(f"Failed to cache data: {e}")

class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
        
    def start_timer(self, operation: str) -> None:
        """Start timing an operation"""
        self.start_times[operation] = time.time()
        
    def end_timer(self, operation: str) -> float:
        """End timing and record duration"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(duration)
            
            del self.start_times[operation]
            return duration
        return 0.0
        
    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for an operation"""
        if operation not in self.metrics or not self.metrics[operation]:
            return {}
            
        times = self.metrics[operation]
        return {
            'count': len(times),
            'total': sum(times),
            'average': sum(times) / len(times),
            'min': min(times),
            'max': max(times),
            'median': sorted(times)[len(times) // 2]
        }
        
    def log_summary(self) -> None:
        """Log performance summary"""
        logging.info("=== Performance Summary ===")
        for operation in self.metrics:
            stats = self.get_stats(operation)
            logging.info(f"{operation}: avg={stats.get('average', 0):.2f}s, "
                        f"count={stats.get('count', 0)}, "
                        f"total={stats.get('total', 0):.2f}s")

def setup_logging(config) -> None:
    """Setup comprehensive logging system"""
    log_dir = config.OUTPUT_CONFIG['logs_directory']
    os.makedirs(log_dir, exist_ok=True)
    
    # Create formatters
    formatter = logging.Formatter(config.LOGGING_CONFIG['format'])
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOGGING_CONFIG['level']))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_file = os.path.join(log_dir, f"spitogatos_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logging.info("Logging system initialized")

def generate_property_id(url: str, address: str) -> str:
    """Generate unique property ID"""
    combined = f"{url}_{address}".encode('utf-8')
    return hashlib.md5(combined).hexdigest()

def safe_sleep(min_seconds: float, max_seconds: float) -> None:
    """Sleep for a random duration within range"""
    duration = random.uniform(min_seconds, max_seconds)
    time.sleep(duration)

def create_output_directories(config) -> None:
    """Create all necessary output directories"""
    base_dir = config.OUTPUT_CONFIG['base_directory']
    
    directories = [
        base_dir,
        os.path.join(base_dir, config.OUTPUT_CONFIG['data_directory']),
        os.path.join(base_dir, config.OUTPUT_CONFIG['reports_directory']),
        os.path.join(base_dir, config.OUTPUT_CONFIG['logs_directory']),
        os.path.join(base_dir, config.OUTPUT_CONFIG['exports_directory'])
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
    logging.info(f"Output directories created in {base_dir}")

# Initialize global utilities
address_processor = AddressProcessor()
performance_monitor = PerformanceMonitor()