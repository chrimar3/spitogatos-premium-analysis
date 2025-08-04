#!/usr/bin/env python3
"""
Test the Ultimate Scraper with Cloudflare bypass
"""

import asyncio
import logging
from scraper_ultimate import UltimateSpitogatosScraper

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_ultimate_scraper():
    """Test the ultimate scraper with Cloudflare bypass"""
    
    print("🚀 Testing Ultimate Spitogatos Scraper")
    print("🛡️ With Advanced Cloudflare Bypass")
    print("=" * 60)
    
    async with UltimateSpitogatosScraper() as scraper:
        print("✅ Ultimate scraper initialized")
        
        # Test locations
        test_locations = [
            "Kolonaki, Athens",
            "Pangrati, Athens", 
            "Exarchia, Athens"
        ]
        
        for location in test_locations:
            print(f"\n🎯 Testing: {location}")
            print("-" * 40)
            
            try:
                properties = await scraper.search_properties(location, max_pages=2)
                
                print(f"📊 Results for {location}:")
                print(f"   Properties found: {len(properties)}")
                
                if properties:
                    print(f"   ✅ SUCCESS! Sample properties:")
                    for i, prop in enumerate(properties[:3]):  # Show first 3
                        print(f"     {i+1}. {prop.title[:50]}...")
                        if prop.price:
                            print(f"        Price: €{prop.price:,}")
                        if prop.sqm:
                            print(f"        Area: {prop.sqm} m²")
                        if prop.url:
                            print(f"        URL: {prop.url}")
                        print()
                else:
                    print(f"   ⚠️ No properties found")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()
            
            # Delay between tests
            print("⏳ Waiting before next test...")
            await asyncio.sleep(10)
        
        # Show final statistics
        print("\n" + "=" * 60)
        scraper.log_statistics()

if __name__ == "__main__":
    asyncio.run(test_ultimate_scraper())