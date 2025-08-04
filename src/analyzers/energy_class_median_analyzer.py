#!/usr/bin/env python3
"""
ENERGY CLASS MEDIAN ANALYZER
Calculate median energy class per Athens city block
"""

import pandas as pd
import numpy as np
from collections import Counter
import json
from datetime import datetime

def energy_class_to_numeric(energy_class):
    """Convert energy class to numeric value for median calculation"""
    energy_mapping = {
        'A+': 7,
        'A': 6,
        'B+': 5,
        'B': 4,
        'C+': 3,
        'C': 2,
        'D': 1,
        'E': 0,
        'F': -1,
        'G': -2
    }
    return energy_mapping.get(energy_class, 0)

def numeric_to_energy_class(numeric_value):
    """Convert numeric value back to energy class"""
    numeric_mapping = {
        7: 'A+',
        6: 'A',
        5: 'B+',
        4: 'B',
        3: 'C+',
        2: 'C',
        1: 'D',
        0: 'E',
        -1: 'F',
        -2: 'G'
    }
    # Round to nearest integer for median calculation
    rounded_value = round(numeric_value)
    return numeric_mapping.get(rounded_value, 'C')

def analyze_energy_class_medians():
    """Analyze median energy class per city block"""
    
    print("🔋 ATHENS CITY BLOCKS - ENERGY CLASS MEDIAN ANALYSIS")
    print("="*70)
    
    # Load the CSV data
    csv_file = '/Users/chrism/spitogatos_premium_analysis/outputs/athens_city_blocks_comprehensive_analysis.csv'
    
    try:
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded {len(df)} properties from CSV")
        
        # Group by area (city block)
        area_groups = df.groupby('area')
        
        results = {}
        detailed_analysis = {}
        
        print(f"\n🏘️ ANALYZING {len(area_groups)} CITY BLOCKS:")
        print("-" * 70)
        
        for area, group in area_groups:
            # Get all energy classes for this area
            energy_classes = group['energy_class'].dropna().tolist()
            
            if not energy_classes:
                print(f"⚠️ {area}: No energy class data")
                continue
            
            # Convert to numeric values
            numeric_values = [energy_class_to_numeric(ec) for ec in energy_classes]
            
            # Calculate median
            median_numeric = np.median(numeric_values)
            median_energy_class = numeric_to_energy_class(median_numeric)
            
            # Get distribution
            energy_distribution = Counter(energy_classes)
            
            # Store results
            results[area] = {
                'median_energy_class': median_energy_class,
                'median_numeric_value': median_numeric,
                'total_properties': len(energy_classes),
                'energy_distribution': dict(energy_distribution)
            }
            
            # Detailed analysis
            detailed_analysis[area] = {
                'properties': len(energy_classes),
                'median_energy_class': median_energy_class,
                'all_energy_classes': energy_classes,
                'distribution': energy_distribution
            }
            
            # Display results
            print(f"🏛️ {area}:")
            print(f"   📊 Properties: {len(energy_classes)}")
            print(f"   🔋 Median Energy Class: {median_energy_class}")
            print(f"   📈 Distribution: {dict(energy_distribution)}")
            print()
        
        # Sort by median energy class (best to worst)
        sorted_results = sorted(results.items(), 
                              key=lambda x: x[1]['median_numeric_value'], 
                              reverse=True)
        
        print("🏆 CITY BLOCKS RANKED BY MEDIAN ENERGY EFFICIENCY:")
        print("="*70)
        
        for i, (area, data) in enumerate(sorted_results, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            print(f"{medal} {area}: {data['median_energy_class']} "
                  f"({data['total_properties']} properties)")
        
        # Summary statistics
        all_medians = [data['median_numeric_value'] for data in results.values()]
        overall_median = np.median(all_medians)
        overall_median_class = numeric_to_energy_class(overall_median)
        
        print(f"\n📊 SUMMARY STATISTICS:")
        print("="*70)
        print(f"🔋 Overall Athens Median Energy Class: {overall_median_class}")
        print(f"🏘️ Total City Blocks Analyzed: {len(results)}")
        print(f"🏠 Total Properties Analyzed: {sum(data['total_properties'] for data in results.values())}")
        
        # Find best and worst performing blocks
        best_block = sorted_results[0]
        worst_block = sorted_results[-1]
        
        print(f"\n🏆 BEST PERFORMING BLOCK:")
        print(f"   🥇 {best_block[0]}: {best_block[1]['median_energy_class']}")
        
        print(f"\n⚠️ LOWEST PERFORMING BLOCK:")
        print(f"   📉 {worst_block[0]}: {worst_block[1]['median_energy_class']}")
        
        # Save detailed results to JSON
        output_file = f'outputs/energy_class_median_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        final_results = {
            'analysis_metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'total_city_blocks': len(results),
                'total_properties': sum(data['total_properties'] for data in results.values()),
                'overall_median_energy_class': overall_median_class,
                'overall_median_numeric': overall_median
            },
            'city_blocks_ranked': [
                {
                    'rank': i,
                    'area': area,
                    'median_energy_class': data['median_energy_class'],
                    'median_numeric_value': data['median_numeric_value'],
                    'total_properties': data['total_properties'],
                    'energy_distribution': data['energy_distribution']
                }
                for i, (area, data) in enumerate(sorted_results, 1)
            ],
            'detailed_analysis': detailed_analysis
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Detailed analysis saved: {output_file}")
        print("="*70)
        
        return results
        
    except Exception as e:
        print(f"❌ Error analyzing energy class medians: {e}")
        return None

if __name__ == "__main__":
    analyze_energy_class_medians()