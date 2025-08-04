#!/usr/bin/env python3
"""
COMPREHENSIVE BLOCK-BY-BLOCK PROPERTY ANALYZER
Detailed listing of every individual property in each Athens block with medians
"""

import pandas as pd
import numpy as np
from collections import Counter
import json
from datetime import datetime

def energy_class_to_numeric(energy_class):
    """Convert energy class to numeric value for median calculation"""
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

def analyze_all_blocks_comprehensive():
    """Comprehensive analysis of all properties in each block"""
    
    print("🏙️ COMPREHENSIVE ATHENS BLOCK-BY-BLOCK PROPERTY ANALYSIS")
    print("="*120)
    
    # Load data
    csv_file = '/Users/chrism/spitogatos_premium_analysis/outputs/athens_city_blocks_comprehensive_analysis.csv'
    
    try:
        df = pd.read_csv(csv_file)
        
        # Clean and prepare data
        df = df.dropna(subset=['area', 'sqm', 'energy_class'])
        df['energy_numeric'] = df['energy_class'].apply(energy_class_to_numeric)
        
        print(f"📊 Total Properties Analyzed: {len(df)}")
        print(f"🏘️ Total Blocks/Neighborhoods: {df['area'].nunique()}")
        print("="*120)
        
        # Group by area and analyze each block
        all_blocks_data = {}
        
        for block_name in sorted(df['area'].unique()):
            block_data = df[df['area'] == block_name].copy()
            
            # Skip blocks with too few properties
            if len(block_data) < 3:
                continue
            
            # Sort properties by energy efficiency, then by SQM
            block_data = block_data.sort_values(['energy_numeric', 'sqm'], ascending=[False, False])
            block_data = block_data.reset_index(drop=True)
            
            # Calculate statistics
            median_sqm = block_data['sqm'].median()
            median_energy_numeric = block_data['energy_numeric'].median()
            median_energy_class = numeric_to_energy_class(median_energy_numeric)
            
            # Create individual property list
            properties_list = []
            for idx, prop in block_data.iterrows():
                property_info = {
                    'rank': idx + 1,
                    'property_id': prop['property_id'],
                    'url': prop['url'],
                    'title': prop.get('title', 'N/A'),
                    'sqm': prop['sqm'],
                    'energy_class': prop['energy_class'],
                    'energy_numeric': prop['energy_numeric'],
                    'property_type': prop.get('property_type', 'N/A'),
                    'listing_type': prop.get('listing_type', 'N/A'),
                    'price': prop.get('price', 0),
                    'price_per_sqm': prop.get('price_per_sqm', 0),
                    'rooms': prop.get('rooms', 'N/A'),
                    'floor': prop.get('floor', 'N/A')
                }
                properties_list.append(property_info)
            
            # Store block data
            all_blocks_data[block_name] = {
                'total_properties': len(block_data),
                'median_sqm': median_sqm,
                'median_energy_class': median_energy_class,
                'median_energy_numeric': median_energy_numeric,
                'properties': properties_list,
                'energy_distribution': dict(Counter(block_data['energy_class'])),
                'sqm_range': f"{block_data['sqm'].min()}m² - {block_data['sqm'].max()}m²"
            }
        
        # Sort blocks by energy efficiency
        sorted_blocks = sorted(all_blocks_data.items(), 
                             key=lambda x: x[1]['median_energy_numeric'], 
                             reverse=True)
        
        # Display comprehensive analysis
        for block_rank, (block_name, block_info) in enumerate(sorted_blocks, 1):
            
            print(f"\n🏘️ BLOCK #{block_rank:02d}: {block_name.upper()}")
            print("="*120)
            print(f"📊 Total Properties: {block_info['total_properties']}")
            print(f"📐 Median SQM: {block_info['median_sqm']}m² | 🔋 Median Energy Class: {block_info['median_energy_class']}")
            print(f"📈 SQM Range: {block_info['sqm_range']}")
            print(f"🔋 Energy Distribution: {block_info['energy_distribution']}")
            print("-"*120)
            
            # List all individual properties
            print(f"🏠 INDIVIDUAL PROPERTIES IN {block_name.upper()}:")
            print("-"*120)
            
            for prop in block_info['properties']:
                print(f"   #{prop['rank']:02d}. {prop['property_id']}")
                print(f"       📋 Title: {prop['title']}")
                print(f"       🔗 URL: {prop['url']}")
                print(f"       📐 SQM: {prop['sqm']}m² | 🔋 Energy: {prop['energy_class']} ({prop['energy_numeric']}/7)")
                print(f"       🏢 Type: {prop['property_type'].title()} | 🏷️ Listing: {prop['listing_type'].title()}")
                print(f"       🚪 Rooms: {prop['rooms']} | 🏢 Floor: {prop['floor']}")
                
                if prop['price'] > 0:
                    if prop['listing_type'].lower() == 'rent':
                        print(f"       💰 Rent: €{prop['price']:,.0f}/month | 💵 €{prop['price_per_sqm']:.2f}/m²")
                    else:
                        print(f"       💰 Price: €{prop['price']:,.0f} | 💵 €{prop['price_per_sqm']:,.2f}/m²")
                
                print()
            
            print(f"📊 {block_name.upper()} SUMMARY:")
            print(f"   • Properties: {block_info['total_properties']}")
            print(f"   • Median SQM: {block_info['median_sqm']}m²")
            print(f"   • Median Energy Class: {block_info['median_energy_class']}")
            print(f"   • Best Property: {block_info['properties'][0]['property_id']} (Energy {block_info['properties'][0]['energy_class']}, {block_info['properties'][0]['sqm']}m²)")
            print(f"   • Energy Leaders: {sum(1 for p in block_info['properties'] if p['energy_numeric'] >= 5)} properties (B+ or better)")
            print("="*120)
        
        # Overall Athens summary
        print(f"\n🏛️ OVERALL ATHENS SUMMARY")
        print("="*80)
        
        total_properties = sum(block_info['total_properties'] for _, block_info in sorted_blocks)
        overall_median_sqm = df['sqm'].median()
        overall_median_energy = numeric_to_energy_class(df['energy_numeric'].median())
        
        print(f"📊 Total Properties Analyzed: {total_properties}")
        print(f"🏘️ Total Blocks: {len(sorted_blocks)}")
        print(f"📐 Overall Median SQM: {overall_median_sqm}m²")
        print(f"🔋 Overall Median Energy Class: {overall_median_energy}")
        
        print(f"\n🏆 TOP 3 ENERGY EFFICIENT BLOCKS:")
        for i, (block_name, block_info) in enumerate(sorted_blocks[:3], 1):
            print(f"   {i}. {block_name}: {block_info['median_energy_class']} (Median SQM: {block_info['median_sqm']}m²)")
        
        print(f"\n📉 BOTTOM 3 ENERGY PERFORMANCE BLOCKS:")
        for i, (block_name, block_info) in enumerate(sorted_blocks[-3:], 1):
            rank = len(sorted_blocks) - 3 + i
            print(f"   {rank}. {block_name}: {block_info['median_energy_class']} (Median SQM: {block_info['median_sqm']}m²)")
        
        # Block comparison table
        print(f"\n📋 QUICK REFERENCE TABLE:")
        print("-"*100)
        print(f"{'BLOCK':<20} {'PROPERTIES':<12} {'MEDIAN SQM':<12} {'MEDIAN ENERGY':<15} {'ENERGY RANGE':<20}")
        print("-"*100)
        
        for block_name, block_info in sorted_blocks:
            energy_classes = list(block_info['energy_distribution'].keys())
            energy_range = f"{min(energy_classes)} to {max(energy_classes)}"
            print(f"{block_name:<20} {block_info['total_properties']:<12} {block_info['median_sqm']:<12.1f}m² {block_info['median_energy_class']:<15} {energy_range:<20}")
        
        # Save comprehensive analysis
        analysis_results = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_properties': total_properties,
                'total_blocks': len(sorted_blocks),
                'overall_median_sqm': float(overall_median_sqm),
                'overall_median_energy_class': overall_median_energy
            },
            'blocks_detailed': dict(sorted_blocks)
        }
        
        output_file = f'outputs/comprehensive_block_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Comprehensive block analysis saved: {output_file}")
        print("="*120)
        
        return analysis_results
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find data file: {csv_file}")
        return None
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return None

if __name__ == "__main__":
    analyze_all_blocks_comprehensive()