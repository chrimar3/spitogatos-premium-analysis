"""
XE.GR Professional Scraper Configuration
"""

import os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ScraperConfig:
    # Target settings
    base_url: str = "https://xe.gr"
    neighborhoods: List[str] = None
    max_properties_per_area: int = 10
    
    # Concurrency settings
    max_workers: int = 5
    producer_delay: float = 2.0
    consumer_delay: float = 1.5
    
    # Browser settings
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    # Proxy settings
    proxy_list: List[str] = None
    
    # Output settings
    output_dir: str = "outputs"
    
    def __post_init__(self):
        if self.neighborhoods is None:
            # 10 major Athens neighborhoods/city blocks
            self.neighborhoods = [
                'Κολωνάκι',     # Kolonaki - upscale central area
                'Παγκράτι',     # Pangrati - trendy neighborhood  
                'Εξάρχεια',     # Exarchia - bohemian area
                'Πλάκα',        # Plaka - historic old town
                'Ψυρρή',        # Psyrri - nightlife district
                'Κυψέλη',       # Kypseli - residential area
                'Αμπελόκηποι',  # Ambelokipi - central district
                'Γκάζι',        # Gazi - industrial turned trendy
                'Νέος Κόσμος',  # Neos Kosmos - south central
                'Πετράλωνα'     # Petralona - traditional area
            ]
        
        os.makedirs(self.output_dir, exist_ok=True)

config = ScraperConfig()