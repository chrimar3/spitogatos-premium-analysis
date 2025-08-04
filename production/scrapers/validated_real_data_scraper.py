#!/usr/bin/env python3
"""
Validated Real Data Scraper - STRICT VALIDATION ONLY
Only accepts properties with verified real data - removes all suspicious/fake data
"""

import asyncio
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from utils import PropertyData, generate_property_id
from xe_gr_enhanced_extractor import XEGREnhancedExtractor

logging.basicConfig(level=logging.INFO)

class ValidatedRealDataScraper:
    """Scraper with STRICT validation - only real, verified data allowed"""
    
    def __init__(self):
        self.xe_extractor = XEGREnhancedExtractor()
        
        # Strict validation criteria
        self.validation_criteria = {
            'min_price': 50,           # Minimum €50 
            'max_price': 5000000,      # Maximum €5M
            'min_sqm': 10,             # Minimum 10m²
            'max_sqm': 500,            # Maximum 500m²
            'min_price_per_sqm': 100,  # Minimum €100/m²
            'max_price_per_sqm': 8000, # Maximum €8000/m² (Athens realistic)
            
            # Realistic Athens energy distribution expectations
            'expected_energy_distribution': {
                'A+': 0.05,  # 5% modern buildings
                'A': 0.10,   # 10% renovated/new
                'B': 0.15,   # 15% good condition
                'C': 0.35,   # 35% average (most common)
                'D': 0.25,   # 25% older buildings
                'E': 0.10,   # 10% old buildings
                'F': 0.00    # 0% very old/poor
            }
        }
        
        logging.info("🔒 VALIDATED REAL DATA SCRAPER - Strict validation only")
    
    async def get_strictly_validated_properties(self, area_name: str) -> List[PropertyData]:
        """Get only strictly validated real properties - no fake data allowed"""
        
        logging.info(f"🔒 STRICT VALIDATION EXTRACTION for {area_name}")
        logging.info(f"📋 Criteria: Only verified real data, no defaults, no suspicious patterns")
        
        # Extract raw properties (smaller sample for testing)
        raw_properties = await self.xe_extractor.extract_all_real_properties(area_name, 50)
        
        if not raw_properties:
            logging.warning(f"❌ No raw properties extracted for {area_name}")
            return []
        
        logging.info(f"📊 Raw extraction: {len(raw_properties)} properties")
        
        # Apply strict validation filters
        validated_properties = []
        
        for prop in raw_properties:
            validation_result = self._strict_property_validation(prop)
            
            if validation_result['is_valid']:
                # Clean the property data
                cleaned_prop = self._clean_property_data(prop, validation_result)
                validated_properties.append(cleaned_prop)
            else:
                logging.debug(f"❌ Rejected {prop.id}: {validation_result['rejection_reason']}")
        
        # Additional cross-validation
        final_properties = self._cross_validate_property_set(validated_properties, area_name)
        
        # Final statistics
        self._log_validation_statistics(raw_properties, final_properties, area_name)
        
        return final_properties
    
    def _strict_property_validation(self, prop: PropertyData) -> Dict[str, Any]:
        """Apply strict validation to a single property"""
        
        validation_result = {
            'is_valid': True,
            'rejection_reason': None,
            'warnings': [],
            'data_quality_score': 0
        }
        
        # VALIDATION 1: Price validation
        if not prop.price or prop.price <= 0:
            validation_result['is_valid'] = False
            validation_result['rejection_reason'] = "No valid price data"
            return validation_result
        
        if prop.price < self.validation_criteria['min_price']:
            validation_result['is_valid'] = False
            validation_result['rejection_reason'] = f"Price too low: €{prop.price}"
            return validation_result
        
        if prop.price > self.validation_criteria['max_price']:
            validation_result['is_valid'] = False
            validation_result['rejection_reason'] = f"Price too high: €{prop.price}"
            return validation_result
        
        validation_result['data_quality_score'] += 2  # Valid price
        
        # VALIDATION 2: Area validation
        if not prop.sqm or prop.sqm <= 0:
            validation_result['is_valid'] = False
            validation_result['rejection_reason'] = "No valid area data"
            return validation_result
        
        if prop.sqm < self.validation_criteria['min_sqm']:
            validation_result['is_valid'] = False
            validation_result['rejection_reason'] = f"Area too small: {prop.sqm}m²"
            return validation_result
        
        if prop.sqm > self.validation_criteria['max_sqm']:
            validation_result['is_valid'] = False
            validation_result['rejection_reason'] = f"Area too large: {prop.sqm}m²"
            return validation_result
        
        validation_result['data_quality_score'] += 2  # Valid area
        
        # VALIDATION 3: Price per sqm validation
        price_per_sqm = prop.price / prop.sqm
        
        if price_per_sqm < self.validation_criteria['min_price_per_sqm']:
            validation_result['is_valid'] = False
            validation_result['rejection_reason'] = f"Price per m² too low: €{price_per_sqm:.0f}/m²"
            return validation_result
        
        if price_per_sqm > self.validation_criteria['max_price_per_sqm']:
            validation_result['is_valid'] = False
            validation_result['rejection_reason'] = f"Price per m² too high: €{price_per_sqm:.0f}/m²"
            return validation_result
        
        validation_result['data_quality_score'] += 2  # Valid price/sqm ratio
        
        # VALIDATION 4: Energy class validation (STRICT)
        if prop.energy_class:
            # Check if energy class appears to be real or just a default
            if self._is_energy_class_suspicious(prop):
                validation_result['warnings'].append("Energy class appears suspicious - removing")
                # Don't reject, just clean the energy class
            else:
                validation_result['data_quality_score'] += 1  # Valid energy class
        
        # VALIDATION 5: Description validation
        if not prop.description or len(prop.description.strip()) < 10:
            validation_result['warnings'].append("Minimal description data")
        else:
            # Check if description contains real property information
            if self._validate_description_content(prop.description):
                validation_result['data_quality_score'] += 1
        
        # VALIDATION 6: Source validation
        if not prop.validation_flags or not any('xe_gr' in flag for flag in prop.validation_flags):
            validation_result['is_valid'] = False
            validation_result['rejection_reason'] = "Not from verified xe.gr source"
            return validation_result
        
        # Minimum quality score required
        if validation_result['data_quality_score'] < 4:  # Must have price + area + ratio + source
            validation_result['is_valid'] = False
            validation_result['rejection_reason'] = f"Insufficient data quality score: {validation_result['data_quality_score']}/6"
            return validation_result
        
        return validation_result
    
    def _is_energy_class_suspicious(self, prop: PropertyData) -> bool:
        """Check if energy class appears to be fake/default rather than real"""
        
        if not prop.energy_class:
            return False
        
        # Check 1: If energy class is 'A' but no energy-related text in description
        if prop.energy_class == 'A' and prop.description:
            desc_lower = prop.description.lower()
            energy_keywords = ['energy', 'ενεργ', 'κλάση', 'class', 'efficient', 'rating']
            
            if not any(keyword in desc_lower for keyword in energy_keywords):
                return True  # 'A' rating but no energy mentions = suspicious
        
        # Check 2: If confidence score is high but energy class seems out of place
        if prop.confidence_score and prop.confidence_score > 0.9 and prop.energy_class == 'A':
            # High confidence + A rating is suspicious unless explicitly mentioned
            if prop.description and prop.energy_class.lower() not in prop.description.lower():
                return True
        
        return False
    
    def _validate_description_content(self, description: str) -> bool:
        """Validate that description contains real property information"""
        
        if not description or len(description) < 20:
            return False
        
        desc_lower = description.lower()
        
        # Check for property-related keywords
        property_keywords = [
            # Greek
            'διαμέρισμα', 'κατοικία', 'ακίνητο', 'δωμάτι', 'μπάνιο', 'κουζίνα',
            'μπαλκόνι', 'θέρμανση', 'κλιματισμός', 'όροφος', 'ασανσέρ',
            
            # English
            'apartment', 'house', 'room', 'bathroom', 'kitchen', 'balcony',
            'heating', 'air', 'floor', 'elevator', 'parking'
        ]
        
        keyword_count = sum(1 for keyword in property_keywords if keyword in desc_lower)
        
        # Must have at least 2 property-related keywords to be considered real
        return keyword_count >= 2
    
    def _clean_property_data(self, prop: PropertyData, validation_result: Dict[str, Any]) -> PropertyData:
        """Clean property data based on validation results"""
        
        # Create cleaned copy
        cleaned_prop = PropertyData(
            id=prop.id,
            url=prop.url,
            title=prop.title,
            address=prop.address,
            price=prop.price,
            sqm=prop.sqm,
            energy_class=None,  # Start with None, only set if truly validated
            floor=prop.floor,
            rooms=prop.rooms,
            latitude=prop.latitude,
            longitude=prop.longitude,
            description=prop.description,
            images=prop.images,
            scraped_at=prop.scraped_at,
            confidence_score=0.95,  # High confidence for validated data
            validation_flags=['strictly_validated', 'real_only'],
            source=prop.source
        )
        
        # Only set energy class if it passed strict validation
        if prop.energy_class and not self._is_energy_class_suspicious(prop):
            # Additional check: energy class must appear in description or be contextually valid
            if self._energy_class_contextually_valid(prop):
                cleaned_prop.energy_class = prop.energy_class
                cleaned_prop.validation_flags.append('energy_class_validated')
        
        # Add validation score to flags
        cleaned_prop.validation_flags.append(f'quality_score_{validation_result["data_quality_score"]}')
        
        return cleaned_prop
    
    def _energy_class_contextually_valid(self, prop: PropertyData) -> bool:
        """Check if energy class is contextually valid"""
        
        if not prop.energy_class or not prop.description:
            return False
        
        desc_lower = prop.description.lower()
        energy_class_lower = prop.energy_class.lower()
        
        # Check 1: Energy class appears in description
        if energy_class_lower in desc_lower:
            return True
        
        # Check 2: Energy-related text supports the rating
        if prop.energy_class in ['A+', 'A', 'B']:
            # High ratings should have supporting text
            positive_keywords = ['new', 'modern', 'renovated', 'efficient', 'νέο', 'μοντέρνο', 'ανακαινισμένο']
            if any(keyword in desc_lower for keyword in positive_keywords):
                return True
        
        elif prop.energy_class in ['D', 'E', 'F']:
            # Low ratings should have supporting text or lack of efficiency mentions
            efficiency_keywords = ['efficient', 'modern', 'new', 'energy', 'ενεργειακή']
            if not any(keyword in desc_lower for keyword in efficiency_keywords):
                return True  # No efficiency claims = could be low rating
        
        return False
    
    def _cross_validate_property_set(self, properties: List[PropertyData], area_name: str) -> List[PropertyData]:
        """Cross-validate the entire property set for consistency"""
        
        if not properties:
            return properties
        
        logging.info(f"🔍 Cross-validating {len(properties)} properties for {area_name}")
        
        # Remove statistical outliers
        cleaned_properties = self._remove_statistical_outliers(properties)
        
        # Validate energy class distribution if any energy classes present
        final_properties = self._validate_energy_distribution(cleaned_properties, area_name)
        
        return final_properties
    
    def _remove_statistical_outliers(self, properties: List[PropertyData]) -> List[PropertyData]:
        """Remove statistical outliers in price and area"""
        
        # Price outlier detection
        prices = [p.price for p in properties if p.price]
        if len(prices) >= 5:
            # Use IQR method for outlier detection
            prices_sorted = sorted(prices)
            q1 = prices_sorted[len(prices_sorted)//4]
            q3 = prices_sorted[3*len(prices_sorted)//4]
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # Filter out price outliers
            properties = [p for p in properties if lower_bound <= p.price <= upper_bound]
            logging.info(f"📊 Price outlier removal: {len(prices) - len(properties)} properties removed")
        
        # Area outlier detection
        areas = [p.sqm for p in properties if p.sqm]
        if len(areas) >= 5:
            areas_sorted = sorted(areas)
            q1 = areas_sorted[len(areas_sorted)//4]
            q3 = areas_sorted[3*len(areas_sorted)//4]
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # Filter out area outliers
            original_count = len(properties)
            properties = [p for p in properties if lower_bound <= p.sqm <= upper_bound]
            logging.info(f"📊 Area outlier removal: {original_count - len(properties)} properties removed")
        
        return properties
    
    def _validate_energy_distribution(self, properties: List[PropertyData], area_name: str) -> List[PropertyData]:
        """Validate energy class distribution against realistic expectations"""
        
        properties_with_energy = [p for p in properties if p.energy_class]
        
        if len(properties_with_energy) == 0:
            logging.info(f"📊 No energy class data to validate for {area_name}")
            return properties
        
        # Calculate actual distribution
        energy_counts = {}
        for prop in properties_with_energy:
            energy_counts[prop.energy_class] = energy_counts.get(prop.energy_class, 0) + 1
        
        total_with_energy = len(properties_with_energy)
        actual_distribution = {k: v/total_with_energy for k, v in energy_counts.items()}
        expected_distribution = self.validation_criteria['expected_energy_distribution']
        
        logging.info(f"📊 Energy class distribution for {area_name}:")
        logging.info(f"   Actual: {actual_distribution}")
        
        # Check for unrealistic distributions
        suspicious_patterns = []
        
        # Too many A ratings
        a_percentage = actual_distribution.get('A', 0) + actual_distribution.get('A+', 0)
        expected_a_percentage = expected_distribution.get('A', 0) + expected_distribution.get('A+', 0)
        
        if a_percentage > expected_a_percentage * 3:  # More than 3x expected
            suspicious_patterns.append(f"Too many A ratings: {a_percentage*100:.1f}% (expected ~{expected_a_percentage*100:.1f}%)")
        
        # No low ratings
        low_ratings = actual_distribution.get('D', 0) + actual_distribution.get('E', 0) + actual_distribution.get('F', 0)
        if low_ratings == 0 and total_with_energy > 5:
            suspicious_patterns.append("No D/E/F ratings found (unrealistic for Athens)")
        
        if suspicious_patterns:
            logging.warning(f"🚨 SUSPICIOUS ENERGY DISTRIBUTION detected:")
            for pattern in suspicious_patterns:
                logging.warning(f"   {pattern}")
            
            # If distribution is highly suspicious, remove all energy class data
            if len(suspicious_patterns) >= 2:
                logging.warning(f"🚨 Removing all energy class data due to suspicious patterns")
                for prop in properties:
                    prop.energy_class = None
                    if 'energy_class_validated' in (prop.validation_flags or []):
                        prop.validation_flags.remove('energy_class_validated')
        
        return properties
    
    def _log_validation_statistics(self, raw_properties: List[PropertyData], 
                                 final_properties: List[PropertyData], area_name: str):
        """Log comprehensive validation statistics"""
        
        logging.info(f"\n📊 STRICT VALIDATION RESULTS for {area_name}:")
        logging.info(f"   Raw extracted: {len(raw_properties)} properties")
        logging.info(f"   Validated real: {len(final_properties)} properties")
        logging.info(f"   Validation rate: {len(final_properties)/len(raw_properties)*100:.1f}%")
        
        if final_properties:
            # Data completeness for validated properties
            with_price = len([p for p in final_properties if p.price])
            with_sqm = len([p for p in final_properties if p.sqm])
            with_energy = len([p for p in final_properties if p.energy_class])
            
            logging.info(f"\n✅ VALIDATED DATA QUALITY:")
            logging.info(f"   Price data: {with_price}/{len(final_properties)} (100%)")  # Should be 100% due to validation
            logging.info(f"   Area data: {with_sqm}/{len(final_properties)} (100%)")    # Should be 100% due to validation
            logging.info(f"   Energy class: {with_energy}/{len(final_properties)} ({with_energy/len(final_properties)*100:.1f}%)")
            
            # Price statistics
            prices = [p.price for p in final_properties]
            areas = [p.sqm for p in final_properties]
            price_per_sqm = [p.price/p.sqm for p in final_properties]
            
            logging.info(f"\n📈 VALIDATED STATISTICS:")
            logging.info(f"   Price range: €{min(prices):,.0f} - €{max(prices):,.0f}")
            logging.info(f"   Area range: {min(areas):.0f}m² - {max(areas):.0f}m²")
            logging.info(f"   Price/m² range: €{min(price_per_sqm):.0f} - €{max(price_per_sqm):.0f}")
            
            if with_energy > 0:
                energy_distribution = {}
                for prop in final_properties:
                    if prop.energy_class:
                        energy_distribution[prop.energy_class] = energy_distribution.get(prop.energy_class, 0) + 1
                logging.info(f"   Energy distribution: {energy_distribution}")
            else:
                logging.info(f"   Energy classes: None (all removed as suspicious)")
        
        else:
            logging.warning(f"❌ NO VALID PROPERTIES FOUND after strict validation")


async def main():
    """Test validated real data scraper"""
    
    print("🔒 VALIDATED REAL DATA SCRAPER TEST")
    print("=" * 60)
    print("📋 STRICT VALIDATION - Only verified real data")
    
    scraper = ValidatedRealDataScraper()
    
    # Test area
    area = "Kolonaki"
    
    print(f"\n🔍 Strict validation extraction for {area}")
    
    # Extract only validated real properties
    validated_properties = await scraper.get_strictly_validated_properties(area)
    
    print(f"\n📊 VALIDATION RESULTS:")
    print(f"   Validated properties: {len(validated_properties)}")
    
    if validated_properties:
        print(f"\n✅ SAMPLE VALIDATED PROPERTIES:")
        for i, prop in enumerate(validated_properties[:5]):
            print(f"\n   Property {i+1}:")
            print(f"     Price: €{prop.price:,}")
            print(f"     Area: {prop.sqm}m²")
            print(f"     Price/m²: €{prop.price/prop.sqm:.0f}")
            print(f"     Energy: {prop.energy_class if prop.energy_class else 'N/A (removed as suspicious)'}")
            print(f"     Validation: {prop.validation_flags}")
        
        # Show energy class results
        with_energy = len([p for p in validated_properties if p.energy_class])
        print(f"\n⚡ ENERGY CLASS RESULTS:")
        print(f"   Properties with energy class: {with_energy}/{len(validated_properties)}")
        
        if with_energy > 0:
            energy_dist = {}
            for prop in validated_properties:
                if prop.energy_class:
                    energy_dist[prop.energy_class] = energy_dist.get(prop.energy_class, 0) + 1
            print(f"   Distribution: {energy_dist}")
        else:
            print(f"   All energy class data removed as suspicious/fake")
    
    else:
        print(f"   ❌ No properties passed strict validation")

if __name__ == "__main__":
    asyncio.run(main())