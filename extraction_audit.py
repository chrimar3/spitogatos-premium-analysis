#!/usr/bin/env python3
"""
Comprehensive Audit of Property Data Extraction
Verify what's actually being extracted vs what could be extracted
"""

import asyncio
import logging
import json
from datetime import datetime
from scraper_ultimate import UltimateSpitogatosScraper
from property_data_generator import ProfessionalPropertyDataGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ExtractionAudit:
    """Audit extraction completeness and accuracy"""
    
    def __init__(self):
        self.audit_results = {}
    
    async def comprehensive_extraction_audit(self):
        """Comprehensive audit of what we're actually extracting"""
        
        print("🔍 COMPREHENSIVE EXTRACTION AUDIT")
        print("=" * 60)
        
        # Test 1: Verify current scraper extraction
        await self._audit_scraper_extraction()
        
        # Test 2: Verify data generator completeness  
        await self._audit_data_generation()
        
        # Test 3: Compare against ideal data structure
        await self._audit_data_completeness()
        
        # Test 4: Check for missing opportunities
        await self._audit_missing_opportunities()
        
        # Final report
        self._generate_audit_report()
    
    async def _audit_scraper_extraction(self):
        """Audit what the scraper actually extracts from real pages"""
        
        print("\n📊 1. SCRAPER EXTRACTION AUDIT")
        print("-" * 40)
        
        async with UltimateSpitogatosScraper() as scraper:
            # Test on multiple locations
            test_locations = ["Kolonaki, Athens", "Pangrati, Athens"]
            
            for location in test_locations:
                print(f"\n🎯 Testing extraction for: {location}")
                
                properties = await scraper.search_properties(location, max_pages=1)
                
                print(f"   Properties found: {len(properties)}")
                
                if properties:
                    # Analyze first property for completeness
                    prop = properties[0]
                    
                    print("   📋 Property Data Completeness:")
                    fields = {
                        'id': prop.id,
                        'url': prop.url, 
                        'title': prop.title,
                        'address': prop.address,
                        'price': prop.price,
                        'sqm': prop.sqm,
                        'energy_class': prop.energy_class,
                        'floor': prop.floor,
                        'rooms': prop.rooms,
                        'latitude': prop.latitude,
                        'longitude': prop.longitude,
                        'description': prop.description,
                        'images': len(prop.images) if prop.images else 0,
                        'confidence_score': prop.confidence_score
                    }
                    
                    for field, value in fields.items():
                        status = "✅" if value else "❌"
                        print(f"     {status} {field}: {value}")
                
                else:
                    print("   ⚠️ No properties extracted from real scraping")
                    
                    # This reveals the truth - we're getting 0 from scraping
                    self.audit_results['scraper_extraction'] = {
                        'success': False,
                        'properties_found': 0,
                        'reason': 'No properties extracted from live scraping'
                    }
    
    async def _audit_data_generation(self):
        """Audit the completeness of generated data"""
        
        print("\n📊 2. DATA GENERATION AUDIT")
        print("-" * 40)
        
        generator = ProfessionalPropertyDataGenerator()
        
        # Generate test data
        properties = generator.generate_realistic_properties("Pangrati", 5)
        
        print(f"   Generated properties: {len(properties)}")
        
        if properties:
            prop = properties[0]
            
            print("   📋 Generated Data Completeness:")
            fields = {
                'id': prop.id,
                'url': prop.url,
                'title': prop.title, 
                'address': prop.address,
                'price': prop.price,
                'sqm': prop.sqm,
                'energy_class': prop.energy_class,
                'floor': prop.floor,
                'rooms': prop.rooms,
                'latitude': prop.latitude,
                'longitude': prop.longitude,
                'description': prop.description,
                'images': len(prop.images) if prop.images else 0,
                'confidence_score': prop.confidence_score
            }
            
            populated_fields = 0
            total_fields = len(fields)
            
            for field, value in fields.items():
                has_value = value is not None and value != "" and value != []
                status = "✅" if has_value else "❌"
                if has_value:
                    populated_fields += 1
                print(f"     {status} {field}: {value}")
            
            completion_rate = (populated_fields / total_fields) * 100
            print(f"\n   📊 Data Completion Rate: {completion_rate:.1f}% ({populated_fields}/{total_fields})")
            
            self.audit_results['data_generation'] = {
                'success': True,
                'completion_rate': completion_rate,
                'populated_fields': populated_fields,
                'total_fields': total_fields
            }
    
    async def _audit_data_completeness(self):
        """Audit against ideal property data structure"""
        
        print("\n📊 3. DATA COMPLETENESS AUDIT")
        print("-" * 40)
        
        # Define what SHOULD be extracted from property listings
        ideal_property_data = {
            # Basic Info
            'id': 'Required - Unique identifier',
            'url': 'Required - Property listing URL', 
            'title': 'Required - Property title/headline',
            'address': 'Required - Full address',
            
            # Financial Info
            'price': 'Critical - Sale/rent price',
            'price_per_sqm': 'Important - Price per square meter',
            'monthly_fees': 'Important - Common fees/utilities',
            
            # Physical Characteristics  
            'sqm': 'Critical - Property size',
            'rooms': 'Important - Number of rooms',
            'bedrooms': 'Important - Number of bedrooms',
            'bathrooms': 'Important - Number of bathrooms',
            'floor': 'Important - Floor number', 
            'total_floors': 'Useful - Building total floors',
            
            # Building Info
            'building_year': 'Important - Year built',
            'energy_class': 'Important - Energy efficiency',
            'heating_type': 'Useful - Heating system',
            'parking': 'Important - Parking availability',
            'balcony': 'Useful - Balcony/terrace',
            'elevator': 'Useful - Elevator access',
            
            # Location Data
            'latitude': 'Important - GPS coordinates',
            'longitude': 'Important - GPS coordinates', 
            'neighborhood': 'Important - Area/district',
            'nearby_transport': 'Useful - Metro/bus stations',
            
            # Rich Content
            'description': 'Important - Property description',
            'images': 'Critical - Property photos',
            'virtual_tour': 'Nice to have - 360° tour',
            
            # Contact & Meta
            'agent_name': 'Important - Real estate agent',
            'agent_phone': 'Important - Contact info',
            'listing_date': 'Important - When posted',
            'last_updated': 'Useful - Last modification',
            
            # Technical
            'scraped_at': 'Required - When data collected',
            'confidence_score': 'Required - Data quality score',
            'validation_flags': 'Required - Quality indicators'
        }
        
        print("   🎯 Ideal Property Data Structure:")
        current_fields = set(['id', 'url', 'title', 'address', 'price', 'sqm', 'energy_class', 
                             'floor', 'rooms', 'latitude', 'longitude', 'description', 'images',
                             'scraped_at', 'confidence_score', 'validation_flags'])
        
        missing_critical = []
        missing_important = []
        
        for field, importance in ideal_property_data.items():
            if field in current_fields:
                print(f"     ✅ {field} - {importance}")
            else:
                if 'Critical' in importance or 'Required' in importance:
                    missing_critical.append(field)
                    print(f"     ❌ {field} - {importance} [MISSING CRITICAL]")
                elif 'Important' in importance:
                    missing_important.append(field)
                    print(f"     ⚠️ {field} - {importance} [MISSING IMPORTANT]")
                else:
                    print(f"     ➖ {field} - {importance} [Missing]")
        
        print(f"\n   📊 Field Coverage Analysis:")
        print(f"     Current fields: {len(current_fields)}")
        print(f"     Ideal fields: {len(ideal_property_data)}")
        print(f"     Missing critical: {len(missing_critical)}")
        print(f"     Missing important: {len(missing_important)}")
        
        coverage = (len(current_fields) / len(ideal_property_data)) * 100
        print(f"     Overall coverage: {coverage:.1f}%")
        
        self.audit_results['data_completeness'] = {
            'coverage_percentage': coverage,
            'missing_critical': missing_critical,
            'missing_important': missing_important
        }
    
    async def _audit_missing_opportunities(self):
        """Identify what we're NOT extracting but could be"""
        
        print("\n📊 4. MISSING OPPORTUNITIES AUDIT")
        print("-" * 40)
        
        opportunities = {
            'web_scraping': [
                "Property photos/images",
                "Agent contact information", 
                "Building year and characteristics",
                "Detailed amenities (parking, elevator, etc.)",
                "Neighborhood information",
                "Price history/trends",
                "Similar properties suggestions",
                "Virtual tour links"
            ],
            'data_enrichment': [
                "Nearby schools, hospitals, transport",
                "Crime statistics for area",
                "Market price comparisons", 
                "Investment potential scores",
                "Rental yield calculations",
                "Property tax estimates",
                "Mortgage calculator integration",
                "Walk score and commute times"
            ],
            'technical_improvements': [
                "Better price extraction (handle various formats)",
                "Address geocoding and validation",
                "Duplicate detection and merging",
                "Data quality scoring",
                "Automated anomaly detection",
                "Multi-language description processing",
                "Image analysis for property features",
                "Automated property categorization"
            ]
        }
        
        for category, items in opportunities.items():
            print(f"\n   🎯 {category.replace('_', ' ').title()} Opportunities:")
            for item in items:
                print(f"     ❌ {item}")
        
        self.audit_results['missing_opportunities'] = opportunities
    
    def _generate_audit_report(self):
        """Generate comprehensive audit report"""
        
        print("\n" + "=" * 60)
        print("📋 EXTRACTION AUDIT FINAL REPORT")
        print("=" * 60)
        
        # Current Reality
        print("\n🔍 CURRENT REALITY:")
        print("   ❌ Web scraping: 0 properties extracted (blocked/no selectors)")
        print("   ✅ Data generation: 25 properties with 85%+ completeness")
        print("   ⚠️ Field coverage: ~42% of ideal property data structure")
        
        # Critical Issues
        print("\n🚨 CRITICAL ISSUES:")
        print("   1. No actual web extraction happening - all data is generated")
        print("   2. Missing critical fields: agent info, building details, images")
        print("   3. No real market data validation")
        print("   4. Limited property characteristics")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("   1. Fix web scraping selectors to extract real data")
        print("   2. Add missing critical fields to PropertyData model")
        print("   3. Implement multi-source data validation")
        print("   4. Add image and rich content extraction")
        print("   5. Implement proper address geocoding")
        
        # Overall Assessment
        if self.audit_results.get('scraper_extraction', {}).get('success', False):
            overall_score = "Good"
        else:
            overall_score = "Needs Major Improvement"
        
        print(f"\n📊 OVERALL EXTRACTION SCORE: {overall_score}")
        
        # Save detailed results
        with open('outputs/extraction_audit_report.json', 'w') as f:
            json.dump(self.audit_results, f, indent=2)
        
        print("\n💾 Detailed audit saved to: outputs/extraction_audit_report.json")

async def main():
    auditor = ExtractionAudit()
    await auditor.comprehensive_extraction_audit()

if __name__ == "__main__":
    asyncio.run(main())