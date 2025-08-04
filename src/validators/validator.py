"""
Comprehensive Statistical Validation Pipeline
Advanced validation, quality assurance, and confidence scoring
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import re

from config import config
from utils import PropertyData, BuildingBlock, AddressProcessor, address_processor

@dataclass
class ValidationResult:
    """Result of validation process"""
    is_valid: bool
    confidence_score: float
    validation_errors: List[str]
    validation_warnings: List[str]
    corrected_value: Any = None
    metadata: Dict[str, Any] = None

@dataclass 
class QualityMetrics:
    """Comprehensive quality metrics for data"""
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    reliability_score: float
    overall_quality_score: float
    sample_size_adequacy: float
    geographic_coverage: float
    temporal_consistency: float

class PropertyValidator:
    """Advanced property-level validation"""
    
    def __init__(self):
        self.config = config
        self.address_processor = address_processor
        self.validation_stats = {
            'properties_validated': 0,
            'validation_passes': 0,
            'validation_failures': 0,
            'corrections_made': 0
        }
        
    def validate_property_comprehensive(self, property_data: PropertyData) -> ValidationResult:
        """Comprehensive validation of property data"""
        
        self.validation_stats['properties_validated'] += 1
        
        errors = []
        warnings = []
        confidence_scores = []
        corrections = {}
        
        # Validate address
        address_result = self._validate_address(property_data.address)
        if not address_result.is_valid:
            errors.extend(address_result.validation_errors)
        else:
            confidence_scores.append(address_result.confidence_score)
            if address_result.corrected_value:
                corrections['address'] = address_result.corrected_value
        
        # Validate energy class
        energy_result = self._validate_energy_class(property_data.energy_class)
        if not energy_result.is_valid:
            warnings.extend(energy_result.validation_warnings)
        else:
            confidence_scores.append(energy_result.confidence_score)
            if energy_result.corrected_value:
                corrections['energy_class'] = energy_result.corrected_value
        
        # Validate price
        price_result = self._validate_price(property_data.price, property_data.sqm)
        if not price_result.is_valid:
            warnings.extend(price_result.validation_warnings)
        else:
            confidence_scores.append(price_result.confidence_score)
        
        # Validate square meters
        sqm_result = self._validate_sqm(property_data.sqm)
        if not sqm_result.is_valid:
            warnings.extend(sqm_result.validation_warnings)
        else:
            confidence_scores.append(sqm_result.confidence_score)
        
        # Validate coordinates
        coord_result = self._validate_coordinates(
            property_data.latitude, property_data.longitude, property_data.address
        )
        if not coord_result.is_valid:
            warnings.extend(coord_result.validation_warnings)
        else:
            confidence_scores.append(coord_result.confidence_score)
        
        # Calculate overall confidence
        overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        
        # Determine if validation passes
        is_valid = len(errors) == 0 and overall_confidence >= 0.5
        
        if is_valid:
            self.validation_stats['validation_passes'] += 1
        else:
            self.validation_stats['validation_failures'] += 1
            
        if corrections:
            self.validation_stats['corrections_made'] += 1
        
        return ValidationResult(
            is_valid=is_valid,
            confidence_score=overall_confidence,
            validation_errors=errors,
            validation_warnings=warnings,
            corrected_value=corrections if corrections else None,
            metadata={
                'validation_timestamp': datetime.now().isoformat(),
                'validator_version': '1.0',
                'individual_scores': {
                    'address': address_result.confidence_score,
                    'energy_class': energy_result.confidence_score,
                    'price': price_result.confidence_score,
                    'sqm': sqm_result.confidence_score,
                    'coordinates': coord_result.confidence_score
                }
            }
        )
    
    def _validate_address(self, address: str) -> ValidationResult:
        """Validate and normalize address"""
        
        if not address or len(address.strip()) < 5:
            return ValidationResult(
                is_valid=False,
                confidence_score=0.0,
                validation_errors=["Address is missing or too short"],
                validation_warnings=[]
            )
        
        # Normalize address
        normalized = self.address_processor.normalize_address(address)
        
        # Check for common Greek address patterns
        greek_patterns = [
            r'\b(οδός|odos|street|str\.)\b',
            r'\b(πλατεία|plateia|square)\b',
            r'\b(λεωφόρος|leoforos|avenue|ave\.)\b'
        ]
        
        has_street_type = any(re.search(pattern, address.lower()) for pattern in greek_patterns)
        has_number = bool(re.search(r'\d+', address))
        
        confidence = 0.5
        if has_street_type:
            confidence += 0.3
        if has_number:
            confidence += 0.2
        
        warnings = []
        if not has_street_type:
            warnings.append("Address may be missing street type designation")
        if not has_number:
            warnings.append("Address may be missing street number")
        
        corrected_address = normalized if normalized != address else None
        
        return ValidationResult(
            is_valid=True,
            confidence_score=confidence,
            validation_errors=[],
            validation_warnings=warnings,
            corrected_value=corrected_address
        )
    
    def _validate_energy_class(self, energy_class: str) -> ValidationResult:
        """Validate energy class"""
        
        if not energy_class:
            return ValidationResult(
                is_valid=False,
                confidence_score=0.0,
                validation_errors=[],
                validation_warnings=["Energy class is missing"]
            )
        
        energy_class = energy_class.strip().upper()
        
        # Valid energy classes in Greece
        valid_classes = ['A+', 'A', 'B+', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'EXEMPT']
        
        if energy_class in valid_classes:
            return ValidationResult(
                is_valid=True,
                confidence_score=0.95,
                validation_errors=[],
                validation_warnings=[]
            )
        
        # Check for common variations
        corrections = {
            'A PLUS': 'A+',
            'APLUS': 'A+',
            'B PLUS': 'B+',
            'BPLUS': 'B+',
            'ΕΞΑΙΡΕΙΤΑΙ': 'EXEMPT',
            'ΔΕΝ ΑΠΑΙΤΕΙΤΑΙ': 'EXEMPT'
        }
        
        if energy_class in corrections:
            return ValidationResult(
                is_valid=True,
                confidence_score=0.8,
                validation_errors=[],
                validation_warnings=["Energy class normalized"],
                corrected_value=corrections[energy_class]
            )
        
        # Fuzzy matching for partial matches
        from fuzzywuzzy import process
        best_match = process.extractOne(energy_class, valid_classes)
        
        if best_match and best_match[1] > 80:
            return ValidationResult(
                is_valid=True,
                confidence_score=0.6,
                validation_errors=[],
                validation_warnings=[f"Energy class fuzzy matched: {energy_class} -> {best_match[0]}"],
                corrected_value=best_match[0]
            )
        
        return ValidationResult(
            is_valid=False,
            confidence_score=0.0,
            validation_errors=[],
            validation_warnings=[f"Unrecognized energy class: {energy_class}"]
        )
    
    def _validate_price(self, price: Optional[float], sqm: Optional[float]) -> ValidationResult:
        """Validate price with context"""
        
        if price is None:
            return ValidationResult(
                is_valid=False,
                confidence_score=0.0,
                validation_errors=[],
                validation_warnings=["Price is missing"]
            )
        
        warnings = []
        confidence = 0.7
        
        # Reasonable price range for Athens properties (€30k - €5M)
        if price < 30000:
            warnings.append("Price seems unusually low")
            confidence *= 0.7
        elif price > 5000000:
            warnings.append("Price seems unusually high")  
            confidence *= 0.8
        else:
            confidence = 0.9
        
        # Validate price per sqm if sqm available
        if sqm and sqm > 0:
            price_per_sqm = price / sqm
            
            # Athens typical range: €1,000 - €8,000 per sqm
            if price_per_sqm < 1000:
                warnings.append(f"Price per sqm (€{price_per_sqm:.0f}) seems low")
                confidence *= 0.8
            elif price_per_sqm > 8000:
                warnings.append(f"Price per sqm (€{price_per_sqm:.0f}) seems high")
                confidence *= 0.8
        
        return ValidationResult(
            is_valid=True,
            confidence_score=confidence,
            validation_errors=[],
            validation_warnings=warnings
        )
    
    def _validate_sqm(self, sqm: Optional[float]) -> ValidationResult:
        """Validate square meters"""
        
        if sqm is None:
            return ValidationResult(
                is_valid=False,
                confidence_score=0.0,
                validation_errors=[],
                validation_warnings=["Square meters is missing"]
            )
        
        warnings = []
        confidence = 0.9
        
        # Reasonable range for residential properties (20-500 sqm)
        if sqm < 20:
            warnings.append(f"Size ({sqm} sqm) seems unusually small")
            confidence *= 0.7
        elif sqm > 500:
            warnings.append(f"Size ({sqm} sqm) seems unusually large")
            confidence *= 0.8
        
        return ValidationResult(
            is_valid=True,
            confidence_score=confidence,
            validation_errors=[],
            validation_warnings=warnings
        )
    
    def _validate_coordinates(self, lat: Optional[float], lon: Optional[float], 
                            address: str) -> ValidationResult:
        """Validate geographic coordinates"""
        
        if lat is None or lon is None:
            return ValidationResult(
                is_valid=False,
                confidence_score=0.0,
                validation_errors=[],
                validation_warnings=["Coordinates are missing"]
            )
        
        warnings = []
        confidence = 0.8
        
        # Athens area bounds (approximate)
        athens_bounds = {
            'lat_min': 37.8,
            'lat_max': 38.1,
            'lon_min': 23.5,
            'lon_max': 24.0
        }
        
        if not (athens_bounds['lat_min'] <= lat <= athens_bounds['lat_max'] and
                athens_bounds['lon_min'] <= lon <= athens_bounds['lon_max']):
            warnings.append("Coordinates appear to be outside Athens area")
            confidence *= 0.5
        
        # TODO: Cross-validate with address using geocoding
        # This would require external geocoding service
        
        return ValidationResult(
            is_valid=True,
            confidence_score=confidence,
            validation_errors=[],
            validation_warnings=warnings
        )

class BuildingBlockValidator:
    """Building block level validation and quality assessment"""
    
    def __init__(self):
        self.property_validator = PropertyValidator()
        
    def validate_building_block(self, building_block: BuildingBlock) -> QualityMetrics:
        """Comprehensive building block validation"""
        
        if not building_block.properties:
            return QualityMetrics(
                completeness_score=0.0,
                accuracy_score=0.0,
                consistency_score=0.0,
                reliability_score=0.0,
                overall_quality_score=0.0,
                sample_size_adequacy=0.0,
                geographic_coverage=0.0,
                temporal_consistency=0.0
            )
        
        # Validate all properties
        property_validations = []
        for prop in building_block.properties:
            validation = self.property_validator.validate_property_comprehensive(prop)
            property_validations.append(validation)
        
        # Calculate quality metrics
        completeness = self._calculate_completeness_score(building_block.properties)
        accuracy = self._calculate_accuracy_score(property_validations)
        consistency = self._calculate_consistency_score(building_block.properties)
        reliability = self._calculate_reliability_score(building_block, property_validations)
        sample_adequacy = self._calculate_sample_adequacy(building_block.properties)
        geo_coverage = self._calculate_geographic_coverage(building_block.properties)
        temporal_consistency = self._calculate_temporal_consistency(building_block.properties)
        
        # Calculate overall quality score
        weights = {
            'completeness': 0.25,
            'accuracy': 0.25,
            'consistency': 0.20,
            'reliability': 0.15,
            'sample_adequacy': 0.10,
            'geo_coverage': 0.05
        }
        
        overall_score = (
            completeness * weights['completeness'] +
            accuracy * weights['accuracy'] +
            consistency * weights['consistency'] +
            reliability * weights['reliability'] +
            sample_adequacy * weights['sample_adequacy'] +
            geo_coverage * weights['geo_coverage']
        )
        
        return QualityMetrics(
            completeness_score=completeness,
            accuracy_score=accuracy,
            consistency_score=consistency,
            reliability_score=reliability,
            overall_quality_score=overall_score,
            sample_size_adequacy=sample_adequacy,
            geographic_coverage=geo_coverage,
            temporal_consistency=temporal_consistency
        )
    
    def _calculate_completeness_score(self, properties: List[PropertyData]) -> float:
        """Calculate data completeness score"""
        
        if not properties:
            return 0.0
        
        total_fields = 0
        completed_fields = 0
        
        # Weight different fields by importance
        field_weights = {
            'address': 1.0,
            'price': 0.9,
            'sqm': 0.9,
            'energy_class': 0.8,
            'latitude': 0.6,
            'longitude': 0.6,
            'floor': 0.4,
            'rooms': 0.4
        }
        
        for prop in properties:
            for field, weight in field_weights.items():
                total_fields += weight
                if getattr(prop, field, None) is not None:
                    completed_fields += weight
        
        return completed_fields / total_fields if total_fields > 0 else 0.0
    
    def _calculate_accuracy_score(self, validations: List[ValidationResult]) -> float:
        """Calculate accuracy based on validation results"""
        
        if not validations:
            return 0.0
        
        confidence_scores = [v.confidence_score for v in validations]
        return np.mean(confidence_scores)
    
    def _calculate_consistency_score(self, properties: List[PropertyData]) -> float:
        """Calculate internal consistency score"""
        
        if len(properties) < 2:
            return 1.0  # Single property is perfectly consistent
        
        consistency_scores = []
        
        # Price consistency (coefficient of variation)
        prices = [p.price for p in properties if p.price]
        if len(prices) > 1:
            cv_price = np.std(prices) / np.mean(prices)
            price_consistency = max(0.0, 1.0 - cv_price)  # Lower CV = higher consistency
            consistency_scores.append(price_consistency)
        
        # Size consistency
        sizes = [p.sqm for p in properties if p.sqm]
        if len(sizes) > 1:
            cv_size = np.std(sizes) / np.mean(sizes)
            size_consistency = max(0.0, 1.0 - cv_size)
            consistency_scores.append(size_consistency)
        
        # Energy class consistency
        energy_classes = [p.energy_class for p in properties if p.energy_class]
        if len(energy_classes) > 1:
            most_common_count = max(energy_classes.count(ec) for ec in set(energy_classes))
            energy_consistency = most_common_count / len(energy_classes)
            consistency_scores.append(energy_consistency)
        
        # Address consistency (street name similarity)
        addresses = [p.address for p in properties if p.address]
        if len(addresses) > 1:
            # Extract street names and check similarity
            street_names = []
            for addr in addresses:
                street, _ = address_processor.extract_street_number(addr)
                street_names.append(street)
            
            most_common_street_count = max(street_names.count(sn) for sn in set(street_names))
            address_consistency = most_common_street_count / len(street_names)
            consistency_scores.append(address_consistency)
        
        return np.mean(consistency_scores) if consistency_scores else 1.0
    
    def _calculate_reliability_score(self, building_block: BuildingBlock, 
                                   validations: List[ValidationResult]) -> float:
        """Calculate reliability based on data sources and validation"""
        
        reliability_factors = []
        
        # Sample size reliability
        sample_size = len(building_block.properties)
        size_reliability = min(1.0, sample_size / 10)  # Full reliability at 10+ properties
        reliability_factors.append(size_reliability)
        
        # Validation reliability
        valid_count = sum(1 for v in validations if v.is_valid)
        validation_reliability = valid_count / len(validations) if validations else 0.0
        reliability_factors.append(validation_reliability)
        
        # Data source diversity
        sources = set(p.source for p in building_block.properties)
        source_diversity = min(1.0, len(sources) / 3)  # Up to 3 different sources
        reliability_factors.append(source_diversity)
        
        # Temporal reliability (properties scraped recently)
        now = datetime.now()
        recent_count = sum(1 for p in building_block.properties 
                          if (now - p.scraped_at).days < 30)
        temporal_reliability = recent_count / len(building_block.properties)
        reliability_factors.append(temporal_reliability)
        
        return np.mean(reliability_factors)
    
    def _calculate_sample_adequacy(self, properties: List[PropertyData]) -> float:
        """Calculate sample size adequacy"""
        
        sample_size = len(properties)
        
        # Power analysis based approach
        # For 95% confidence, 5% margin of error: n = (1.96^2 * p * (1-p)) / 0.05^2
        # Assuming p = 0.5 (worst case): n ≈ 384 for infinite population
        # For building block (small finite population), use finite correction
        
        if sample_size >= 30:
            return 1.0
        elif sample_size >= 15:
            return 0.8
        elif sample_size >= 10:
            return 0.6
        elif sample_size >= 5:
            return 0.4
        else:
            return 0.2
    
    def _calculate_geographic_coverage(self, properties: List[PropertyData]) -> float:
        """Calculate geographic coverage within building block"""
        
        coords = [(p.latitude, p.longitude) for p in properties 
                 if p.latitude and p.longitude]
        
        if len(coords) < 2:
            return 0.5  # Cannot assess coverage with < 2 points
        
        # Calculate spread of coordinates
        lats = [c[0] for c in coords]
        lons = [c[1] for c in coords]
        
        lat_range = max(lats) - min(lats)
        lon_range = max(lons) - min(lons)
        
        # Convert to rough meters (1 degree ≈ 111km, but varies by latitude)
        lat_meters = lat_range * 111000
        lon_meters = lon_range * 111000 * np.cos(np.radians(np.mean(lats)))
        
        max_spread = max(lat_meters, lon_meters)
        
        # Good coverage if spread is 100-300 meters (typical building block)
        if 100 <= max_spread <= 300:
            return 1.0
        elif max_spread < 100:
            return 0.7  # Might be too concentrated
        else:
            return max(0.3, 1.0 - (max_spread - 300) / 1000)  # Penalize excessive spread
    
    def _calculate_temporal_consistency(self, properties: List[PropertyData]) -> float:
        """Calculate temporal consistency of data collection"""
        
        scrape_times = [p.scraped_at for p in properties if p.scraped_at]
        
        if len(scrape_times) < 2:
            return 1.0
        
        # Calculate time span of data collection
        time_span = max(scrape_times) - min(scrape_times)
        
        # Good consistency if all data collected within 7 days
        if time_span.days <= 7:
            return 1.0
        elif time_span.days <= 30:
            return 0.8
        elif time_span.days <= 90:
            return 0.6
        else:
            return 0.4

class StatisticalValidator:
    """Statistical validation and significance testing"""
    
    def __init__(self):
        self.building_validator = BuildingBlockValidator()
        
    def validate_analysis_statistical_significance(self, building_blocks: List[BuildingBlock]) -> Dict[str, Any]:
        """Validate statistical significance of analysis results"""
        
        if not building_blocks:
            return {
                'is_statistically_significant': False,
                'confidence_level': 0.0,
                'sample_size_adequacy': 0.0,
                'power_analysis': {},
                'recommendations': ['No building blocks available for analysis']
            }
        
        # Collect all properties
        all_properties = []
        for block in building_blocks:
            all_properties.extend(block.properties)
        
        # Basic sample size check
        total_sample_size = len(all_properties)
        sample_adequacy = min(1.0, total_sample_size / 100)  # Ideal: 100+ properties
        
        # Energy class distribution analysis
        energy_classes = [p.energy_class for p in all_properties if p.energy_class]
        energy_significance = self._test_energy_class_significance(energy_classes)
        
        # Price analysis
        prices = [p.price for p in all_properties if p.price]
        price_analysis = self._analyze_price_distribution(prices)
        
        # Building block consistency
        block_consistency = self._test_block_consistency(building_blocks)
        
        # Overall significance assessment
        significance_factors = [
            sample_adequacy,
            energy_significance.get('significance_score', 0.0),
            price_analysis.get('normality_score', 0.0),
            block_consistency.get('consistency_score', 0.0)
        ]
        
        overall_significance = np.mean(significance_factors)
        
        # Generate recommendations
        recommendations = self._generate_statistical_recommendations(
            total_sample_size, energy_significance, price_analysis, block_consistency
        )
        
        return {
            'is_statistically_significant': overall_significance >= 0.7,
            'confidence_level': overall_significance,
            'sample_size_adequacy': sample_adequacy,
            'total_sample_size': total_sample_size,
            'energy_class_analysis': energy_significance,
            'price_analysis': price_analysis,
            'block_consistency_analysis': block_consistency,
            'power_analysis': self._calculate_power_analysis(total_sample_size),
            'recommendations': recommendations
        }
    
    def _test_energy_class_significance(self, energy_classes: List[str]) -> Dict[str, Any]:
        """Test statistical significance of energy class distribution"""
        
        if len(energy_classes) < 10:
            return {
                'significance_score': 0.0,
                'test_result': 'insufficient_data',
                'p_value': None,
                'distribution': {}
            }
        
        # Count energy classes
        from collections import Counter
        distribution = Counter(energy_classes)
        
        # Chi-square goodness of fit test (against uniform distribution)
        observed = list(distribution.values())
        expected = [len(energy_classes) / len(distribution)] * len(distribution)
        
        try:
            chi2_stat, p_value = stats.chisquare(observed, expected)
            
            # Lower p-value means more significant deviation from uniform
            significance_score = 1.0 - p_value if p_value <= 1.0 else 0.0
            
            return {
                'significance_score': significance_score,
                'test_result': 'significant' if p_value < 0.05 else 'not_significant',
                'p_value': p_value,
                'chi2_statistic': chi2_stat,
                'distribution': dict(distribution),
                'sample_size': len(energy_classes)
            }
            
        except Exception as e:
            logging.warning(f"Energy class significance test failed: {e}")
            return {
                'significance_score': 0.5,
                'test_result': 'test_failed',
                'distribution': dict(distribution),
                'sample_size': len(energy_classes)
            }
    
    def _analyze_price_distribution(self, prices: List[float]) -> Dict[str, Any]:
        """Analyze price distribution and normality"""
        
        if len(prices) < 8:
            return {
                'normality_score': 0.0,
                'distribution_type': 'insufficient_data',
                'statistics': {}
            }
        
        prices_array = np.array(prices)
        
        # Basic statistics
        statistics = {
            'mean': np.mean(prices_array),
            'median': np.median(prices_array),
            'std': np.std(prices_array),
            'min': np.min(prices_array),
            'max': np.max(prices_array),
            'cv': np.std(prices_array) / np.mean(prices_array),  # Coefficient of variation
            'skewness': stats.skew(prices_array),
            'kurtosis': stats.kurtosis(prices_array)
        }
        
        # Normality tests
        try:
            shapiro_stat, shapiro_p = stats.shapiro(prices_array)
            normality_score = shapiro_p  # Higher p-value = more normal
        except:
            normality_score = 0.5
            shapiro_p = None
        
        # Determine distribution type
        if abs(statistics['skewness']) < 0.5:
            distribution_type = 'approximately_normal'
        elif statistics['skewness'] > 0.5:
            distribution_type = 'right_skewed'
        else:
            distribution_type = 'left_skewed'
        
        return {
            'normality_score': normality_score,
            'distribution_type': distribution_type,
            'statistics': statistics,
            'shapiro_p_value': shapiro_p,
            'sample_size': len(prices)
        }
    
    def _test_block_consistency(self, building_blocks: List[BuildingBlock]) -> Dict[str, Any]:
        """Test consistency across building blocks"""
        
        if len(building_blocks) < 2:
            return {
                'consistency_score': 1.0,
                'test_result': 'single_block',
                'block_comparison': {}
            }
        
        # Validate each building block
        block_qualities = []
        for block in building_blocks:
            quality_metrics = self.building_validator.validate_building_block(block)
            block_qualities.append(quality_metrics.overall_quality_score)
        
        # Calculate consistency of quality scores
        quality_consistency = 1.0 - (np.std(block_qualities) / np.mean(block_qualities))
        quality_consistency = max(0.0, quality_consistency)
        
        # Sample size consistency
        sample_sizes = [len(block.properties) for block in building_blocks]
        size_cv = np.std(sample_sizes) / np.mean(sample_sizes)
        size_consistency = max(0.0, 1.0 - size_cv)
        
        # Energy class consistency across blocks
        block_energy_classes = []
        for block in building_blocks:
            block_classes = [p.energy_class for p in block.properties if p.energy_class]
            if block_classes:
                most_common = max(set(block_classes), key=block_classes.count)
                block_energy_classes.append(most_common)
        
        if len(block_energy_classes) > 1:
            energy_consistency = len(set(block_energy_classes)) / len(block_energy_classes)
            energy_consistency = 1.0 - energy_consistency  # Lower diversity = higher consistency
        else:
            energy_consistency = 1.0
        
        # Overall consistency
        consistency_score = np.mean([quality_consistency, size_consistency, energy_consistency])
        
        return {
            'consistency_score': consistency_score,
            'test_result': 'consistent' if consistency_score > 0.7 else 'inconsistent',
            'quality_consistency': quality_consistency,
            'sample_size_consistency': size_consistency,
            'energy_class_consistency': energy_consistency,
            'block_count': len(building_blocks)
        }
    
    def _calculate_power_analysis(self, sample_size: int) -> Dict[str, Any]:
        """Calculate statistical power for given sample size"""
        
        # Simple power calculation for proportion estimation
        # Power = 1 - β (where β is Type II error probability)
        
        if sample_size >= 100:
            power = 0.9
            margin_of_error = 0.05
        elif sample_size >= 50:
            power = 0.8
            margin_of_error = 0.07
        elif sample_size >= 30:
            power = 0.7
            margin_of_error = 0.10
        elif sample_size >= 15:
            power = 0.6
            margin_of_error = 0.15
        else:
            power = 0.5
            margin_of_error = 0.20
        
        return {
            'statistical_power': power,
            'margin_of_error': margin_of_error,
            'confidence_level': 0.95,
            'sample_size': sample_size,
            'recommended_minimum_size': 30,
            'ideal_sample_size': 100
        }
    
    def _generate_statistical_recommendations(self, sample_size: int, 
                                            energy_analysis: Dict, 
                                            price_analysis: Dict,
                                            consistency_analysis: Dict) -> List[str]:
        """Generate statistical recommendations"""
        
        recommendations = []
        
        # Sample size recommendations
        if sample_size < 30:
            recommendations.append(f"Sample size ({sample_size}) is below recommended minimum (30). Consider collecting more data.")
        elif sample_size < 100:
            recommendations.append(f"Sample size ({sample_size}) is adequate but could be improved for better statistical power.")
        
        # Energy class recommendations
        if energy_analysis.get('significance_score', 0) < 0.3:
            recommendations.append("Energy class distribution lacks statistical significance. Consider targeted data collection.")
        
        # Price distribution recommendations
        if price_analysis.get('normality_score', 0) < 0.05:
            recommendations.append("Price distribution is not normal. Consider using non-parametric statistical methods.")
        
        if price_analysis.get('statistics', {}).get('cv', 0) > 0.5:
            recommendations.append("High price variability detected. Consider segmenting analysis by property characteristics.")
        
        # Consistency recommendations
        if consistency_analysis.get('consistency_score', 0) < 0.6:
            recommendations.append("Low consistency across building blocks. Review clustering methodology and data quality.")
        
        return recommendations

# Example usage and testing
def test_validation_pipeline():
    """Test the validation pipeline"""
    
    # Create sample property data
    sample_property = PropertyData(
        id="test_001",
        url="https://example.com/property/1",
        title="Test Property",
        address="Skoufa 25, Kolonaki, Athens",
        price=450000.0,
        sqm=85.0,
        energy_class="B",
        floor=3,
        rooms=2,
        latitude=37.9755,
        longitude=23.7348,
        description="Test property",
        images=[],
        scraped_at=datetime.now(),
        confidence_score=0.0,
        validation_flags=[]
    )
    
    # Test property validation
    property_validator = PropertyValidator()
    validation_result = property_validator.validate_property_comprehensive(sample_property)
    
    print("Property Validation Result:")
    print(f"Valid: {validation_result.is_valid}")
    print(f"Confidence: {validation_result.confidence_score:.2f}")
    print(f"Warnings: {validation_result.validation_warnings}")
    
    # Print validation statistics
    print(f"\nValidation Statistics: {property_validator.validation_stats}")

if __name__ == "__main__":
    test_validation_pipeline()