#!/usr/bin/env python3
"""
ENERGY CLASS VERIFICATION - Double Check Analysis
Verify median energy class calculations with detailed breakdown
"""

import pandas as pd
import numpy as np
from collections import Counter
import statistics

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

def verify_energy_class_analysis():
    """Verify and double-check energy class median calculations"""
    
    print("🔍 ENERGY CLASS ANALYSIS VERIFICATION")
    print("="*80)
    
    # Load the CSV data
    csv_file = '/Users/chrism/spitogatos_premium_analysis/outputs/athens_city_blocks_comprehensive_analysis.csv'
    
    try:
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded {len(df)} properties from CSV")
        
        # Check data quality first
        print(f"\n📋 DATA QUALITY CHECK:")
        print(f"   Total rows: {len(df)}")
        print(f"   Rows with energy class: {len(df.dropna(subset=['energy_class']))}")
        print(f"   Rows with area: {len(df.dropna(subset=['area']))}")
        print(f"   Unique areas: {df['area'].nunique()}")
        
        # Show all unique energy classes
        unique_energy_classes = df['energy_class'].dropna().unique()
        print(f"   Unique energy classes: {sorted(unique_energy_classes)}")
        
        # Group by area and verify calculations manually
        verification_results = {}
        
        print(f"\n🔍 DETAILED VERIFICATION BY CITY BLOCK:")
        print("="*80)
        
        for area in sorted(df['area'].unique()):
            if pd.isna(area):
                continue
                
            area_data = df[df['area'] == area]
            energy_classes = area_data['energy_class'].dropna().tolist()
            
            if not energy_classes:
                print(f"⚠️ {area}: No energy class data")
                continue
            
            print(f"\n🏛️ {area}:")
            print(f"   📊 Total Properties: {len(energy_classes)}")
            print(f"   🔋 Energy Classes: {energy_classes}")
            
            # Manual calculation step by step
            numeric_values = [energy_class_to_numeric(ec) for ec in energy_classes]
            print(f"   🔢 Numeric Values: {numeric_values}")
            
            # Calculate median using multiple methods
            median_numpy = np.median(numeric_values)
            median_statistics = statistics.median(numeric_values)
            
            print(f"   📈 Median (numpy): {median_numpy}")
            print(f"   📈 Median (statistics): {median_statistics}")
            
            # Convert back to energy class
            median_energy_class = numeric_to_energy_class(median_numpy)
            print(f"   🎯 Median Energy Class: {median_energy_class}")
            
            # Show distribution
            distribution = Counter(energy_classes)
            print(f"   📊 Distribution: {dict(distribution)}")
            
            # Manual verification for small sets
            if len(energy_classes) <= 5:
                sorted_classes = sorted(energy_classes, key=energy_class_to_numeric, reverse=True)
                print(f"   ✅ Sorted classes (best to worst): {sorted_classes}")
                if len(sorted_classes) % 2 == 1:
                    manual_median = sorted_classes[len(sorted_classes) // 2]
                else:
                    mid1 = sorted_classes[len(sorted_classes) // 2 - 1]
                    mid2 = sorted_classes[len(sorted_classes) // 2]
                    mid1_num = energy_class_to_numeric(mid1)
                    mid2_num = energy_class_to_numeric(mid2)
                    manual_median_num = (mid1_num + mid2_num) / 2
                    manual_median = numeric_to_energy_class(manual_median_num)
                print(f"   🔍 Manual median check: {manual_median}")
            
            verification_results[area] = {
                'properties': len(energy_classes),
                'energy_classes': energy_classes,
                'median_energy_class': median_energy_class,
                'median_numeric': median_numpy,
                'distribution': dict(distribution)
            }
        
        # Compare with previous results
        print(f"\n📊 COMPARISON WITH PREVIOUS ANALYSIS:")
        print("="*80)
        
        previous_rankings = [
            ('Κολωνάκι', 'A'),
            ('Πλάκα', 'B'),
            ('Κουκάκι', 'B'), 
            ('Παγκράτι', 'B'),
            ('Αμπελόκηποι', 'C+'),
            ('Ψυρρή', 'C+'),
            ('Μοναστηράκι', 'C'),
            ('Πετράλωνα', 'C'),
            ('Εξάρχεια', 'D'),
            ('Κυψέλη', 'D')
        ]
        
        print("Area | Previous | Verified | Match?")
        print("-" * 50)
        
        verification_matches = 0
        for area, previous_median in previous_rankings:
            if area in verification_results:
                verified_median = verification_results[area]['median_energy_class']
                match = "✅" if previous_median == verified_median else "❌"
                if previous_median == verified_median:
                    verification_matches += 1
                print(f"{area:<15} | {previous_median:<8} | {verified_median:<8} | {match}")
            else:
                print(f"{area:<15} | {previous_median:<8} | Missing  | ❌")
        
        print(f"\n🎯 Verification Score: {verification_matches}/{len(previous_rankings)} ({100*verification_matches/len(previous_rankings):.1f}%)")
        
        # Additional sanity checks
        print(f"\n🔍 SANITY CHECKS:")
        print("="*40)
        
        # Check if Kolonaki really has the best median
        kolonaki_data = verification_results.get('Κολωνάκι', {})
        if kolonaki_data:
            kolonaki_median_num = kolonaki_data['median_numeric']
            print(f"✅ Κολωνάκι median numeric: {kolonaki_median_num}")
            
            better_blocks = []
            for area, data in verification_results.items():
                if data['median_numeric'] > kolonaki_median_num:
                    better_blocks.append((area, data['median_energy_class'], data['median_numeric']))
            
            if better_blocks:
                print(f"⚠️ Blocks with better median than Κολωνάκι: {better_blocks}")
            else:
                print(f"✅ Κολωνάκι confirmed as best performing block")
        
        # Check if Kypseli and Exarchia really have the worst medians
        worst_blocks = []
        for area, data in verification_results.items():
            if data['median_energy_class'] in ['D', 'E', 'F']:
                worst_blocks.append((area, data['median_energy_class'], data['median_numeric']))
        
        worst_blocks.sort(key=lambda x: x[2])  # Sort by numeric value
        print(f"📉 Worst performing blocks: {worst_blocks}")
        
        # Final verification summary
        print(f"\n✅ VERIFICATION SUMMARY:")
        print("="*50)
        print(f"📊 Total properties verified: {sum(data['properties'] for data in verification_results.values())}")
        print(f"🏘️ Total city blocks verified: {len(verification_results)}")
        print(f"🎯 Accuracy of previous analysis: {100*verification_matches/len(previous_rankings):.1f}%")
        
        if verification_matches == len(previous_rankings):
            print("🎉 ALL CALCULATIONS VERIFIED CORRECTLY!")
        else:
            print("⚠️ Some discrepancies found - see details above")
        
        return verification_results
        
    except Exception as e:
        print(f"❌ Error in verification: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    verify_energy_class_analysis()