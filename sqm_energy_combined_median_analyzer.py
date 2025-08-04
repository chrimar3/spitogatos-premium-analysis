#!/usr/bin/env python3
"""
SQM-ENERGY COMBINED MEDIAN ANALYZER
Calculate median energy class based on BOTH SQM and energy class combined
"""

import pandas as pd
import numpy as np
from collections import Counter
import json
from datetime import datetime

def energy_class_to_numeric(energy_class):
    """Convert energy class to numeric value"""
    energy_mapping = {
        'A+': 7, 'A': 6, 'B+': 5, 'B': 4, 'C+': 3, 'C': 2, 'D': 1, 'E': 0, 'F': -1, 'G': -2
    }
    return energy_mapping.get(energy_class, 0)

def numeric_to_energy_class(numeric_value):
    """Convert numeric value back to energy class"""
    numeric_mapping = {
        7: 'A+', 6: 'A', 5: 'B+', 4: 'B', 3: 'C+', 2: 'C', 1: 'D', 0: 'E', -1: 'F', -2: 'G'
    }
    rounded_value = round(numeric_value)
    return numeric_mapping.get(rounded_value, 'C')

def normalize_sqm(sqm, min_sqm, max_sqm):
    """Normalize SQM to 0-7 scale to match energy scale"""
    if max_sqm == min_sqm:
        return 3.5  # middle value if all same
    normalized = ((sqm - min_sqm) / (max_sqm - min_sqm)) * 7
    return normalized

def calculate_combined_score(sqm, energy_class, min_sqm, max_sqm, sqm_weight=0.3, energy_weight=0.7):
    """
    Calculate combined SQM-Energy score
    Default: Energy is weighted more heavily (70%) than size (30%)
    """
    energy_numeric = energy_class_to_numeric(energy_class)
    sqm_normalized = normalize_sqm(sqm, min_sqm, max_sqm)
    
    combined_score = (sqm_weight * sqm_normalized) + (energy_weight * energy_numeric)
    return combined_score

def analyze_sqm_energy_combined_median():
    """Analyze median energy class based on BOTH SQM and energy class"""
    
    print("🏘️🔋 SQM-ENERGY COMBINED MEDIAN ANALYSIS")
    print("="*100)
    print("📊 Calculating median energy class based on BOTH property size AND energy efficiency")
    print("="*100)
    
    # Load data
    csv_file = '/Users/chrism/spitogatos_premium_analysis/outputs/athens_city_blocks_comprehensive_analysis.csv'
    
    try:
        df = pd.read_csv(csv_file)
        
        # Clean and prepare data
        df = df.dropna(subset=['area', 'sqm', 'energy_class'])
        df['energy_numeric'] = df['energy_class'].apply(energy_class_to_numeric)
        
        print(f"📊 Total Properties Analyzed: {len(df)}")
        print(f"🏘️ Total Blocks: {df['area'].nunique()}")
        
        # Get global SQM range for normalization
        global_min_sqm = df['sqm'].min()
        global_max_sqm = df['sqm'].max()
        
        print(f"📐 Global SQM Range: {global_min_sqm}m² - {global_max_sqm}m²")
        print()
        
        # Calculate combined scores for each property
        df['combined_score'] = df.apply(lambda row: calculate_combined_score(
            row['sqm'], row['energy_class'], global_min_sqm, global_max_sqm
        ), axis=1)
        
        # Analyze each block
        all_blocks_analysis = {}
        
        for block_name in sorted(df['area'].unique()):
            block_data = df[df['area'] == block_name].copy()
            
            if len(block_data) < 3:
                continue
            
            # Calculate various medians
            median_sqm = block_data['sqm'].median()
            median_energy_numeric = block_data['energy_numeric'].median()
            median_energy_class = numeric_to_energy_class(median_energy_numeric)
            
            # NEW: Combined SQM-Energy median
            median_combined_score = block_data['combined_score'].median()
            combined_median_energy_class = numeric_to_energy_class(median_combined_score)
            
            # Sort properties by combined score
            block_data_sorted = block_data.sort_values('combined_score', ascending=False).reset_index(drop=True)
            
            # Create detailed property list with combined scores
            properties_detailed = []
            for idx, prop in block_data_sorted.iterrows():
                prop_info = {
                    'rank': idx + 1,
                    'property_id': prop['property_id'],
                    'url': prop['url'],
                    'title': prop.get('title', 'N/A'),
                    'sqm': prop['sqm'],
                    'energy_class': prop['energy_class'],
                    'energy_numeric': prop['energy_numeric'],
                    'combined_score': round(prop['combined_score'], 2),
                    'sqm_normalized': round(normalize_sqm(prop['sqm'], global_min_sqm, global_max_sqm), 2),
                    'property_type': prop.get('property_type', 'N/A'),
                    'listing_type': prop.get('listing_type', 'N/A'),
                    'price': prop.get('price', 0),
                    'price_per_sqm': prop.get('price_per_sqm', 0),
                    'rooms': prop.get('rooms', 'N/A'),
                    'floor': prop.get('floor', 'N/A')
                }
                properties_detailed.append(prop_info)
            
            all_blocks_analysis[block_name] = {
                'total_properties': len(block_data),
                'median_sqm': median_sqm,
                'median_energy_class_only': median_energy_class,
                'median_combined_score': round(median_combined_score, 2),
                'median_energy_class_combined': combined_median_energy_class,
                'sqm_range': f"{block_data['sqm'].min()}m² - {block_data['sqm'].max()}m²",
                'energy_distribution': dict(Counter(block_data['energy_class'])),
                'properties': properties_detailed,
                'best_combined': properties_detailed[0],
                'worst_combined': properties_detailed[-1]
            }
        
        # Sort blocks by combined median score
        sorted_blocks_combined = sorted(all_blocks_analysis.items(), 
                                      key=lambda x: x[1]['median_combined_score'], 
                                      reverse=True)
        
        # Display results
        print(f"🏆 BLOCKS RANKED BY COMBINED SQM-ENERGY MEDIAN")
        print("="*100)
        
        for rank, (block_name, block_info) in enumerate(sorted_blocks_combined, 1):
            print(f"\n🏘️ #{rank:02d}. {block_name.upper()}")
            print("-" * 80)
            print(f"   📊 Properties: {block_info['total_properties']}")
            print(f"   📐 Median SQM: {block_info['median_sqm']}m² | Range: {block_info['sqm_range']}")
            print(f"   🔋 Energy-Only Median: {block_info['median_energy_class_only']}")
            print(f"   ⚡ Combined SQM-Energy Median: {block_info['median_energy_class_combined']} (Score: {block_info['median_combined_score']})")
            print(f"   🏆 Best Combined: {block_info['best_combined']['property_id']} (Score: {block_info['best_combined']['combined_score']}, {block_info['best_combined']['sqm']}m², {block_info['best_combined']['energy_class']})")
            print(f"   📉 Worst Combined: {block_info['worst_combined']['property_id']} (Score: {block_info['worst_combined']['combined_score']}, {block_info['worst_combined']['sqm']}m², {block_info['worst_combined']['energy_class']})")
            
            # Show top 3 properties in each block
            print(f"   🏠 TOP 3 PROPERTIES (by combined SQM-Energy score):")
            for i, prop in enumerate(block_info['properties'][:3], 1):
                print(f"      {i}. {prop['property_id']}: {prop['sqm']}m², {prop['energy_class']} → Score: {prop['combined_score']}")
                print(f"         URL: {prop['url']}")
        
        # Comparison table
        print(f"\n📋 COMPARISON: ENERGY-ONLY vs COMBINED SQM-ENERGY MEDIANS")
        print("="*100)
        print(f"{'BLOCK':<20} {'PROPERTIES':<12} {'MEDIAN SQM':<12} {'ENERGY-ONLY':<13} {'COMBINED':<13} {'SCORE':<8}")
        print("-"*100)
        
        for block_name, block_info in sorted_blocks_combined:
            print(f"{block_name:<20} {block_info['total_properties']:<12} {block_info['median_sqm']:<12.1f}m² {block_info['median_energy_class_only']:<13} {block_info['median_energy_class_combined']:<13} {block_info['median_combined_score']:<8.2f}")
        
        # Methodology explanation
        print(f"\n📚 METHODOLOGY EXPLANATION")
        print("="*60)
        print("🔢 Combined Score Calculation:")
        print("   • SQM normalized to 0-7 scale (matching energy scale)")
        print("   • Energy class: A+ = 7, A = 6, B+ = 5, ..., F = -1")
        print("   • Combined Score = (30% × SQM_normalized) + (70% × Energy_numeric)")
        print("   • Higher scores = better combined SQM-Energy performance")
        print("   • Median taken from all combined scores in each block")
        
        print(f"\n💡 KEY INSIGHTS")
        print("-"*40)
        print("✅ Blocks where COMBINED median differs from energy-only median:")
        
        different_medians = []
        for block_name, block_info in sorted_blocks_combined:
            if block_info['median_energy_class_only'] != block_info['median_energy_class_combined']:
                different_medians.append((
                    block_name, 
                    block_info['median_energy_class_only'], 
                    block_info['median_energy_class_combined']
                ))
        
        if different_medians:
            for block, energy_only, combined in different_medians:
                print(f"   • {block}: Energy-only ({energy_only}) → Combined ({combined})")
        else:
            print("   • All blocks show same median for both methods")
        
        # Save results
        analysis_results = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'methodology': 'Combined SQM-Energy median calculation',
                'sqm_weight': 0.3,
                'energy_weight': 0.7,
                'total_properties': len(df),
                'total_blocks': len(sorted_blocks_combined),
                'global_sqm_range': f"{global_min_sqm}m² - {global_max_sqm}m²"
            },
            'blocks_analysis': dict(sorted_blocks_combined)
        }
        
        output_file = f'outputs/sqm_energy_combined_median_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Combined SQM-Energy analysis saved: {output_file}")
        print("="*100)
        
        return analysis_results
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find data file: {csv_file}")
        return None
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return None

if __name__ == "__main__":
    analyze_sqm_energy_combined_median()