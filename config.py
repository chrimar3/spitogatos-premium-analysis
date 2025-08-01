"""
Configuration module for Spitogatos Premium Analysis
Comprehensive settings for intelligent data collection and analysis
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

@dataclass
class RateLimitConfig:
    """Configuration for intelligent rate limiting"""
    base_delay_seconds: float = 3.0
    random_jitter_max: float = 2.0
    concurrent_sessions: int = 3
    max_retries: int = 3
    exponential_backoff: bool = True
    backoff_multiplier: float = 2.0
    max_delay: float = 60.0

@dataclass
class ScrapingConfig:
    """Configuration for web scraping operations"""
    user_agent_rotation_frequency: int = 10
    session_rotation_frequency: int = 50
    request_timeout: int = 30
    max_concurrent_requests: int = 3
    enable_caching: bool = True
    cache_duration_hours: int = 24
    
@dataclass
class AreaConfig:
    """Configuration for target areas"""
    name: str
    search_strategy: str
    streets: List[Dict[str, Any]]
    expected_properties: int
    quality_threshold: float
    priority: int = 1

@dataclass
class ValidationConfig:
    """Configuration for data validation"""
    data_completeness_threshold: float = 0.85
    address_validation_rate_threshold: float = 0.95
    energy_class_confidence_threshold: float = 0.80
    geocoding_enabled: bool = True
    fuzzy_matching_threshold: float = 0.85
    
@dataclass
class ClusteringConfig:
    """Configuration for building block clustering"""
    address_similarity_threshold: float = 0.85
    coordinate_radius_meters: float = 75.0
    min_properties_per_cluster: int = 4
    clustering_algorithm: str = "dbscan"
    
class Config:
    """Main configuration class for the Spitogatos Premium Analysis system"""
    
    # Project metadata
    PROJECT_NAME = "spitogatos_premium_analysis"
    DELIVERY_DEADLINE_HOURS = 36
    
    # Base URLs and endpoints
    SPITOGATOS_BASE_URL = "https://www.spitogatos.gr"
    SEARCH_ENDPOINT = "/search/results"
    WAYBACK_MACHINE_URL = "https://web.archive.org"
    
    # Rate limiting configuration
    RATE_LIMITS = RateLimitConfig()
    
    # Scraping configuration
    SCRAPING = ScrapingConfig()
    
    # Validation configuration
    VALIDATION = ValidationConfig()
    
    # Clustering configuration  
    CLUSTERING = ClusteringConfig()
    
    # Enhanced target areas with comprehensive coverage
    TARGET_AREAS = [
        AreaConfig(
            name="Kolonaki_Premium",
            search_strategy="exhaustive_luxury_focus",
            streets=[
                {"name": "Skoufa", "range": "25-65", "priority": 1},
                {"name": "Voukourestiou", "range": "5-35", "priority": 1},
                {"name": "Kanari", "range": "15-45", "priority": 2},
                {"name": "Patriarchou Ioakim", "range": "10-40", "priority": 2},
                {"name": "Solonos", "range": "30-70", "priority": 3}
            ],
            expected_properties=40,
            quality_threshold=0.90
        ),
        AreaConfig(
            name="Exarchia_Cultural",
            search_strategy="comprehensive_bohemian_district",
            streets=[
                {"name": "Kallidromiou", "range": "15-55", "priority": 1},
                {"name": "Themistokleous", "range": "45-85", "priority": 1},
                {"name": "Emmanouil Benaki", "range": "65-105", "priority": 2},
                {"name": "Mavromichali", "range": "20-60", "priority": 2},
                {"name": "Dervenion", "range": "5-35", "priority": 3}
            ],
            expected_properties=35,
            quality_threshold=0.85
        ),
        AreaConfig(
            name="Pangrati_Residential",  
            search_strategy="systematic_family_housing",
            streets=[
                {"name": "Ymittou", "range": "35-75", "priority": 1},
                {"name": "Plastira", "range": "5-35", "priority": 1},
                {"name": "Archimidous", "range": "15-45", "priority": 2},
                {"name": "Damareos", "range": "25-65", "priority": 2},
                {"name": "Formionos", "range": "10-40", "priority": 3}
            ],
            expected_properties=45,
            quality_threshold=0.88
        ),
        AreaConfig(
            name="Psyrri_Historic",
            search_strategy="heritage_district_focus",
            streets=[
                {"name": "Aristofanous", "range": "5-25", "priority": 1},
                {"name": "Agion Anargyron", "range": "10-30", "priority": 1},
                {"name": "Karaiskaki", "range": "15-45", "priority": 2},
                {"name": "Pittakou", "range": "1-20", "priority": 2}
            ],
            expected_properties=30,
            quality_threshold=0.82
        )
    ]
    
    # User agents for rotation
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    # Energy class patterns for validation
    ENERGY_CLASS_PATTERNS = {
        'A+': r'A\+',
        'A': r'\bA\b',
        'B+': r'B\+', 
        'B': r'\bB\b',
        'C': r'\bC\b',
        'D': r'\bD\b',
        'E': r'\bE\b',
        'F': r'\bF\b',
        'G': r'\bG\b',
        'H': r'\bH\b',
        'Exempt': r'(?i)(exempt|εξαιρείται|δεν\s+απαιτείται)'
    }
    
    # Data validation patterns
    VALIDATION_PATTERNS = {
        'sqm': r'(\d+(?:\.\d+)?)\s*(?:τ\.μ\.|m²|sqm|τετραγωνικά)',
        'price': r'€?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
        'floor': r'(\d+)(?:ος|ο)?\s*(?:όροφος|floor)',
        'rooms': r'(\d+)\s*(?:δωμάτια|rooms|υπνοδωμάτια)'
    }
    
    # Success metrics
    SUCCESS_METRICS = {
        'minimum_acceptable': {
            'building_blocks_analyzed': 10,
            'properties_per_block_avg': 25,
            'energy_class_coverage': 0.80,
            'data_validation_pass_rate': 0.90,
            'statistical_confidence': 0.95
        },
        'target_excellence': {
            'building_blocks_analyzed': 12,
            'properties_per_block_avg': 35,
            'energy_class_coverage': 0.85,
            'data_validation_pass_rate': 0.95,
            'statistical_confidence': 0.95
        }
    }
    
    # Output configuration
    OUTPUT_CONFIG = {
        'base_directory': 'outputs',
        'data_directory': 'data',
        'reports_directory': 'reports',
        'logs_directory': 'logs',
        'exports_directory': 'exports'
    }
    
    # Logging configuration
    LOGGING_CONFIG = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'handlers': ['file', 'console'],
        'max_file_size_mb': 10,
        'backup_count': 5
    }
    
    @classmethod
    def get_area_by_name(cls, name: str) -> AreaConfig:
        """Get area configuration by name"""
        for area in cls.TARGET_AREAS:
            if area.name == name:
                return area
        raise ValueError(f"Area {name} not found in configuration")
    
    @classmethod
    def get_high_priority_areas(cls) -> List[AreaConfig]:
        """Get areas sorted by priority"""
        return sorted([area for area in cls.TARGET_AREAS if area.priority == 1], 
                     key=lambda x: x.expected_properties, reverse=True)
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        try:
            assert cls.RATE_LIMITS.base_delay_seconds > 0
            assert cls.RATE_LIMITS.concurrent_sessions > 0
            assert cls.VALIDATION.data_completeness_threshold > 0
            assert cls.VALIDATION.data_completeness_threshold <= 1
            assert len(cls.TARGET_AREAS) > 0
            return True
        except AssertionError:
            return False

# Global configuration instance
config = Config()

# Validate configuration on import
if not config.validate_config():
    raise ValueError("Invalid configuration detected. Please check config.py settings.")