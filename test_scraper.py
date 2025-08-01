#!/usr/bin/env python3
"""
Test script for the professional scraper
"""

import asyncio
import logging
from scraper_pro import ProfessionalSpitogatosScraper

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_scraper():
    """Test the professional scraper with a simple search"""
    
    print("🧪 Testing Professional Spitogatos Scraper")
    print("=" * 50)
    
    async with ProfessionalSpitogatosScraper() as scraper:
        print("✅ Scraper initialized successfully")
        
        # Test with a simple area search
        test_location = "Kolonaki, Athens"
        print(f"🔍 Testing search for: {test_location}")
        
        try:
            properties = await scraper.search_properties(test_location, max_pages=2)
            
            print(f"📊 Results:")
            print(f"   Properties found: {len(properties)}")
            
            if properties:
                print(f"   Sample property:")
                sample = properties[0]
                print(f"     Title: {sample.title}")
                print(f"     Price: {sample.price}")
                print(f"     URL: {sample.url}")
            
            # Show statistics
            scraper.log_statistics()
            
        except Exception as e:
            print(f"❌ Error during search: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scraper())