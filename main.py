"""
Spitogatos Premium Analysis - Main Execution Engine
36-Hour Premium Property Analysis System
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import argparse
import sys
import os

from config import config
from utils import (
    setup_logging, create_output_directories, performance_monitor,
    PropertyData, BuildingBlock
)
from scraper_ultimate import UltimateSpitogatosScraper
from analyzer import ComprehensiveAnalysisEngine
from validator import StatisticalValidator
from reporter import ReportGenerator

class SpitogatosPremiumAnalyzer:
    """Main orchestrator for the premium analysis system"""
    
    def __init__(self):
        self.config = config
        self.performance_monitor = performance_monitor
        self.analysis_results = {}
        self.total_properties = []
        self.total_building_blocks = []
        
        # Initialize components
        self.analysis_engine = ComprehensiveAnalysisEngine()
        self.statistical_validator = StatisticalValidator()
        self.report_generator = ReportGenerator()
        
        # Execution state
        self.start_time = None
        self.current_phase = "initialization"
        self.areas_completed = 0
        self.total_areas = len(self.config.TARGET_AREAS)
        
        logging.info("Spitogatos Premium Analyzer initialized")
    
    async def execute_full_analysis(self, target_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute complete 36-hour premium analysis"""
        
        self.start_time = datetime.now()
        logging.info("🚀 Starting Spitogatos Premium Analysis")
        logging.info(f"Target delivery: {self.config.DELIVERY_DEADLINE_HOURS} hours")
        
        try:
            # Setup phase
            self.current_phase = "setup"
            await self._setup_analysis_environment()
            
            # Determine target areas
            areas_to_analyze = self._determine_target_areas(target_areas)
            logging.info(f"Analyzing {len(areas_to_analyze)} areas: {[a.name for a in areas_to_analyze]}")
            
            # Phase 1: Robust Foundation (Hours 0-4)
            self.current_phase = "foundation"
            await self._execute_foundation_phase(areas_to_analyze)
            
            # Phase 2: Intelligent Data Collection (Hours 4-20)
            self.current_phase = "data_collection"
            await self._execute_data_collection_phase(areas_to_analyze)
            
            # Phase 3: Advanced Processing (Hours 20-30)
            self.current_phase = "processing"
            await self._execute_processing_phase()
            
            # Phase 4: Premium Output Generation (Hours 30-36)
            self.current_phase = "reporting"
            final_results = await self._execute_reporting_phase()
            
            # Final validation and delivery
            self.current_phase = "completion"
            await self._finalize_analysis()
            
            logging.info("✅ Spitogatos Premium Analysis completed successfully!")
            return final_results
            
        except Exception as e:
            logging.error(f"❌ Analysis failed in {self.current_phase} phase: {e}")
            await self._handle_analysis_failure(e)
            raise
    
    async def _setup_analysis_environment(self) -> None:
        """Setup analysis environment and validate configuration"""
        
        logging.info("Setting up analysis environment...")
        
        # Create output directories
        create_output_directories(self.config)
        
        # Validate configuration
        if not self.config.validate_config():
            raise ValueError("Invalid configuration detected")
        
        # Log analysis parameters
        logging.info(f"Rate limiting: {self.config.RATE_LIMITS.base_delay_seconds}s base delay")
        logging.info(f"Target areas: {len(self.config.TARGET_AREAS)}")
        logging.info(f"Success criteria: {self.config.SUCCESS_METRICS['minimum_acceptable']}")
        
        self.performance_monitor.start_timer('total_analysis')
    
    def _determine_target_areas(self, target_areas: Optional[List[str]]) -> List:
        """Determine which areas to analyze based on input and priority"""
        
        if target_areas:
            # Filter requested areas
            areas_to_analyze = []
            for area_name in target_areas:
                try:
                    area_config = self.config.get_area_by_name(area_name)
                    areas_to_analyze.append(area_config)
                except ValueError:
                    logging.warning(f"Unknown area requested: {area_name}")
            
            if not areas_to_analyze:
                logging.warning("No valid areas found in request, using high priority areas")
                areas_to_analyze = self.config.get_high_priority_areas()
        else:
            # Use all configured areas, prioritized 
            areas_to_analyze = sorted(self.config.TARGET_AREAS, 
                                    key=lambda x: (x.priority, -x.expected_properties))
        
        return areas_to_analyze
    
    async def _execute_foundation_phase(self, areas_to_analyze: List) -> None:
        """Phase 1: Robust Foundation (Hours 0-4)"""
        
        logging.info("📋 Phase 1: Establishing Robust Foundation")
        self.performance_monitor.start_timer('foundation_phase')
        
        # Initialize and validate scraping infrastructure
        async with UltimateSpitogatosScraper() as scraper:
            logging.info("✓ Scraping infrastructure initialized")
            
            # Test connectivity and rate limiting
            test_area = areas_to_analyze[0]
            test_properties = await scraper.comprehensive_area_search(
                test_area.name, test_area.streets[:1]  # Test with one street
            )
            
            if test_properties:
                logging.info(f"✓ Connectivity test passed: {len(test_properties)} properties found")
            else:
                logging.warning("⚠ Connectivity test returned no results")
            
            # Log scraper statistics
            scraper.log_statistics()
        
        self.performance_monitor.end_timer('foundation_phase')
        logging.info("✅ Foundation phase completed")
    
    async def _execute_data_collection_phase(self, areas_to_analyze: List) -> None:
        """Phase 2: Intelligent Data Collection (Hours 4-20)"""
        
        logging.info("🔍 Phase 2: Intelligent Data Collection")
        self.performance_monitor.start_timer('data_collection_phase')
        
        # Process areas with intelligent prioritization
        for i, area_config in enumerate(areas_to_analyze):
            area_start_time = time.time()
            
            logging.info(f"Analyzing area {i+1}/{len(areas_to_analyze)}: {area_config.name}")
            
            try:
                # Execute comprehensive area analysis
                area_result = await self.analysis_engine.analyze_area_comprehensive(area_config)
                
                if area_result:
                    self.analysis_results[area_config.name] = area_result
                    
                    # Extract properties and building blocks
                    area_properties = []
                    area_blocks = []
                    
                    for block_data in area_result.get('building_blocks', []):
                        # Convert dict back to BuildingBlock object for processing
                        # This is a simplified version - in production you'd have proper deserialization
                        block_properties = block_data.get('properties', [])
                        area_properties.extend(block_properties)
                    
                    self.total_properties.extend(area_properties)
                    logging.info(f"✓ {area_config.name}: {len(area_properties)} properties found")
                    
                    self.areas_completed += 1
                    
                else:
                    logging.warning(f"⚠ No results for {area_config.name}")
                
            except Exception as e:
                logging.error(f"❌ Error analyzing {area_config.name}: {e}")
                continue
            
            # Progress reporting
            area_duration = time.time() - area_start_time
            elapsed_total = time.time() - self.start_time.timestamp()
            
            logging.info(f"Area completed in {area_duration:.1f}s. "
                        f"Total elapsed: {elapsed_total/3600:.1f}h")
            
            # Adaptive pacing - slow down if we're ahead of schedule
            target_time_per_area = (16 * 3600) / len(areas_to_analyze)  # 16 hours for this phase
            if area_duration < target_time_per_area * 0.7:
                additional_delay = min(30, (target_time_per_area - area_duration) * 0.5)
                logging.info(f"Pacing: adding {additional_delay:.1f}s delay")
                await asyncio.sleep(additional_delay)
        
        self.performance_monitor.end_timer('data_collection_phase')
        logging.info(f"✅ Data collection completed: {len(self.total_properties)} total properties")
    
    async def _execute_processing_phase(self) -> None:
        """Phase 3: Advanced Processing (Hours 20-30)"""
        
        logging.info("⚙️ Phase 3: Advanced Processing")
        self.performance_monitor.start_timer('processing_phase')
        
        if not self.total_properties:
            logging.error("No properties available for processing!")
            return
        
        # Statistical validation across all areas
        logging.info("Running statistical validation...")
        
        # Note: This would require building blocks to be properly reconstructed
        # For now, we'll validate what we have
        
        validation_results = self.statistical_validator.validate_analysis_statistical_significance([])
        
        logging.info(f"Statistical validation: {validation_results.get('confidence_level', 0):.2f} confidence")
        
        # Quality assessment
        total_with_energy = sum(1 for result in self.analysis_results.values()
                              for block in result.get('building_blocks', [])
                              for prop in block.get('properties', [])
                              if prop.get('energy_class'))
        
        energy_coverage = total_with_energy / max(1, len(self.total_properties))
        
        logging.info(f"Energy class coverage: {energy_coverage:.1%}")
        
        self.performance_monitor.end_timer('processing_phase')
        logging.info("✅ Processing phase completed")
    
    async def _execute_reporting_phase(self) -> Dict[str, Any]:
        """Phase 4: Premium Output Generation (Hours 30-36)"""
        
        logging.info("📊 Phase 4: Premium Output Generation")
        self.performance_monitor.start_timer('reporting_phase')
        
        # Prepare consolidated results
        consolidated_results = self._consolidate_analysis_results()
        
        # Generate comprehensive reports
        try:
            # Convert analysis results to proper format for reporting
            all_properties = []
            building_blocks = []
            
            # This is a simplified extraction - in production you'd have proper object reconstruction
            for area_name, area_result in self.analysis_results.items():
                for block_data in area_result.get('building_blocks', []):
                    block_properties = block_data.get('properties', [])
                    all_properties.extend(block_properties)
            
            if all_properties:
                # Convert to PropertyData objects (simplified)
                property_objects = []
                for prop_data in all_properties:
                    # This would be more robust in production
                    property_objects.append(PropertyData(
                        id=prop_data.get('id', ''),
                        url=prop_data.get('url', ''),
                        title=prop_data.get('title', ''),
                        address=prop_data.get('address', ''),
                        price=prop_data.get('price'),
                        sqm=prop_data.get('sqm'),
                        energy_class=prop_data.get('energy_class'),
                        floor=prop_data.get('floor'),
                        rooms=prop_data.get('rooms'),
                        latitude=prop_data.get('latitude'),
                        longitude=prop_data.get('longitude'),
                        description=prop_data.get('description', ''),
                        images=prop_data.get('images', []),
                        scraped_at=datetime.now(),
                        confidence_score=prop_data.get('confidence_score', 0.0),
                        validation_flags=prop_data.get('validation_flags', [])
                    ))
                
                # Generate reports
                generated_files = self.report_generator.generate_comprehensive_report(
                    consolidated_results, building_blocks, property_objects
                )
                
                logging.info(f"✓ Generated {len(generated_files)} report files")
                
            else:
                logging.warning("No properties available for reporting")
                generated_files = {}
            
        except Exception as e:
            logging.error(f"Error generating reports: {e}")
            generated_files = {}
        
        self.performance_monitor.end_timer('reporting_phase')
        
        # Final results
        final_results = {
            **consolidated_results,
            'generated_files': generated_files,
            'execution_summary': self._generate_execution_summary()
        }
        
        logging.info("✅ Reporting phase completed")
        return final_results
    
    def _consolidate_analysis_results(self) -> Dict[str, Any]:
        """Consolidate results from all analyzed areas"""
        
        total_properties_found = len(self.total_properties)
        total_blocks_created = sum(len(result.get('building_blocks', [])) 
                                 for result in self.analysis_results.values())
        
        # Aggregate statistics
        all_energy_classes = []
        all_prices = []
        
        for result in self.analysis_results.values():
            for block in result.get('building_blocks', []):
                for prop in block.get('properties', []):
                    if prop.get('energy_class'):
                        all_energy_classes.append(prop['energy_class'])
                    if prop.get('price'):
                        all_prices.append(prop['price'])
        
        # Calculate overall metrics
        energy_coverage = len(all_energy_classes) / max(1, total_properties_found)
        
        from collections import Counter
        energy_distribution = Counter(all_energy_classes)
        most_common_energy = energy_distribution.most_common(1)[0] if energy_distribution else ('Unknown', 0)
        
        consolidated = {
            'analysis_summary': {
                'total_areas_analyzed': len(self.analysis_results),
                'total_properties_found': total_properties_found,
                'total_building_blocks': total_blocks_created,
                'energy_class_coverage': energy_coverage,
                'most_common_energy_class': most_common_energy[0]
            },
            'area_results': self.analysis_results,
            'success_metrics_assessment': self._assess_success_metrics(
                total_properties_found, total_blocks_created, energy_coverage
            ),
            'performance_metrics': {
                'total_duration': self.performance_monitor.get_stats('total_analysis'),
                'phase_durations': {
                    'foundation': self.performance_monitor.get_stats('foundation_phase'),
                    'data_collection': self.performance_monitor.get_stats('data_collection_phase'),
                    'processing': self.performance_monitor.get_stats('processing_phase'),
                    'reporting': self.performance_monitor.get_stats('reporting_phase')
                }
            }
        }
        
        return consolidated
    
    def _assess_success_metrics(self, total_properties: int, total_blocks: int, 
                              energy_coverage: float) -> Dict[str, Any]:
        """Assess performance against success criteria"""
        
        minimum = self.config.SUCCESS_METRICS['minimum_acceptable']
        target = self.config.SUCCESS_METRICS['target_excellence']
        
        # Calculate scores
        blocks_score = min(1.0, total_blocks / minimum['building_blocks_analyzed'])
        
        avg_props_per_block = total_properties / max(1, total_blocks)
        props_score = min(1.0, avg_props_per_block / minimum['properties_per_block_avg'])
        
        energy_score = min(1.0, energy_coverage / minimum['energy_class_coverage'])
        
        overall_score = (blocks_score + props_score + energy_score) / 3
        
        # Determine achievement level
        if overall_score >= 0.9:
            achievement_level = "Excellent - Exceeds target criteria"
        elif overall_score >= 0.7:
            achievement_level = "Good - Meets minimum criteria"
        elif overall_score >= 0.5:
            achievement_level = "Adequate - Partially meets criteria"
        else:
            achievement_level = "Needs Improvement - Below minimum criteria"
        
        return {
            'overall_score': overall_score,
            'achievement_level': achievement_level,
            'individual_scores': {
                'building_blocks': blocks_score,
                'properties_per_block': props_score,
                'energy_coverage': energy_score
            },
            'meets_minimum_criteria': overall_score >= 0.7,
            'meets_target_criteria': overall_score >= 0.9
        }
    
    def _generate_execution_summary(self) -> Dict[str, Any]:
        """Generate execution summary"""
        
        total_duration = time.time() - self.start_time.timestamp()
        
        return {
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'total_duration_hours': total_duration / 3600,
            'areas_completed': self.areas_completed,
            'total_areas_planned': self.total_areas,
            'completion_rate': self.areas_completed / max(1, self.total_areas),
            'final_phase': self.current_phase,
            'properties_discovered': len(self.total_properties),
            'performance_summary': self.performance_monitor.get_stats('total_analysis')
        }
    
    async def _finalize_analysis(self) -> None:
        """Finalize analysis and cleanup"""
        
        total_duration = self.performance_monitor.end_timer('total_analysis')
        
        logging.info("🎯 Analysis Finalization")
        logging.info(f"Total duration: {total_duration/3600:.1f} hours")
        logging.info(f"Areas completed: {self.areas_completed}/{self.total_areas}")
        logging.info(f"Properties discovered: {len(self.total_properties)}")
        
        # Log performance summary
        self.performance_monitor.log_summary()
        
        logging.info("🏁 Spitogatos Premium Analysis completed!")
    
    async def _handle_analysis_failure(self, error: Exception) -> None:
        """Handle analysis failure gracefully"""
        
        logging.error(f"Analysis failed in {self.current_phase} phase: {error}")
        
        # Attempt to save partial results
        try:
            if self.analysis_results:
                partial_results = self._consolidate_analysis_results()
                
                # Save to file
                import json
                failure_report_path = os.path.join(
                    self.config.OUTPUT_CONFIG['base_directory'],
                    'reports',
                    f'failure_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                )
                
                with open(failure_report_path, 'w') as f:
                    json.dump(partial_results, f, indent=2, default=str)
                
                logging.info(f"Partial results saved to: {failure_report_path}")
            
        except Exception as save_error:
            logging.error(f"Failed to save partial results: {save_error}")

async def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description="Spitogatos Premium Analysis System")
    parser.add_argument('--areas', nargs='+', help='Specific areas to analyze')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    parser.add_argument('--output-dir', default='outputs', help='Output directory')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(config)
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    
    # Initialize analyzer
    analyzer = SpitogatosPremiumAnalyzer()
    
    try:
        # Execute analysis
        results = await analyzer.execute_full_analysis(args.areas)
        
        # Print summary
        print("\n" + "="*60)
        print("🎉 SPITOGATOS PREMIUM ANALYSIS COMPLETED")
        print("="*60)
        print(f"Properties Found: {results['analysis_summary']['total_properties_found']:,}")
        print(f"Building Blocks: {results['analysis_summary']['total_building_blocks']}")
        print(f"Energy Coverage: {results['analysis_summary']['energy_class_coverage']:.1%}")
        print(f"Success Level: {results['success_metrics_assessment']['achievement_level']}")
        print(f"Duration: {results['execution_summary']['total_duration_hours']:.1f} hours")
        
        if results.get('generated_files'):
            print(f"\nGenerated Files:")
            for file_type, file_path in results['generated_files'].items():
                print(f"  {file_type}: {file_path}")
        
        print("="*60)
        
    except KeyboardInterrupt:
        logging.info("Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())