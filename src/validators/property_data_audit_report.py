#!/usr/bin/env python3
"""
Property Data Audit Report - Raw Data Validation
Creates detailed report of all properties examined with URLs, addresses, sqm, energy classes
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import re

class PropertyDataAuditReport:
    """Generate detailed audit report of all properties examined"""
    
    def __init__(self):
        self.analysis_data = None
        print("🔍 Property Data Audit Report Generator")
    
    def load_analysis_data(self, file_path: str = 'outputs/comprehensive_multi_area_analysis.json'):
        """Load comprehensive analysis data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.analysis_data = json.load(f)
            print(f"✅ Analysis data loaded: {self.analysis_data['analysis_summary']['total_city_blocks']} blocks")
            return True
        except FileNotFoundError:
            print(f"❌ Analysis file not found: {file_path}")
            return False
    
    def create_comprehensive_audit_report(self) -> Dict[str, Any]:
        """Create comprehensive audit report with all property details"""
        
        if not self.analysis_data:
            print("❌ No analysis data loaded")
            return {}
        
        print("🔍 Creating Comprehensive Property Audit Report...")
        
        # ⚠️ CRITICAL ISSUE DISCOVERED ⚠️
        print("\n🚨 CRITICAL DATA ISSUE IDENTIFIED:")
        print("The current analysis data contains AGGREGATED city block summaries,")
        print("but does NOT contain the individual property URLs and detailed data!")
        print("\nThis means we cannot validate:")
        print("- Individual property URLs from xe.gr")
        print("- Specific addresses and street names") 
        print("- Individual property square meters")
        print("- Individual energy class ratings")
        print("\nThe analysis was based on SYNTHETIC city block data,")
        print("not actual scraped property records!")
        
        # Generate what we CAN audit from existing data
        audit_report = self._create_available_data_audit()
        
        # Flag the critical data validation issue
        audit_report['CRITICAL_VALIDATION_ISSUE'] = {
            'issue': 'Missing individual property data for validation',
            'impact': 'Cannot verify URLs, addresses, or individual property details',
            'current_data': 'Aggregated city block summaries only',
            'required_for_validation': [
                'Individual property URLs from xe.gr',
                'Specific street addresses', 
                'Individual property square meters',
                'Individual energy class ratings',
                'Scraping timestamps and source verification'
            ],
            'recommendation': 'Re-run analysis with property-level data retention'
        }
        
        # Save audit report
        output_file = 'outputs/property_data_audit_report.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(audit_report, f, indent=2, ensure_ascii=False, default=str)
        
        # Create detailed Excel report
        self._create_excel_audit_report(audit_report)
        
        print(f"✅ Audit report saved: {output_file}")
        
        return audit_report
    
    def _create_available_data_audit(self) -> Dict[str, Any]:
        """Create audit report from available aggregated data"""
        
        audit_sections = {
            'audit_metadata': {
                'audit_timestamp': datetime.now().isoformat(),
                'data_source': 'Aggregated city block analysis',
                'total_blocks_claimed': len(self.analysis_data['city_blocks']),
                'total_properties_claimed': self.analysis_data['analysis_summary']['total_properties'],
                'areas_analyzed': self.analysis_data['analysis_summary']['areas_included']
            },
            
            'data_availability_audit': self._audit_data_availability(),
            'city_block_summary_audit': self._audit_city_block_summaries(),
            'energy_distribution_audit': self._audit_energy_distributions(),
            'pricing_data_audit': self._audit_pricing_data(),
            'geographic_data_audit': self._audit_geographic_data(),
            'data_quality_flags': self._identify_data_quality_issues()
        }
        
        return audit_sections
    
    def _audit_data_availability(self) -> Dict[str, Any]:
        """Audit what data is actually available vs claimed"""
        
        available_fields = set()
        missing_fields = set()
        
        # Check each city block for available fields
        for block in self.analysis_data['city_blocks']:
            for field in block.keys():
                available_fields.add(field)
        
        # Fields we NEED for validation but don't have
        required_fields = {
            'individual_property_urls',
            'individual_property_addresses', 
            'individual_property_sqm',
            'individual_energy_classes',
            'scraping_source_verification',
            'property_ids',
            'scraping_timestamps'
        }
        
        missing_fields = required_fields - available_fields
        
        return {
            'available_fields': list(available_fields),
            'missing_critical_fields': list(missing_fields),
            'validation_possible': len(missing_fields) == 0,
            'data_completeness_score': len(available_fields) / (len(available_fields) + len(missing_fields)),
            'critical_issue': 'Individual property data not retained for validation'
        }
    
    def _audit_city_block_summaries(self) -> List[Dict[str, Any]]:
        """Audit city block summary data"""
        
        block_audits = []
        
        for block in self.analysis_data['city_blocks']:
            block_audit = {
                'block_id': block['block_id'],
                'claimed_properties': block['properties_count'],
                'claimed_total_sqm': block['total_sqm'],
                'weighted_median_energy': block['weighted_median_energy_class'],
                'energy_breakdown': block['energy_class_breakdown'],
                'avg_price_per_sqm': block['avg_price_per_sqm'],
                'street_boundaries': block['street_boundaries'],
                
                # Validation flags
                'validation_issues': self._validate_block_data(block),
                'data_consistency_score': self._calculate_block_consistency_score(block),
                'suspicious_patterns': self._identify_suspicious_patterns(block)
            }
            
            block_audits.append(block_audit)
        
        return block_audits
    
    def _validate_block_data(self, block: Dict) -> List[str]:
        """Validate individual block data for issues"""
        
        issues = []
        
        # Check for unrealistic data
        if block['avg_price_per_sqm'] > 5000:
            issues.append(f"Extremely high price/m²: €{block['avg_price_per_sqm']}")
        
        if block['avg_price_per_sqm'] < 200:
            issues.append(f"Suspiciously low price/m²: €{block['avg_price_per_sqm']}")
        
        # Check energy distribution
        total_energy_props = sum(block['energy_class_breakdown'].values())
        if total_energy_props != block['properties_count']:
            issues.append(f"Energy breakdown ({total_energy_props}) doesn't match property count ({block['properties_count']})")
        
        # Check for energy class dominance
        if block['energy_class_breakdown'].get('A', 0) > block['properties_count'] * 0.5:
            issues.append("Suspicious A-class dominance (>50%)")
        
        # Check street boundaries
        if len(block['street_boundaries']) != 4:
            issues.append(f"Incorrect street boundary count: {len(block['street_boundaries'])}")
        
        # Check for generic street names
        generic_patterns = ['Street', 'Avenue', 'Square']
        if any(pattern in str(block['street_boundaries']) for pattern in generic_patterns):
            issues.append("Generic street names detected - likely synthetic data")
        
        return issues
    
    def _calculate_block_consistency_score(self, block: Dict) -> float:
        """Calculate data consistency score for block"""
        
        consistency_points = 0
        total_checks = 0
        
        # Price consistency check
        total_checks += 1
        if 300 <= block['avg_price_per_sqm'] <= 3000:  # Reasonable Athens range
            consistency_points += 1
        
        # Energy distribution realism
        total_checks += 1
        energy_breakdown = block['energy_class_breakdown']
        c_d_percentage = (energy_breakdown.get('C', 0) + energy_breakdown.get('D', 0)) / sum(energy_breakdown.values())
        if 0.4 <= c_d_percentage <= 0.8:  # Realistic C/D dominance
            consistency_points += 1
        
        # Property count reasonableness
        total_checks += 1
        if 10 <= block['properties_count'] <= 20:  # Reasonable block size
            consistency_points += 1
        
        # Area size reasonableness
        total_checks += 1
        if block['total_sqm'] > 0 and block['sqm_range']['avg'] > 0:
            consistency_points += 1
        
        return consistency_points / total_checks if total_checks > 0 else 0
    
    def _identify_suspicious_patterns(self, block: Dict) -> List[str]:
        """Identify suspicious data patterns"""
        
        suspicious = []
        
        # Perfect round numbers
        if block['properties_count'] == 15:  # Exactly 15 for most blocks
            suspicious.append("Suspiciously consistent property count (15)")
        
        # Generic street naming
        street_names = ' '.join(block['street_boundaries'])
        if 'Street' in street_names and 'Avenue' in street_names:
            suspicious.append("Generic English street names in Greek city")
        
        # Confidence score patterns
        if block['confidence_score'] == 1.0:
            suspicious.append("Perfect confidence score (100%) - unlikely for real data")
        
        # Energy class patterns
        energy_classes = list(block['energy_class_breakdown'].keys())
        if len(energy_classes) <= 2:
            suspicious.append("Too few energy classes for realistic block")
        
        return suspicious
    
    def _audit_energy_distributions(self) -> Dict[str, Any]:
        """Audit energy class distributions for realism"""
        
        # Aggregate all energy data
        total_energy_dist = {}
        total_properties = 0
        
        for block in self.analysis_data['city_blocks']:
            for energy, count in block['energy_class_breakdown'].items():
                total_energy_dist[energy] = total_energy_dist.get(energy, 0) + count
                total_properties += count
        
        # Calculate percentages
        energy_percentages = {
            energy: (count / total_properties * 100) 
            for energy, count in total_energy_dist.items()
        }
        
        # Compare to realistic Athens distribution
        realistic_athens = {
            'A+': 3, 'A': 7, 'B': 12, 'C': 35, 'D': 30, 'E': 10, 'F': 3
        }
        
        # Calculate deviations
        deviations = {}
        for energy in ['A+', 'A', 'B', 'C', 'D', 'E', 'F']:
            actual = energy_percentages.get(energy, 0)
            expected = realistic_athens[energy]
            deviation = actual - expected
            deviations[energy] = {
                'actual_percent': round(actual, 1),
                'expected_percent': expected,
                'deviation': round(deviation, 1),
                'deviation_ratio': round(deviation / expected, 2) if expected > 0 else float('inf')
            }
        
        return {
            'total_properties_with_energy': total_properties,
            'actual_distribution': energy_percentages,
            'expected_athens_distribution': realistic_athens,
            'deviations_analysis': deviations,
            'realism_assessment': self._assess_distribution_realism(deviations)
        }
    
    def _assess_distribution_realism(self, deviations: Dict) -> str:
        """Assess realism of energy distribution"""
        
        large_deviations = sum(1 for d in deviations.values() if abs(d['deviation']) > 10)
        
        if large_deviations >= 4:
            return "Highly unrealistic - major deviations from expected Athens distribution"
        elif large_deviations >= 2:
            return "Moderately unrealistic - some significant deviations"
        else:
            return "Reasonably realistic distribution"
    
    def _audit_pricing_data(self) -> Dict[str, Any]:
        """Audit pricing data for consistency"""
        
        all_prices = []
        price_ranges = []
        
        for block in self.analysis_data['city_blocks']:
            all_prices.append(block['avg_price_per_sqm'])
            price_ranges.append(block['price_range']['max'] - block['price_range']['min'])
        
        return {
            'avg_price_per_sqm_range': {
                'min': min(all_prices),
                'max': max(all_prices),
                'avg': sum(all_prices) / len(all_prices),
                'coefficient_of_variation': pd.Series(all_prices).std() / pd.Series(all_prices).mean()
            },
            'price_range_analysis': {
                'min_range': min(price_ranges),
                'max_range': max(price_ranges),
                'avg_range': sum(price_ranges) / len(price_ranges)
            },
            'pricing_realism': self._assess_pricing_realism(all_prices, price_ranges)
        }
    
    def _assess_pricing_realism(self, prices: List[float], ranges: List[float]) -> str:
        """Assess realism of pricing data"""
        
        # Check for unrealistic patterns
        if max(prices) > 4000:
            return "Some unrealistically high prices detected"
        elif min(prices) < 300:
            return "Some unrealistically low prices detected"
        elif max(ranges) > 500000:
            return "Suspiciously large price ranges within blocks"
        else:
            return "Pricing appears realistic for Athens market"
    
    def _audit_geographic_data(self) -> Dict[str, Any]:
        """Audit geographic data"""
        
        areas = {}
        
        for block in self.analysis_data['city_blocks']:
            area = block.get('area', block['block_id'].split('_')[0])
            if area not in areas:
                areas[area] = {
                    'blocks': 0,
                    'properties': 0,
                    'street_samples': []
                }
            
            areas[area]['blocks'] += 1
            areas[area]['properties'] += block['properties_count']
            areas[area]['street_samples'].extend(block['street_boundaries'][:2])  # Sample streets
        
        return {
            'areas_analyzed': areas,
            'geographic_coverage': len(areas),
            'geographic_realism': self._assess_geographic_realism(areas)
        }
    
    def _assess_geographic_realism(self, areas: Dict) -> str:
        """Assess realism of geographic data"""
        
        # Check for realistic Greek street names
        all_streets = []
        for area_data in areas.values():
            all_streets.extend(area_data['street_samples'])
        
        greek_patterns = ['οδός', 'λεωφόρος', 'πλατεία', 'street', 'avenue']
        greek_streets = sum(1 for street in all_streets 
                          if any(pattern.lower() in street.lower() for pattern in greek_patterns))
        
        if greek_streets == 0:
            return "No recognizable Greek street patterns - likely synthetic"
        elif greek_streets < len(all_streets) * 0.5:
            return "Mixed real/synthetic street names"
        else:
            return "Street names appear realistic"
    
    def _identify_data_quality_issues(self) -> List[Dict[str, Any]]:
        """Identify overall data quality issues"""
        
        issues = []
        
        # Issue 1: Missing individual property data
        issues.append({
            'severity': 'CRITICAL',
            'issue': 'Missing Individual Property Data',
            'description': 'Cannot validate URLs, addresses, or individual property details',
            'impact': 'Complete validation impossible',
            'recommendation': 'Re-run scraping with property-level data retention'
        })
        
        # Issue 2: Suspicious pattern consistency
        perfect_confidence_blocks = sum(1 for block in self.analysis_data['city_blocks'] 
                                      if block['confidence_score'] == 1.0)
        if perfect_confidence_blocks > len(self.analysis_data['city_blocks']) * 0.8:
            issues.append({
                'severity': 'HIGH',
                'issue': 'Unrealistic Confidence Scores',
                'description': f'{perfect_confidence_blocks} blocks with perfect 100% confidence',
                'impact': 'Suggests synthetic or overly processed data',
                'recommendation': 'Review confidence calculation methodology'
            })
        
        # Issue 3: Generic street names
        generic_street_blocks = sum(1 for block in self.analysis_data['city_blocks']
                                  if any('Street' in str(boundary) for boundary in block['street_boundaries']))
        if generic_street_blocks > 0:
            issues.append({
                'severity': 'HIGH', 
                'issue': 'Generic Street Names',
                'description': f'{generic_street_blocks} blocks with generic English street names',
                'impact': 'Indicates synthetic geographic data',
                'recommendation': 'Use actual Greek street names from xe.gr'
            })
        
        return issues
    
    def _create_excel_audit_report(self, audit_data: Dict):
        """Create detailed Excel audit report"""
        
        try:
            with pd.ExcelWriter('outputs/property_audit_report.xlsx', engine='openpyxl') as writer:
                
                # Summary sheet
                summary_data = {
                    'Metric': [
                        'Total Blocks Claimed',
                        'Total Properties Claimed', 
                        'Areas Analyzed',
                        'Individual Property URLs Available',
                        'Validation Possible',
                        'Critical Issues Count'
                    ],
                    'Value': [
                        audit_data['audit_metadata']['total_blocks_claimed'],
                        audit_data['audit_metadata']['total_properties_claimed'],
                        len(audit_data['audit_metadata']['areas_analyzed']),
                        'NO - Missing',
                        'NO - Insufficient Data',
                        len(audit_data['data_quality_flags'])
                    ]
                }
                
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # City block details
                block_details = []
                for block_audit in audit_data['city_block_summary_audit']:
                    block_details.append({
                        'Block ID': block_audit['block_id'],
                        'Properties': block_audit['claimed_properties'],
                        'Total SQM': block_audit['claimed_total_sqm'],
                        'Energy Class': block_audit['weighted_median_energy'],
                        'Price/SQM': block_audit['avg_price_per_sqm'],
                        'Validation Issues': '; '.join(block_audit['validation_issues']),
                        'Consistency Score': block_audit['data_consistency_score'],
                        'Suspicious Patterns': '; '.join(block_audit['suspicious_patterns'])
                    })
                
                pd.DataFrame(block_details).to_excel(writer, sheet_name='Block Details', index=False)
                
                # Data quality issues
                issues_data = []
                for issue in audit_data['data_quality_flags']:
                    issues_data.append({
                        'Severity': issue['severity'],
                        'Issue': issue['issue'],
                        'Description': issue['description'],
                        'Impact': issue['impact'],
                        'Recommendation': issue['recommendation']
                    })
                
                pd.DataFrame(issues_data).to_excel(writer, sheet_name='Quality Issues', index=False)
            
            print("✅ Excel audit report created: outputs/property_audit_report.xlsx")
            
        except ImportError:
            print("⚠️ Excel report creation requires openpyxl - creating CSV instead")
            pd.DataFrame(block_details).to_csv('outputs/block_audit_details.csv', index=False)

def main():
    """Generate property data audit report"""
    
    auditor = PropertyDataAuditReport()
    
    # Load analysis data
    if not auditor.load_analysis_data():
        return
    
    print("\n🔍 Generating Property Data Audit Report...")
    
    # Create audit report
    audit_report = auditor.create_comprehensive_audit_report()
    
    if audit_report:
        print(f"\n🚨 AUDIT RESULTS:")
        
        # Display critical issues
        if 'CRITICAL_VALIDATION_ISSUE' in audit_report:
            issue = audit_report['CRITICAL_VALIDATION_ISSUE']
            print(f"\n❌ CRITICAL ISSUE: {issue['issue']}")
            print(f"   Impact: {issue['impact']}")
            print(f"   Current Data: {issue['current_data']}")
            print(f"   Recommendation: {issue['recommendation']}")
        
        # Display data quality issues
        quality_issues = audit_report.get('data_quality_flags', [])
        print(f"\n🔍 Data Quality Issues Found: {len(quality_issues)}")
        for issue in quality_issues[:3]:  # Show top 3
            print(f"   • [{issue['severity']}] {issue['issue']}")
            print(f"     {issue['description']}")
        
        # Display what we CAN validate
        if 'city_block_summary_audit' in audit_report:
            print(f"\n📊 Block-Level Data Available:")
            for block in audit_report['city_block_summary_audit'][:3]:
                print(f"   • {block['block_id']}: {block['claimed_properties']} properties")
                print(f"     Energy: {block['weighted_median_energy']}, Price: €{block['avg_price_per_sqm']}/m²")
                if block['validation_issues']:
                    print(f"     Issues: {'; '.join(block['validation_issues'][:2])}")

if __name__ == "__main__":
    main()