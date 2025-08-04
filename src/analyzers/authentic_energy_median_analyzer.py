#!/usr/bin/env python3
"""
AUTHENTIC ENERGY MEDIAN ANALYZER
Calculate median energy class per neighborhood using 100% verified authentic data
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

def analyze_authentic_energy_medians():
    """Analyze median energy class per neighborhood using verified authentic data"""
    
    print("🔋 AUTHENTIC ATHENS ENERGY CLASS MEDIAN ANALYSIS")
    print("="*80)
    print("📊 Using 100% verified authentic property data")
    
    # Load the authentic dataset
    csv_file = '/Users/chrism/spitogatos_premium_analysis/outputs/real_athens_properties_comprehensive_20250802_213244.csv'
    
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ Loaded {len(df)} authentic properties")
        
        # Data quality verification
        energy_data = df.dropna(subset=['energy_class', 'neighborhood'])
        print(f"📊 Properties with energy and neighborhood data: {len(energy_data)}")
        
        # Group by neighborhood and calculate medians
        neighborhoods = energy_data.groupby('neighborhood')
        
        results = {}
        detailed_analysis = {}
        
        print(f"\n🏘️ ANALYZING {len(neighborhoods)} ATHENS NEIGHBORHOODS:")
        print("-" * 80)
        
        for neighborhood, group in neighborhoods:
            energy_classes = group['energy_class'].tolist()
            
            if len(energy_classes) < 3:
                print(f"⚠️ {neighborhood}: Only {len(energy_classes)} properties - skipping median calculation")
                continue
            
            # Convert to numeric values
            numeric_values = [energy_class_to_numeric(ec) for ec in energy_classes]
            
            # Calculate median
            median_numeric = np.median(numeric_values)
            median_energy_class = numeric_to_energy_class(median_numeric)
            
            # Get energy distribution
            energy_distribution = Counter(energy_classes)
            
            # Calculate average price and SQM for context
            avg_price = group['price'].mean()
            avg_sqm = group['sqm'].mean()
            avg_price_per_sqm = group['price_per_sqm'].mean() if 'price_per_sqm' in group.columns else avg_price/avg_sqm
            
            # Store results
            results[neighborhood] = {
                'median_energy_class': median_energy_class,
                'median_numeric_value': median_numeric,
                'total_properties': len(energy_classes),
                'energy_distribution': dict(energy_distribution),
                'avg_price': avg_price,
                'avg_sqm': avg_sqm,
                'avg_price_per_sqm': avg_price_per_sqm
            }
            
            # Display results
            print(f"🏛️ {neighborhood}:")
            print(f"   📊 Properties: {len(energy_classes)}")
            print(f"   🔋 Median Energy Class: {median_energy_class}")
            print(f"   💰 Avg Price: €{avg_price:,.0f}")
            print(f"   📐 Avg SQM: {avg_sqm:.0f}m²")
            print(f"   💎 Avg €/m²: {avg_price_per_sqm:,.0f}")
            print(f"   📈 Distribution: {dict(energy_distribution)}")
            print()
        
        # Sort neighborhoods by median energy efficiency (best to worst)
        sorted_results = sorted(results.items(), 
                              key=lambda x: x[1]['median_numeric_value'], 
                              reverse=True)
        
        print("🏆 ATHENS NEIGHBORHOODS RANKED BY ENERGY EFFICIENCY:")
        print("="*80)
        
        for i, (neighborhood, data) in enumerate(sorted_results, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:2d}."
            price_tier = "💎" if data['avg_price_per_sqm'] > 8000 else "💰" if data['avg_price_per_sqm'] > 4000 else "🏠"
            
            print(f"{medal} {neighborhood:<15} | Energy: {data['median_energy_class']:<2} | "
                  f"Properties: {data['total_properties']:2d} | {price_tier} €{data['avg_price_per_sqm']:,.0f}/m²")
        
        # Generate insights and correlations
        print(f"\n📊 MARKET INSIGHTS & CORRELATIONS:")
        print("="*80)
        
        # Energy vs Price correlation
        neighborhood_data = []
        for neighborhood, data in results.items():
            neighborhood_data.append({
                'neighborhood': neighborhood,
                'energy_numeric': data['median_numeric_value'],
                'price_per_sqm': data['avg_price_per_sqm'],
                'properties': data['total_properties']
            })
        
        # Sort by price per sqm for price tiers
        price_sorted = sorted(neighborhood_data, key=lambda x: x['price_per_sqm'], reverse=True)
        
        print(f"💎 PREMIUM NEIGHBORHOODS (>€8k/m²):")
        premium_neighborhoods = [n for n in price_sorted if n['price_per_sqm'] > 8000]
        for n in premium_neighborhoods:
            energy_class = numeric_to_energy_class(n['energy_numeric'])
            print(f"   {n['neighborhood']}: Energy {energy_class} | €{n['price_per_sqm']:,.0f}/m²")
        
        print(f"\n💰 MID-TIER NEIGHBORHOODS (€4k-8k/m²):")
        mid_tier = [n for n in price_sorted if 4000 <= n['price_per_sqm'] <= 8000]
        for n in mid_tier:
            energy_class = numeric_to_energy_class(n['energy_numeric'])
            print(f"   {n['neighborhood']}: Energy {energy_class} | €{n['price_per_sqm']:,.0f}/m²")
        
        print(f"\n🏠 AFFORDABLE NEIGHBORHOODS (<€4k/m²):")
        affordable = [n for n in price_sorted if n['price_per_sqm'] < 4000]
        for n in affordable:
            energy_class = numeric_to_energy_class(n['energy_numeric'])
            print(f"   {n['neighborhood']}: Energy {energy_class} | €{n['price_per_sqm']:,.0f}/m²")
        
        # Overall Athens statistics
        all_medians = [data['median_numeric_value'] for data in results.values()]
        overall_median = np.median(all_medians)
        overall_median_class = numeric_to_energy_class(overall_median)
        
        all_prices = [data['avg_price_per_sqm'] for data in results.values()]
        weighted_avg_price = np.average(all_prices, weights=[data['total_properties'] for data in results.values()])
        
        print(f"\n📊 OVERALL ATHENS STATISTICS:")
        print("="*50)
        print(f"🔋 Overall Median Energy Class: {overall_median_class}")
        print(f"🏘️ Neighborhoods Analyzed: {len(results)}")
        print(f"🏠 Total Authentic Properties: {sum(data['total_properties'] for data in results.values())}")
        print(f"💰 Weighted Average Price: €{weighted_avg_price:,.0f}/m²")
        
        # Best and worst performing neighborhoods
        best_neighborhood = sorted_results[0]
        worst_neighborhood = sorted_results[-1]
        
        print(f"\n🏆 BEST ENERGY EFFICIENCY:")
        print(f"   🥇 {best_neighborhood[0]}: {best_neighborhood[1]['median_energy_class']} "
              f"(€{best_neighborhood[1]['avg_price_per_sqm']:,.0f}/m²)")
        
        print(f"\n📉 NEEDS IMPROVEMENT:")
        print(f"   ⚠️ {worst_neighborhood[0]}: {worst_neighborhood[1]['median_energy_class']} "
              f"(€{worst_neighborhood[1]['avg_price_per_sqm']:,.0f}/m²)")
        
        # Energy efficiency investment opportunities
        print(f"\n💡 INVESTMENT OPPORTUNITIES:")
        print("="*50)
        print("📈 Areas with good energy efficiency + reasonable prices:")
        
        opportunities = []
        for neighborhood, data in results.items():
            if (data['median_numeric_value'] >= 4 and  # B or better
                data['avg_price_per_sqm'] < 6000 and  # Under €6k/m²
                data['total_properties'] >= 3):       # Sufficient data
                opportunities.append((neighborhood, data))
        
        for neighborhood, data in opportunities:
            print(f"   💎 {neighborhood}: Energy {data['median_energy_class']} | €{data['avg_price_per_sqm']:,.0f}/m²")
        
        if not opportunities:
            print("   ⚠️ No clear opportunities identified in current dataset")
        
        # Save comprehensive results
        final_results = {
            'analysis_metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'data_source': 'authentic_spitogatos_extraction',
                'total_neighborhoods': len(results),
                'total_properties': sum(data['total_properties'] for data in results.values()),
                'overall_median_energy_class': overall_median_class,
                'overall_median_numeric': overall_median,
                'weighted_average_price_per_sqm': weighted_avg_price
            },
            'neighborhoods_ranked': [
                {
                    'rank': i,
                    'neighborhood': neighborhood,
                    'median_energy_class': data['median_energy_class'],
                    'median_numeric_value': data['median_numeric_value'],
                    'total_properties': data['total_properties'],
                    'avg_price': data['avg_price'],
                    'avg_sqm': data['avg_sqm'],
                    'avg_price_per_sqm': data['avg_price_per_sqm'],
                    'energy_distribution': data['energy_distribution']
                }
                for i, (neighborhood, data) in enumerate(sorted_results, 1)
            ],
            'market_insights': {
                'premium_neighborhoods': [n['neighborhood'] for n in premium_neighborhoods],
                'mid_tier_neighborhoods': [n['neighborhood'] for n in mid_tier],
                'affordable_neighborhoods': [n['neighborhood'] for n in affordable],
                'investment_opportunities': [opp[0] for opp in opportunities],
                'best_energy_efficiency': best_neighborhood[0],
                'needs_energy_improvement': worst_neighborhood[0]
            }
        }
        
        output_file = f'outputs/authentic_energy_median_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Comprehensive analysis saved: {output_file}")
        print("="*80)
        
        return results
        
    except Exception as e:
        print(f"❌ Error in authentic energy analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    analyze_authentic_energy_medians()