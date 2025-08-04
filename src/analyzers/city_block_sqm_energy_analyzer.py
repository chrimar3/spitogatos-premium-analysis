#!/usr/bin/env python3
"""
CITY BLOCK SQM & ENERGY CLASS ANALYZER
Analyze median SQM and energy class per Athens city block/neighborhood
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
    rounded_value = round(numeric_value)
    return numeric_mapping.get(rounded_value, 'C')

def analyze_city_blocks():
    """Analyze SQM and energy class by city block/neighborhood"""
    
    print("🏘️ CITY BLOCK SQM & ENERGY CLASS ANALYSIS")
    print("="*80)
    
    # Load city blocks data
    csv_file = '/Users/chrism/spitogatos_premium_analysis/outputs/athens_city_blocks_comprehensive_analysis.csv'
    
    try:
        df = pd.read_csv(csv_file)
        print(f"📊 Analyzing {len(df)} properties across Athens city blocks")
        
        # Clean and prepare data
        df = df.dropna(subset=['area', 'sqm', 'energy_class'])
        df['energy_numeric'] = df['energy_class'].apply(energy_class_to_numeric)
        
        print(f"✅ Properties with complete data: {len(df)}")
        print(f"🏘️ City blocks/neighborhoods found: {df['area'].nunique()}")
        
        # Group by city block/area
        block_analysis = {}
        
        for area in sorted(df['area'].unique()):
            area_data = df[df['area'] == area]
            
            if len(area_data) < 3:  # Skip areas with too few properties
                continue
                
            # Calculate statistics
            median_sqm = area_data['sqm'].median()
            mean_sqm = area_data['sqm'].mean()
            median_energy_numeric = area_data['energy_numeric'].median()
            median_energy_class = numeric_to_energy_class(median_energy_numeric)
            
            # Energy class distribution
            energy_distribution = Counter(area_data['energy_class'])
            
            # Price analysis
            median_price_per_sqm = area_data['price_per_sqm'].median() if 'price_per_sqm' in area_data.columns else None
            
            # Property counts
            total_properties = len(area_data)
            
            # Best and worst properties
            best_property = area_data.loc[area_data['energy_numeric'].idxmax()]
            worst_property = area_data.loc[area_data['energy_numeric'].idxmin()]
            
            block_analysis[area] = {
                'total_properties': total_properties,
                'median_sqm': round(median_sqm, 1),
                'mean_sqm': round(mean_sqm, 1),
                'sqm_range': f"{area_data['sqm'].min()}m² - {area_data['sqm'].max()}m²",
                'median_energy_class': median_energy_class,
                'median_energy_numeric': median_energy_numeric,
                'energy_distribution': dict(energy_distribution),
                'median_price_per_sqm': round(median_price_per_sqm, 2) if median_price_per_sqm else None,
                'best_property': {
                    'property_id': best_property['property_id'],
                    'energy_class': best_property['energy_class'],
                    'sqm': best_property['sqm'],
                    'price_per_sqm': round(best_property['price_per_sqm'], 2) if 'price_per_sqm' in best_property else None
                },
                'worst_property': {
                    'property_id': worst_property['property_id'],
                    'energy_class': worst_property['energy_class'],
                    'sqm': worst_property['sqm'],
                    'price_per_sqm': round(worst_property['price_per_sqm'], 2) if 'price_per_sqm' in worst_property else None
                }
            }
        
        # Sort by median energy efficiency (best to worst)
        sorted_blocks = sorted(block_analysis.items(), 
                             key=lambda x: x[1]['median_energy_numeric'], 
                             reverse=True)
        
        print(f"\n🏆 CITY BLOCK ANALYSIS RESULTS")
        print("="*80)
        print(f"📊 Blocks analyzed: {len(sorted_blocks)}")
        print(f"🏘️ Total properties: {sum(block['total_properties'] for _, block in sorted_blocks)}")
        
        # Display results
        for rank, (area, data) in enumerate(sorted_blocks, 1):
            print(f"\n🏘️ #{rank}. {area.upper()}")
            print("-" * 60)
            print(f"   📊 Properties: {data['total_properties']}")
            print(f"   📐 Median SQM: {data['median_sqm']}m² (Range: {data['sqm_range']})")
            print(f"   🔋 Median Energy Class: {data['median_energy_class']}")
            if data['median_price_per_sqm']:
                print(f"   💰 Median Price/m²: €{data['median_price_per_sqm']:,}")
            print(f"   🏆 Best Property: {data['best_property']['property_id']} (Energy {data['best_property']['energy_class']}, {data['best_property']['sqm']}m²)")
            print(f"   📉 Worst Property: {data['worst_property']['property_id']} (Energy {data['worst_property']['energy_class']}, {data['worst_property']['sqm']}m²)")
            print(f"   📈 Energy Distribution: {data['energy_distribution']}")
        
        # Overall statistics
        print(f"\n📊 OVERALL STATISTICS")
        print("="*50)
        overall_median_sqm = df['sqm'].median()
        overall_median_energy = numeric_to_energy_class(df['energy_numeric'].median())
        
        print(f"🏠 Overall Median SQM: {overall_median_sqm}m²")
        print(f"🔋 Overall Median Energy Class: {overall_median_energy}")
        
        # Energy efficiency leaders and laggards
        print(f"\n🏆 ENERGY EFFICIENCY LEADERS:")
        print("-" * 40)
        for area, data in sorted_blocks[:3]:
            print(f"   {area}: {data['median_energy_class']} (Median SQM: {data['median_sqm']}m²)")
        
        print(f"\n📉 ENERGY EFFICIENCY CHALLENGES:")
        print("-" * 40)
        for area, data in sorted_blocks[-3:]:
            print(f"   {area}: {data['median_energy_class']} (Median SQM: {data['median_sqm']}m²)")
        
        # Size vs Energy correlation per block
        print(f"\n🔍 SIZE vs ENERGY INSIGHTS:")
        print("-" * 40)
        large_efficient = []
        small_efficient = []
        for area, data in sorted_blocks:
            if data['median_sqm'] > overall_median_sqm and data['median_energy_numeric'] >= 4:  # B or better
                large_efficient.append(area)
            elif data['median_sqm'] <= overall_median_sqm and data['median_energy_numeric'] >= 4:  # B or better
                small_efficient.append(area)
        
        if large_efficient:
            print(f"   🏢 Large & Efficient Blocks: {', '.join(large_efficient)}")
        if small_efficient:
            print(f"   🏠 Small & Efficient Blocks: {', '.join(small_efficient)}")
        
        # Save results
        analysis_results = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_properties': len(df),
                'blocks_analyzed': len(sorted_blocks),
                'overall_median_sqm': float(overall_median_sqm),
                'overall_median_energy_class': overall_median_energy
            },
            'block_analysis': dict(sorted_blocks)
        }
        
        output_file = f'outputs/city_block_sqm_energy_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 City block analysis saved: {output_file}")
        print("="*80)
        
        return analysis_results
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find city blocks data file: {csv_file}")
        return None
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return None

if __name__ == "__main__":
    analyze_city_blocks()