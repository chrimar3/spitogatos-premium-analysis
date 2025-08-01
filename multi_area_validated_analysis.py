#!/usr/bin/env python3
"""
Multi-Area Validated Analysis
Analyze multiple Athens areas: Kolonaki, Exarchia, Kipseli, Pangrati
Using validated real data only for comprehensive city block analysis
"""

import asyncio
import logging
import json
from typing import List, Dict, Any
from datetime import datetime

from validated_real_data_scraper import ValidatedRealDataScraper

logging.basicConfig(level=logging.INFO)

class MultiAreaValidatedAnalysis:
    """Multi-area analysis using only validated real data"""
    
    def __init__(self):
        self.validated_scraper = ValidatedRealDataScraper()
        
        # Target areas for comprehensive analysis
        self.target_areas = [
            'Kolonaki',
            'Exarchia', 
            'Kipseli',
            'Pangrati'
        ]
        
        logging.info("🏙️ MULTI-AREA VALIDATED ANALYSIS")
        logging.info(f"📋 Target areas: {', '.join(self.target_areas)}")
        logging.info("🔒 Using strict validation - only real data")
    
    async def analyze_all_areas(self) -> Dict[str, Any]:
        """Analyze all target areas with validated data"""
        
        logging.info("🎯 COMPREHENSIVE MULTI-AREA ANALYSIS")
        logging.info("=" * 60)
        
        all_results = {
            'analysis_summary': {
                'timestamp': datetime.now().isoformat(),
                'areas_analyzed': [],
                'total_properties': 0,
                'successful_areas': 0,
                'data_quality': 'validated_real_only'
            },
            'areas': {},
            'city_blocks': []
        }
        
        for area in self.target_areas:
            logging.info(f"\n🏙️ ANALYZING {area.upper()}")
            logging.info("=" * 40)
            
            try:
                # Extract validated properties for this area
                validated_properties = await self.validated_scraper.get_strictly_validated_properties(area)
                
                if validated_properties:
                    logging.info(f"✅ {area}: {len(validated_properties)} validated properties")
                    
                    # Create city blocks from validated properties
                    area_blocks = self.create_city_blocks_from_properties(validated_properties, area)
                    
                    # Store area results
                    all_results['areas'][area] = {
                        'properties_count': len(validated_properties),
                        'city_blocks_count': len(area_blocks),
                        'validation_stats': self._calculate_validation_stats(validated_properties),
                        'status': 'success'
                    }
                    
                    # Add blocks to overall collection
                    all_results['city_blocks'].extend(area_blocks)
                    
                    # Update summary
                    all_results['analysis_summary']['areas_analyzed'].append(area)
                    all_results['analysis_summary']['total_properties'] += len(validated_properties)
                    all_results['analysis_summary']['successful_areas'] += 1
                    
                    # Log area statistics
                    self._log_area_statistics(area, validated_properties, area_blocks)
                
                else:
                    logging.warning(f"❌ {area}: No validated properties found")
                    all_results['areas'][area] = {
                        'properties_count': 0,
                        'status': 'no_validated_data'
                    }
                
            except Exception as e:
                logging.error(f"❌ {area} analysis failed: {e}")
                all_results['areas'][area] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # Brief pause between areas
            await asyncio.sleep(3)
        
        # Generate final comprehensive report
        self._generate_comprehensive_report(all_results)
        
        return all_results
    
    def create_city_blocks_from_properties(self, properties: List, area_name: str) -> List[Dict[str, Any]]:
        """Create city blocks from validated properties"""
        
        city_blocks = []
        
        # Group properties into blocks of 15+ properties each
        min_block_size = 10  # Minimum properties per block
        target_block_size = 15  # Target properties per block
        
        for i in range(0, len(properties), target_block_size):
            block_properties = properties[i:i + target_block_size]
            
            if len(block_properties) >= min_block_size:
                block_id = f"{area_name}_ValidatedBlock_{len(city_blocks) + 1:02d}"
                
                # Calculate block statistics
                total_sqm = sum(p.sqm for p in block_properties if p.sqm)
                prices = [p.price for p in block_properties if p.price]
                areas = [p.sqm for p in block_properties if p.sqm]
                
                # Calculate weighted median energy class
                energy_classes = [(p.energy_class, p.sqm) for p in block_properties if p.energy_class and p.sqm]
                weighted_median_energy = self._calculate_weighted_median_energy(energy_classes)
                
                # Create city block
                city_block = {
                    'block_id': block_id,
                    'area_name': area_name,
                    'properties_count': len(block_properties),
                    'total_sqm': total_sqm,
                    'weighted_median_energy_class': weighted_median_energy,
                    'price_statistics': {
                        'min': min(prices) if prices else 0,
                        'max': max(prices) if prices else 0,
                        'average': sum(prices) / len(prices) if prices else 0
                    },
                    'area_statistics': {
                        'min_sqm': min(areas) if areas else 0,
                        'max_sqm': max(areas) if areas else 0,
                        'average_sqm': sum(areas) / len(areas) if areas else 0
                    },
                    'energy_class_breakdown': self._get_energy_breakdown(block_properties),
                    'avg_price_per_sqm': (sum(prices) / len(prices)) / (sum(areas) / len(areas)) if prices and areas else 0,
                    'data_quality': 'validated_real_only'
                }
                
                city_blocks.append(city_block)
        
        return city_blocks
    
    def _calculate_weighted_median_energy(self, energy_classes: List[tuple]) -> str:
        """Calculate weighted median energy class by square meters"""
        
        if not energy_classes:
            return None
        
        # Energy class to numeric mapping
        energy_values = {'A+': 7, 'A': 6, 'B': 5, 'C': 4, 'D': 3, 'E': 2, 'F': 1}
        reverse_mapping = {v: k for k, v in energy_values.items()}
        
        # Create weighted list
        weighted_values = []
        for energy_class, sqm in energy_classes:
            if energy_class in energy_values:
                # Add the energy value repeated by sqm times (weighted by area)
                weighted_values.extend([energy_values[energy_class]] * int(sqm))
        
        if not weighted_values:
            return None
        
        # Calculate median of weighted values
        weighted_values.sort()
        n = len(weighted_values)
        
        if n % 2 == 1:
            median_value = weighted_values[n // 2]
        else:
            median_value = (weighted_values[n // 2 - 1] + weighted_values[n // 2]) / 2
        
        # Convert back to energy class
        closest_value = round(median_value)
        return reverse_mapping.get(closest_value, 'C')
    
    def _get_energy_breakdown(self, properties: List) -> Dict[str, int]:
        """Get energy class breakdown for properties"""
        
        breakdown = {}
        for prop in properties:
            if prop.energy_class:
                breakdown[prop.energy_class] = breakdown.get(prop.energy_class, 0) + 1
        return breakdown
    
    def _calculate_validation_stats(self, properties: List) -> Dict[str, Any]:
        """Calculate validation statistics"""
        
        total = len(properties)
        with_price = len([p for p in properties if p.price])
        with_sqm = len([p for p in properties if p.sqm])
        with_energy = len([p for p in properties if p.energy_class])
        
        return {
            'total_properties': total,
            'price_completeness': with_price / total if total > 0 else 0,
            'area_completeness': with_sqm / total if total > 0 else 0,
            'energy_completeness': with_energy / total if total > 0 else 0,
            'validation_approach': 'strict_real_data_only'
        }
    
    def _log_area_statistics(self, area: str, properties: List, blocks: List[Dict[str, Any]]):
        """Log detailed statistics for an area"""
        
        logging.info(f"\n📊 {area.upper()} STATISTICS:")
        logging.info(f"   Properties: {len(properties)} (validated)")
        logging.info(f"   City blocks: {len(blocks)}")
        
        if properties:
            prices = [p.price for p in properties if p.price]
            areas = [p.sqm for p in properties if p.sqm]
            energy_count = len([p for p in properties if p.energy_class])
            
            if prices and areas:
                avg_price_per_sqm = sum(p.price/p.sqm for p in properties if p.price and p.sqm) / len([p for p in properties if p.price and p.sqm])
                logging.info(f"   Price range: €{min(prices):,.0f} - €{max(prices):,.0f}")
                logging.info(f"   Area range: {min(areas):.0f}m² - {max(areas):.0f}m²")
                logging.info(f"   Avg price/m²: €{avg_price_per_sqm:.0f}")
            
            logging.info(f"   Energy class data: {energy_count}/{len(properties)} ({energy_count/len(properties)*100:.1f}%)")
    
    def _generate_comprehensive_report(self, results: Dict[str, Any]):
        """Generate comprehensive multi-area report"""
        
        logging.info("\n" + "=" * 80)
        logging.info("📋 COMPREHENSIVE MULTI-AREA ANALYSIS REPORT")
        logging.info("=" * 80)
        
        summary = results['analysis_summary']
        
        logging.info(f"\n🎯 OVERALL SUMMARY:")
        logging.info(f"   Areas analyzed: {summary['successful_areas']}/{len(self.target_areas)}")
        logging.info(f"   Total validated properties: {summary['total_properties']}")
        logging.info(f"   Total city blocks: {len(results['city_blocks'])}")
        logging.info(f"   Data quality: {summary['data_quality']}")
        
        # Area breakdown
        logging.info(f"\n🏙️ AREA BREAKDOWN:")
        for area, data in results['areas'].items():
            if data.get('status') == 'success':
                logging.info(f"   {area}: {data['properties_count']} properties → {data['city_blocks_count']} blocks")
            else:
                logging.info(f"   {area}: {data.get('status', 'unknown status')}")
        
        # City blocks summary
        if results['city_blocks']:
            logging.info(f"\n🏗️ CITY BLOCKS SUMMARY:")
            for block in results['city_blocks']:
                energy_info = f"Energy: {block['weighted_median_energy_class']}" if block['weighted_median_energy_class'] else "Energy: N/A"
                logging.info(f"   {block['block_id']}: {block['properties_count']} properties, {block['total_sqm']}m², {energy_info}")
        
        # Save comprehensive report
        output_file = "outputs/multi_area_validated_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logging.info(f"\n💾 Comprehensive report saved: {output_file}")
        
        # Success metrics
        if len(results['city_blocks']) >= 10:
            logging.info(f"\n🎉 SUCCESS: {len(results['city_blocks'])} city blocks created (target: 10+)")
        else:
            logging.info(f"\n📊 Progress: {len(results['city_blocks'])} city blocks created (target: 10)")
        
        if summary['total_properties'] >= 150:
            logging.info(f"🎉 EXCELLENT: {summary['total_properties']} validated properties (target: 150+)")
        else:
            logging.info(f"📈 Good: {summary['total_properties']} validated properties")


async def main():
    """Run comprehensive multi-area validated analysis"""
    
    print("🏙️ MULTI-AREA VALIDATED ANALYSIS")
    print("=" * 70)
    print("🎯 Analyzing: Kolonaki, Exarchia, Kipseli, Pangrati")
    print("🔒 Using strict validation for real data only")
    print("=" * 70)
    
    analyzer = MultiAreaValidatedAnalysis()
    
    # Run comprehensive analysis
    results = await analyzer.analyze_all_areas()
    
    # Final summary
    print(f"\n🎉 MULTI-AREA ANALYSIS COMPLETE:")
    print(f"   Successful areas: {results['analysis_summary']['successful_areas']}")
    print(f"   Total properties: {results['analysis_summary']['total_properties']} (100% validated)")
    print(f"   City blocks created: {len(results['city_blocks'])}")
    print(f"   Report: outputs/multi_area_validated_analysis.json")

if __name__ == "__main__":
    asyncio.run(main())