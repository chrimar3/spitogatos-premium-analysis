#!/usr/bin/env python3
"""
SQM-ENERGY CORRELATION ANALYZER
Calculate median energy class based on property size (SQM) and energy class correlation
"""

import pandas as pd
import numpy as np
from collections import Counter
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

def energy_class_to_numeric(energy_class):
    """Convert energy class to numeric value for analysis"""
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

def categorize_by_sqm(sqm):
    """Categorize properties by size"""
    if sqm <= 80:
        return "Small (≤80m²)"
    elif sqm <= 150:
        return "Medium (81-150m²)"
    elif sqm <= 200:
        return "Large (151-200m²)"
    else:
        return "Extra Large (>200m²)"

def analyze_sqm_energy_correlation():
    """Analyze correlation between property size (SQM) and energy efficiency"""
    
    print("🔋📐 SQM-ENERGY CORRELATION ANALYSIS")
    print("="*80)
    print("📊 Analyzing relationship between property size and energy efficiency")
    
    # Load the authentic dataset
    csv_file = '/Users/chrism/spitogatos_premium_analysis/outputs/real_athens_properties_comprehensive_20250802_213244.csv'
    
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ Loaded {len(df)} authentic properties")
        
        # Data quality verification
        clean_data = df.dropna(subset=['sqm', 'energy_class', 'price']).copy()
        print(f"📊 Properties with complete SQM and energy data: {len(clean_data)}")
        
        # Add numeric energy values
        clean_data['energy_numeric'] = clean_data['energy_class'].apply(energy_class_to_numeric)
        
        # Add SQM categories
        clean_data['sqm_category'] = clean_data['sqm'].apply(categorize_by_sqm)
        
        # Calculate price per SQM if not present
        if 'price_per_sqm' not in clean_data.columns:
            clean_data['price_per_sqm'] = clean_data['price'] / clean_data['sqm']
        
        # Overall statistics
        print(f"\\n📊 OVERALL DATASET STATISTICS:")
        print("-" * 50)
        print(f"SQM Range: {clean_data['sqm'].min():.0f}m² - {clean_data['sqm'].max():.0f}m²")
        print(f"Median SQM: {clean_data['sqm'].median():.0f}m²")
        print(f"Overall Median Energy Class: {numeric_to_energy_class(clean_data['energy_numeric'].median())}")
        print(f"Average Price/m²: €{clean_data['price_per_sqm'].mean():,.0f}")
        
        # Analysis by SQM categories
        sqm_analysis = {}
        
        print(f"\\n🏠 ANALYSIS BY PROPERTY SIZE CATEGORIES:")
        print("="*80)
        
        for category in ["Small (≤80m²)", "Medium (81-150m²)", "Large (151-200m²)", "Extra Large (>200m²)"]:
            category_data = clean_data[clean_data['sqm_category'] == category]
            
            if len(category_data) == 0:
                continue
                
            # Calculate statistics
            median_energy_numeric = category_data['energy_numeric'].median()
            median_energy_class = numeric_to_energy_class(median_energy_numeric)
            median_sqm = category_data['sqm'].median()
            avg_price_per_sqm = category_data['price_per_sqm'].mean()
            
            # Energy distribution
            energy_distribution = Counter(category_data['energy_class'])
            
            # Best and worst properties in category
            best_property = category_data.loc[category_data['energy_numeric'].idxmax()]
            worst_property = category_data.loc[category_data['energy_numeric'].idxmin()]
            
            # Store results
            sqm_analysis[category] = {
                'count': len(category_data),
                'median_energy_class': median_energy_class,
                'median_energy_numeric': median_energy_numeric,
                'median_sqm': median_sqm,
                'sqm_range': f"{category_data['sqm'].min():.0f}m² - {category_data['sqm'].max():.0f}m²",
                'avg_price_per_sqm': avg_price_per_sqm,
                'energy_distribution': dict(energy_distribution),
                'best_property': {
                    'property_id': best_property['property_id'],
                    'energy_class': best_property['energy_class'],
                    'sqm': best_property['sqm'],
                    'price_per_sqm': best_property['price_per_sqm'],
                    'neighborhood': best_property['neighborhood']
                },
                'worst_property': {
                    'property_id': worst_property['property_id'],
                    'energy_class': worst_property['energy_class'],
                    'sqm': worst_property['sqm'],
                    'price_per_sqm': worst_property['price_per_sqm'],
                    'neighborhood': worst_property['neighborhood']
                }
            }
            
            # Display results
            print(f"\\n🏘️ {category}:")
            print(f"   📊 Properties: {len(category_data)}")
            print(f"   📐 SQM Range: {category_data['sqm'].min():.0f}m² - {category_data['sqm'].max():.0f}m²")
            print(f"   📐 Median SQM: {median_sqm:.0f}m²")
            print(f"   🔋 Median Energy Class: {median_energy_class}")
            print(f"   💰 Avg Price/m²: €{avg_price_per_sqm:,.0f}")
            print(f"   🏆 Best Property: {best_property['property_id']} (Energy {best_property['energy_class']}, {best_property['sqm']:.0f}m², €{best_property['price_per_sqm']:,.0f}/m²)")
            print(f"   📉 Worst Property: {worst_property['property_id']} (Energy {worst_property['energy_class']}, {worst_property['sqm']:.0f}m², €{worst_property['price_per_sqm']:,.0f}/m²)")
            print(f"   📈 Energy Distribution: {dict(energy_distribution)}")
        
        # Correlation analysis
        print(f"\\n📊 CORRELATION ANALYSIS:")
        print("="*50)
        
        # Calculate correlation between SQM and energy efficiency
        sqm_energy_corr = clean_data['sqm'].corr(clean_data['energy_numeric'])
        sqm_price_corr = clean_data['sqm'].corr(clean_data['price_per_sqm'])
        energy_price_corr = clean_data['energy_numeric'].corr(clean_data['price_per_sqm'])
        
        print(f"🔗 SQM ↔ Energy Efficiency Correlation: {sqm_energy_corr:.3f}")
        print(f"🔗 SQM ↔ Price/m² Correlation: {sqm_price_corr:.3f}")
        print(f"🔗 Energy Efficiency ↔ Price/m² Correlation: {energy_price_corr:.3f}")
        
        # Interpret correlations
        def interpret_correlation(corr, var1, var2):
            if abs(corr) < 0.1:
                return f"No meaningful correlation between {var1} and {var2}"
            elif abs(corr) < 0.3:
                return f"Weak {'positive' if corr > 0 else 'negative'} correlation between {var1} and {var2}"
            elif abs(corr) < 0.7:
                return f"Moderate {'positive' if corr > 0 else 'negative'} correlation between {var1} and {var2}"
            else:
                return f"Strong {'positive' if corr > 0 else 'negative'} correlation between {var1} and {var2}"
        
        print(f"\\n📊 CORRELATION INTERPRETATION:")
        print("-" * 50)
        print(f"🔍 {interpret_correlation(sqm_energy_corr, 'Property Size', 'Energy Efficiency')}")
        print(f"🔍 {interpret_correlation(sqm_price_corr, 'Property Size', 'Price per m²')}")
        print(f"🔍 {interpret_correlation(energy_price_corr, 'Energy Efficiency', 'Price per m²')}")
        
        # Key insights
        print(f"\\n💡 KEY INSIGHTS:")
        print("="*50)
        
        # Check if all categories have same median energy class
        median_classes = [data['median_energy_class'] for data in sqm_analysis.values()]
        if len(set(median_classes)) == 1:
            print(f"🔋 All size categories show median {median_classes[0]} energy performance")
            print(f"📊 Property size does NOT significantly impact energy efficiency")
        
        # Price variation by size
        price_ranges = [(cat, data['avg_price_per_sqm']) for cat, data in sqm_analysis.items()]
        price_ranges.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\\n💰 PRICE VARIATION BY SIZE:")
        for category, avg_price in price_ranges:
            print(f"   {category}: €{avg_price:,.0f}/m²")
        
        if price_ranges[0][1] > price_ranges[-1][1] * 1.5:
            print(f"💡 Smaller properties command significant price premium")
        
        # Investment recommendations by size
        print(f"\\n🎯 INVESTMENT RECOMMENDATIONS BY SIZE:")
        print("="*50)
        
        for category, data in sqm_analysis.items():
            energy_variety = len(data['energy_distribution'])
            best_energy = data['best_property']['energy_class']
            avg_price = data['avg_price_per_sqm']
            
            print(f"\\n🏠 {category}:")
            if energy_variety >= 6:
                print(f"   ⚠️ High energy variability - careful property selection needed")
            print(f"   🎯 Target: {best_energy} class or better for premium positioning")
            print(f"   💰 Budget: €{avg_price:,.0f}/m² average")
            print(f"   🏆 Best Example: {data['best_property']['property_id']} in {data['best_property']['neighborhood']}")
        
        # Save comprehensive analysis
        analysis_results = {
            'analysis_metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'total_properties': len(clean_data),
                'sqm_range': f"{clean_data['sqm'].min():.0f}m² - {clean_data['sqm'].max():.0f}m²",
                'overall_median_energy': numeric_to_energy_class(clean_data['energy_numeric'].median()),
                'correlations': {
                    'sqm_energy': sqm_energy_corr,
                    'sqm_price': sqm_price_corr,
                    'energy_price': energy_price_corr
                }
            },
            'size_categories': sqm_analysis,
            'key_insights': {
                'size_energy_independence': len(set(median_classes)) == 1,
                'price_premium_factor': price_ranges[0][1] / price_ranges[-1][1] if len(price_ranges) > 1 else 1,
                'energy_efficiency_driver': 'building_quality_not_size' if abs(sqm_energy_corr) < 0.2 else 'size_dependent'
            }
        }
        
        output_file = f'outputs/sqm_energy_correlation_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\\n💾 SQM-Energy correlation analysis saved: {output_file}")
        print("="*80)
        
        return analysis_results
        
    except Exception as e:
        print(f"❌ Error in SQM-Energy correlation analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    analyze_sqm_energy_correlation()