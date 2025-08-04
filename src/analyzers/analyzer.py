"""
Advanced Property Analysis Engine
Multi-strategy discovery, building block clustering, and statistical validation
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from geopy.distance import geodesic
import json
import os

from config import config
from utils import (
    PropertyData, BuildingBlock, AddressProcessor, DataValidator,
    StatisticalAnalyzer, PerformanceMonitor, address_processor,
    performance_monitor, create_output_directories
)
from scraper_ultimate import UltimateSpitogatosScraper

# Define SearchParams for backward compatibility
@dataclass
class SearchParams:
    location: str
    property_type: str = "apartment"
    transaction_type: str = "sale"

@dataclass
class AnalysisResult:
    """Complete analysis result for a building block"""
    building_block: BuildingBlock
    properties: List[PropertyData]
    metadata: Dict[str, Any]
    quality_metrics: Dict[str, float]
    statistical_summary: Dict[str, Any]
    
class MultiStrategyDiscovery:
    """Advanced property discovery using multiple complementary strategies"""
    
    def __init__(self, scraper: UltimateSpitogatosScraper):
        self.scraper = scraper
        self.discovered_properties: Dict[str, PropertyData] = {}
        self.discovery_stats = {
            'systematic_search': 0,
            'adjacency_discovery': 0,
            'historical_integration': 0,
            'cross_platform_verification': 0
        }
        
    async def discover_properties_comprehensive(self, area_config) -> List[PropertyData]:
        """Comprehensive property discovery using all strategies"""
        all_properties = []
        
        logging.info(f"Starting comprehensive discovery for {area_config.name}")
        
        # Strategy 1: Systematic street coverage
        systematic_properties = await self._systematic_street_discovery(area_config)
        all_properties.extend(systematic_properties)
        self.discovery_stats['systematic_search'] = len(systematic_properties)
        
        # Strategy 2: Adjacency-based discovery
        adjacency_properties = await self._adjacency_discovery(systematic_properties)
        all_properties.extend(adjacency_properties)
        self.discovery_stats['adjacency_discovery'] = len(adjacency_properties)
        
        # Strategy 3: Historical/Wayback integration (placeholder for now)
        # historical_properties = await self._historical_discovery(area_config)
        # all_properties.extend(historical_properties)
        
        # Remove duplicates and merge data
        unique_properties = self._merge_duplicate_properties(all_properties)
        
        logging.info(f"Discovery completed for {area_config.name}. "
                    f"Found {len(unique_properties)} unique properties")
        
        return unique_properties
    
    async def _systematic_street_discovery(self, area_config) -> List[PropertyData]:
        """Systematic discovery by searching each street methodically"""
        properties = []
        
        logging.info(f"Starting systematic street discovery for {area_config.name}")
        
        # Sort streets by priority
        sorted_streets = sorted(area_config.streets, key=lambda x: x.get('priority', 1))
        
        for street_info in sorted_streets:
            street_name = street_info['name']
            address_range = street_info.get('range', '1-100')
            priority = street_info.get('priority', 1)
            
            logging.info(f"Searching {street_name} (priority {priority})")
            
            # Search with multiple approaches
            street_properties = await self._search_street_comprehensive(
                street_name, area_config.name, priority
            )
            
            properties.extend(street_properties)
            
            # Adaptive delay based on priority and findings
            delay = 2.0 if priority == 1 else 3.0
            if len(street_properties) > 10:  # Found many properties, slow down
                delay *= 1.5
                
            await asyncio.sleep(delay)
        
        return properties
    
    async def _search_street_comprehensive(self, street_name: str, area_name: str, 
                                         priority: int) -> List[PropertyData]:
        """Comprehensive search for a specific street"""
        properties = []
        
        # Primary search: Exact street name
        search_params = SearchParams(
            location=f"{street_name}, {area_name}, Athens",
            property_type="apartment"
        )
        
        primary_results = await self.scraper.search_properties(
            search_params.location, max_pages=15
        )
        properties.extend(primary_results)
        
        # Secondary search: Street with different variations
        street_variations = self._generate_street_variations(street_name)
        
        for variation in street_variations[:3]:  # Limit to top 3 variations
            variation_params = SearchParams(
                location=f"{variation}, {area_name}, Athens",
                property_type="apartment"
            )
            
            variation_results = await self.scraper.search_properties(
                variation_params.location, max_pages=8
            )
            properties.extend(variation_results)
            
            await asyncio.sleep(1.5)  # Brief delay between variations
        
        return properties
    
    def _generate_street_variations(self, street_name: str) -> List[str]:
        """Generate common variations of street names"""
        variations = []
        
        # Common Greek street variations
        replacements = [
            ('Οδός', ''),
            ('οδός', ''),
            ('Str.', ''),
            ('Street', ''),
            (' ', ''),  # Remove spaces
            ('ου', 'ου'),  # Keep as is for now
        ]
        
        for old, new in replacements:
            if old in street_name:
                variation = street_name.replace(old, new).strip()
                if variation and variation != street_name:
                    variations.append(variation)
        
        return variations[:5]  # Limit variations
    
    async def _adjacency_discovery(self, known_properties: List[PropertyData]) -> List[PropertyData]:
        """Discover properties adjacent to known properties"""
        adjacency_properties = []
        
        logging.info("Starting adjacency-based discovery")
        
        # Group properties by approximate location
        location_clusters = self._cluster_properties_by_location(known_properties)
        
        for cluster in location_clusters:
            if len(cluster) < 2:
                continue
                
            # Find the center of this cluster
            center_lat = np.mean([p.latitude for p in cluster if p.latitude])
            center_lon = np.mean([p.longitude for p in cluster if p.longitude])
            
            if not (center_lat and center_lon):
                continue
            
            # Search in expanding radius around cluster center
            nearby_properties = await self._search_radius_area(
                center_lat, center_lon, radius_meters=200
            )
            
            adjacency_properties.extend(nearby_properties)
            
            await asyncio.sleep(2.0)  # Delay between cluster searches
        
        return adjacency_properties
    
    def _cluster_properties_by_location(self, properties: List[PropertyData]) -> List[List[PropertyData]]:
        """Cluster properties by geographic proximity"""
        # Filter properties with coordinates
        geo_properties = [p for p in properties if p.latitude and p.longitude]
        
        if len(geo_properties) < 2:
            return []
        
        # Create coordinate matrix
        coords = np.array([[p.latitude, p.longitude] for p in geo_properties])
        
        # Use DBSCAN for clustering
        clustering = DBSCAN(eps=0.002, min_samples=2)  # ~200m radius
        cluster_labels = clustering.fit_predict(coords)
        
        # Group properties by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label != -1:  # Ignore noise points
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(geo_properties[i])
        
        return list(clusters.values())
    
    async def _search_radius_area(self, lat: float, lon: float, 
                                radius_meters: int) -> List[PropertyData]:
        """Search for properties within radius of a point"""
        # This would require geocoded search capability
        # For now, return empty list as placeholder
        # In a real implementation, you'd search using lat/lon bounds
        
        return []
    
    def _merge_duplicate_properties(self, properties: List[PropertyData]) -> List[PropertyData]:
        """Merge duplicate properties and enhance data quality"""
        property_groups = {}
        
        # Group by ID (which is based on URL and address)
        for prop in properties:
            if prop.id not in property_groups:
                property_groups[prop.id] = []
            property_groups[prop.id].append(prop)
        
        merged_properties = []
        
        for prop_id, prop_group in property_groups.items():
            if len(prop_group) == 1:
                merged_properties.append(prop_group[0])
            else:
                # Merge multiple entries for same property
                merged_prop = self._merge_property_data(prop_group)
                merged_properties.append(merged_prop)
        
        return merged_properties
    
    def _merge_property_data(self, properties: List[PropertyData]) -> PropertyData:
        """Merge multiple PropertyData objects for the same property"""
        # Use the most recent one as base
        base_prop = max(properties, key=lambda p: p.scraped_at)
        
        # Merge data from all sources
        merged_images = []
        for prop in properties:
            merged_images.extend(prop.images)
        
        # Remove duplicate images
        unique_images = list(dict.fromkeys(merged_images))
        
        # Use best available data for each field
        best_price = max((p.price for p in properties if p.price), default=base_prop.price)
        best_sqm = max((p.sqm for p in properties if p.sqm), default=base_prop.sqm)
        
        # Create merged property
        merged_prop = PropertyData(
            id=base_prop.id,
            url=base_prop.url,
            title=base_prop.title,
            address=base_prop.address,
            price=best_price,
            sqm=best_sqm,
            energy_class=base_prop.energy_class,
            floor=base_prop.floor,
            rooms=base_prop.rooms,
            latitude=base_prop.latitude,
            longitude=base_prop.longitude,
            description=base_prop.description,
            images=unique_images,
            scraped_at=base_prop.scraped_at,
            confidence_score=0.0,  # Will be recalculated
            validation_flags=['merged_data'],
            source=f"merged_{len(properties)}_sources"
        )
        
        return merged_prop

class BuildingBlockAnalyzer:
    """Advanced building block clustering and analysis"""
    
    def __init__(self):
        self.address_processor = address_processor
        self.data_validator = DataValidator(config)
        self.statistical_analyzer = StatisticalAnalyzer()
        
    def cluster_properties_into_blocks(self, properties: List[PropertyData]) -> List[BuildingBlock]:
        """Cluster properties into building blocks using multiple factors"""
        
        logging.info(f"Clustering {len(properties)} properties into building blocks")
        
        if len(properties) < config.CLUSTERING.min_properties_per_cluster:
            logging.warning("Insufficient properties for clustering")
            return []
        
        # Prepare data for clustering
        clustering_data = self._prepare_clustering_data(properties)
        
        if not clustering_data:
            return []
        
        # Perform clustering
        clusters = self._perform_dbscan_clustering(clustering_data, properties)
        
        # Convert clusters to building blocks
        building_blocks = []
        for cluster_id, cluster_properties in clusters.items():
            building_block = self._create_building_block(cluster_id, cluster_properties)
            if building_block:
                building_blocks.append(building_block)
        
        logging.info(f"Created {len(building_blocks)} building blocks")
        return building_blocks
    
    def _prepare_clustering_data(self, properties: List[PropertyData]) -> Optional[np.ndarray]:
        """Prepare data matrix for clustering"""
        clustering_features = []
        valid_properties = []
        
        for prop in properties:
            features = []
            
            # Address similarity features (normalized street name)
            if prop.address:
                street_name, number = self.address_processor.extract_street_number(prop.address)
                street_hash = hash(self.address_processor.normalize_address(street_name)) % 10000
                features.append(street_hash)
                features.append(number or 0)
            else:
                features.extend([0, 0])
            
            # Geographic features
            if prop.latitude and prop.longitude:
                # Scale coordinates for clustering (Athens area roughly)
                scaled_lat = (prop.latitude - 37.9) * 1000  # Rough center of Athens
                scaled_lon = (prop.longitude - 23.7) * 1000
                features.extend([scaled_lat, scaled_lon])
            else:
                features.extend([0, 0])
            
            # Building characteristics
            features.append(prop.sqm or 0)
            features.append(prop.floor or 0)
            
            clustering_features.append(features)
            valid_properties.append(prop)
        
        if not clustering_features:
            return None
        
        # Convert to numpy array and normalize
        data_matrix = np.array(clustering_features)
        
        # Use StandardScaler to normalize features
        scaler = StandardScaler()
        normalized_data = scaler.fit_transform(data_matrix)
        
        return normalized_data
    
    def _perform_dbscan_clustering(self, data_matrix: np.ndarray, 
                                 properties: List[PropertyData]) -> Dict[int, List[PropertyData]]:
        """Perform DBSCAN clustering"""
        
        # Configure DBSCAN parameters
        eps = 0.5  # Distance threshold
        min_samples = config.CLUSTERING.min_properties_per_cluster
        
        clustering = DBSCAN(eps=eps, min_samples=min_samples)
        cluster_labels = clustering.fit_predict(data_matrix)
        
        # Group properties by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label != -1:  # Ignore noise points
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(properties[i])
        
        # Log clustering results
        noise_count = sum(1 for label in cluster_labels if label == -1)
        logging.info(f"DBSCAN clustering: {len(clusters)} clusters, {noise_count} noise points")
        
        return clusters
    
    def _create_building_block(self, cluster_id: int, 
                             properties: List[PropertyData]) -> Optional[BuildingBlock]:
        """Create building block from clustered properties"""
        
        if len(properties) < config.CLUSTERING.min_properties_per_cluster:
            return None
        
        # Calculate center coordinates
        valid_coords = [(p.latitude, p.longitude) for p in properties 
                       if p.latitude and p.longitude]
        
        if valid_coords:
            center_lat = np.mean([coord[0] for coord in valid_coords])
            center_lon = np.mean([coord[1] for coord in valid_coords])
        else:
            center_lat = center_lon = 0.0
        
        # Calculate weighted energy class and confidence
        weighted_energy_class, confidence_interval = (
            self.statistical_analyzer.calculate_weighted_energy_class(properties)
        )
        
        # Calculate quality metrics
        completeness_score = self._calculate_completeness_score(properties)
        validation_score = self._calculate_validation_score(properties)
        
        # Generate building block name
        addresses = [p.address for p in properties if p.address]
        if addresses:
            # Use most common street name
            street_names = []
            for addr in addresses:
                street, _ = self.address_processor.extract_street_number(addr)
                street_names.append(street)
            
            most_common_street = max(set(street_names), key=street_names.count)
            block_name = f"{most_common_street}_Block_{cluster_id}"
        else:
            block_name = f"Unknown_Block_{cluster_id}"
        
        # Create building block
        building_block = BuildingBlock(
            id=f"block_{cluster_id}",
            name=block_name,
            properties=properties,
            center_lat=center_lat,
            center_lon=center_lon,
            weighted_energy_class=weighted_energy_class,
            confidence_interval=confidence_interval,
            sample_size=len(properties),
            completeness_score=completeness_score,
            validation_score=validation_score,
            analysis_timestamp=datetime.now()
        )
        
        return building_block
    
    def _calculate_completeness_score(self, properties: List[PropertyData]) -> float:
        """Calculate data completeness score for building block"""
        if not properties:
            return 0.0
        
        total_fields = 0
        completed_fields = 0
        
        important_fields = ['address', 'price', 'sqm', 'energy_class']
        
        for prop in properties:
            for field in important_fields:
                total_fields += 1
                if getattr(prop, field, None):
                    completed_fields += 1
        
        return completed_fields / total_fields if total_fields > 0 else 0.0
    
    def _calculate_validation_score(self, properties: List[PropertyData]) -> float:
        """Calculate validation score for building block"""
        if not properties:
            return 0.0
        
        validation_scores = []
        
        for prop in properties:
            # Validate each property and get confidence score
            prop_confidence = self.data_validator.calculate_property_confidence(prop)
            validation_scores.append(prop_confidence)
        
        return np.mean(validation_scores) if validation_scores else 0.0

class ComprehensiveAnalysisEngine:
    """Main analysis engine coordinating all components"""
    
    def __init__(self):
        self.performance_monitor = performance_monitor
        self.discovery_engine = None  # Will be initialized with scraper
        self.building_analyzer = BuildingBlockAnalyzer()
        self.results = {}
        
    async def analyze_area_comprehensive(self, area_config) -> AnalysisResult:
        """Perform comprehensive analysis for an area"""
        
        logging.info(f"Starting comprehensive analysis for {area_config.name}")
        self.performance_monitor.start_timer(f"analysis_{area_config.name}")
        
        try:
            # Initialize scraper and discovery engine
            async with UltimateSpitogatosScraper() as scraper:
                self.discovery_engine = MultiStrategyDiscovery(scraper)
                
                # Phase 1: Property Discovery with professional fallback
                properties = await scraper.comprehensive_area_search(
                    area_config.name, 
                    [s['name'] for s in area_config.streets[:5]]  # Pass street names
                )
                
                if not properties:
                    logging.warning(f"No properties discovered for {area_config.name}")
                    return None
                
                # Phase 2: Building Block Clustering
                building_blocks = self.building_analyzer.cluster_properties_into_blocks(properties)
                
                if not building_blocks:
                    logging.warning(f"No building blocks created for {area_config.name}")
                    return None
                
                # Phase 3: Statistical Analysis
                analysis_results = []
                
                for building_block in building_blocks:
                    result = self._analyze_building_block_comprehensive(building_block)
                    analysis_results.append(result)
                
                # Phase 4: Area-level aggregation
                area_result = self._create_area_analysis_result(
                    area_config, properties, building_blocks, analysis_results
                )
                
                self.performance_monitor.end_timer(f"analysis_{area_config.name}")
                
                logging.info(f"Analysis completed for {area_config.name}")
                return area_result
                
        except Exception as e:
            logging.error(f"Error in comprehensive analysis for {area_config.name}: {e}")
            return None
    
    def _analyze_building_block_comprehensive(self, building_block: BuildingBlock) -> AnalysisResult:
        """Perform comprehensive analysis for a single building block"""
        
        # Quality metrics
        quality_metrics = {
            'completeness_score': building_block.completeness_score,
            'validation_score': building_block.validation_score,
            'confidence_score': building_block.confidence_interval.get('confidence', 0.0),
            'sample_size_adequacy': min(1.0, building_block.sample_size / 10)
        }
        
        # Statistical summary
        prices = [p.price for p in building_block.properties if p.price]
        sqms = [p.sqm for p in building_block.properties if p.sqm]
        
        statistical_summary = {
            'property_count': len(building_block.properties),
            'energy_class_distribution': self._calculate_energy_distribution(building_block.properties),
            'price_statistics': self._calculate_price_statistics(prices),
            'size_statistics': self._calculate_size_statistics(sqms),
            'geographic_spread': self._calculate_geographic_spread(building_block.properties)
        }
        
        # Metadata
        metadata = {
            'analysis_timestamp': building_block.analysis_timestamp.isoformat(),
            'center_coordinates': {
                'latitude': building_block.center_lat,
                'longitude': building_block.center_lon
            },
            'data_sources': list(set(p.source for p in building_block.properties)),
            'validation_flags': self._collect_validation_flags(building_block.properties)
        }
        
        return AnalysisResult(
            building_block=building_block,
            properties=building_block.properties,
            metadata=metadata,
            quality_metrics=quality_metrics,
            statistical_summary=statistical_summary
        )
    
    def _create_area_analysis_result(self, area_config, properties: List[PropertyData],
                                   building_blocks: List[BuildingBlock],
                                   analysis_results: List[AnalysisResult]) -> Dict[str, Any]:
        """Create comprehensive area-level analysis result"""
        
        return {
            'area_info': {
                'name': area_config.name,
                'strategy': area_config.search_strategy,
                'expected_properties': area_config.expected_properties,
                'quality_threshold': area_config.quality_threshold
            },
            'discovery_summary': {
                'total_properties_found': len(properties),
                'building_blocks_created': len(building_blocks),
                'discovery_stats': self.discovery_engine.discovery_stats if self.discovery_engine else {}
            },
            'building_blocks': [asdict(result.building_block) for result in analysis_results],
            'quality_assessment': self._assess_area_quality(analysis_results, area_config),
            'statistical_overview': self._create_statistical_overview(analysis_results),
            'recommendations': self._generate_recommendations(analysis_results, area_config),
            'analysis_metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'analysis_duration': self.performance_monitor.get_stats(f"analysis_{area_config.name}"),
                'data_quality_flags': self._assess_data_quality(properties)
            }
        }
    
    def _calculate_energy_distribution(self, properties: List[PropertyData]) -> Dict[str, int]:
        """Calculate energy class distribution"""
        distribution = {}
        for prop in properties:
            if prop.energy_class:
                distribution[prop.energy_class] = distribution.get(prop.energy_class, 0) + 1
        return distribution
    
    def _calculate_price_statistics(self, prices: List[float]) -> Dict[str, float]:
        """Calculate price statistics"""
        if not prices:
            return {}
        
        return {
            'count': len(prices),
            'mean': np.mean(prices),
            'median': np.median(prices),
            'std': np.std(prices),
            'min': min(prices),
            'max': max(prices),
            'quartile_25': np.percentile(prices, 25),
            'quartile_75': np.percentile(prices, 75)
        }
    
    def _calculate_size_statistics(self, sizes: List[float]) -> Dict[str, float]:
        """Calculate size statistics"""
        if not sizes:
            return {}
        
        return {
            'count': len(sizes),
            'mean': np.mean(sizes),
            'median': np.median(sizes),
            'std': np.std(sizes),
            'min': min(sizes),
            'max': max(sizes)
        }
    
    def _calculate_geographic_spread(self, properties: List[PropertyData]) -> Dict[str, float]:
        """Calculate geographic spread metrics"""
        coords = [(p.latitude, p.longitude) for p in properties if p.latitude and p.longitude]
        
        if len(coords) < 2:
            return {'spread_meters': 0.0}
        
        # Calculate max distance between any two points
        max_distance = 0.0
        for i, coord1 in enumerate(coords):
            for coord2 in coords[i+1:]:
                distance = geodesic(coord1, coord2).meters
                max_distance = max(max_distance, distance)
        
        return {'spread_meters': max_distance}
    
    def _collect_validation_flags(self, properties: List[PropertyData]) -> List[str]:
        """Collect all validation flags from properties"""
        all_flags = []
        for prop in properties:
            all_flags.extend(prop.validation_flags)
        return list(set(all_flags))
    
    def _assess_area_quality(self, analysis_results: List[AnalysisResult], 
                           area_config) -> Dict[str, Any]:
        """Assess overall quality of area analysis"""
        if not analysis_results:
            return {'overall_score': 0.0, 'meets_threshold': False}
        
        # Calculate average quality metrics
        completeness_scores = [r.quality_metrics['completeness_score'] for r in analysis_results]
        validation_scores = [r.quality_metrics['validation_score'] for r in analysis_results]
        
        overall_score = (np.mean(completeness_scores) + np.mean(validation_scores)) / 2
        meets_threshold = overall_score >= area_config.quality_threshold
        
        return {
            'overall_score': overall_score,
            'meets_threshold': meets_threshold,
            'completeness_average': np.mean(completeness_scores),
            'validation_average': np.mean(validation_scores),
            'building_blocks_analyzed': len(analysis_results)
        }
    
    def _create_statistical_overview(self, analysis_results: List[AnalysisResult]) -> Dict[str, Any]:
        """Create statistical overview across all building blocks"""
        all_properties = []
        for result in analysis_results:
            all_properties.extend(result.properties)
        
        energy_classes = [p.energy_class for p in all_properties if p.energy_class]
        prices = [p.price for p in all_properties if p.price]
        sizes = [p.sqm for p in all_properties if p.sqm]
        
        return {
            'total_properties': len(all_properties),
            'energy_class_coverage': len(energy_classes) / len(all_properties) if all_properties else 0,
            'most_common_energy_class': max(set(energy_classes), key=energy_classes.count) if energy_classes else None,
            'price_range': {'min': min(prices), 'max': max(prices)} if prices else None,
            'size_range': {'min': min(sizes), 'max': max(sizes)} if sizes else None
        }
    
    def _generate_recommendations(self, analysis_results: List[AnalysisResult], 
                                area_config) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        if not analysis_results:
            recommendations.append("No building blocks found - consider expanding search criteria")
            return recommendations
        
        # Data quality recommendations
        avg_completeness = np.mean([r.quality_metrics['completeness_score'] for r in analysis_results])
        if avg_completeness < 0.7:
            recommendations.append("Data completeness is low - consider additional data collection")
        
        # Sample size recommendations
        small_blocks = [r for r in analysis_results if r.building_block.sample_size < 5]
        if len(small_blocks) > len(analysis_results) * 0.5:
            recommendations.append("Many building blocks have small sample sizes - consider merging nearby blocks")
        
        # Energy class recommendations
        blocks_without_energy = [r for r in analysis_results 
                               if r.building_block.weighted_energy_class == "Unknown"]
        if len(blocks_without_energy) > 0:
            recommendations.append(f"{len(blocks_without_energy)} blocks lack energy class data - prioritize energy assessment")
        
        return recommendations
    
    def _assess_data_quality(self, properties: List[PropertyData]) -> List[str]:
        """Assess overall data quality flags"""
        flags = []
        
        if not properties:
            flags.append("no_properties_found")
            return flags
        
        # Check completeness
        address_coverage = sum(1 for p in properties if p.address) / len(properties)
        if address_coverage < 0.9:
            flags.append("low_address_coverage")
        
        energy_coverage = sum(1 for p in properties if p.energy_class) / len(properties)
        if energy_coverage < 0.5:
            flags.append("low_energy_class_coverage")
        
        price_coverage = sum(1 for p in properties if p.price) / len(properties)
        if price_coverage < 0.8:
            flags.append("low_price_coverage")
        
        return flags

# Example usage
async def test_comprehensive_analysis():
    """Test the comprehensive analysis system"""
    
    # Create output directories
    create_output_directories(config)
    
    engine = ComprehensiveAnalysisEngine()
    
    # Test with Kolonaki area
    kolonaki_config = config.get_area_by_name("Kolonaki_Premium")
    
    result = await engine.analyze_area_comprehensive(kolonaki_config)
    
    if result:
        print("Analysis completed successfully!")
        print(f"Found: {result['discovery_summary']['total_properties_found']} properties")
        print(f"Created: {result['discovery_summary']['building_blocks_created']} building blocks")
    else:
        print("Analysis failed")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_analysis())