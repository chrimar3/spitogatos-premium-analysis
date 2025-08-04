#!/usr/bin/env python3
"""
KOLONAKI DETAILED PROPERTY ANALYZER
Comprehensive analysis of all individual properties in Kolonaki
"""

import pandas as pd
import numpy as np
from collections import Counter
import json
from datetime import datetime

def energy_class_to_numeric(energy_class):
    """Convert energy class to numeric value for analysis"""
    energy_mapping = {
        'A+': 7, 'A': 6, 'B+': 5, 'B': 4, 'C+': 3, 'C': 2, 'D': 1, 'E': 0, 'F': -1, 'G': -2
    }
    return energy_mapping.get(energy_class, 0)

def format_price(price):
    """Format price with proper currency and commas"""
    if pd.isna(price) or price == 0:
        return "N/A"
    return f"€{price:,.0f}"

def format_price_per_sqm(price_per_sqm):
    """Format price per sqm"""
    if pd.isna(price_per_sqm) or price_per_sqm == 0:
        return "N/A"
    return f"€{price_per_sqm:,.2f}/m²"

def analyze_kolonaki_properties():
    """Detailed analysis of all Kolonaki properties"""
    
    print("🏛️ KOLONAKI DETAILED PROPERTY ANALYSIS")
    print("="*100)
    
    # Load data
    csv_file = '/Users/chrism/spitogatos_premium_analysis/outputs/athens_city_blocks_comprehensive_analysis.csv'
    
    try:
        df = pd.read_csv(csv_file)
        
        # Filter for Kolonaki properties
        kolonaki_df = df[df['area'] == 'Κολωνάκι'].copy()
        
        print(f"📊 Total Kolonaki Properties Found: {len(kolonaki_df)}")
        print(f"🏛️ Premium Athens Neighborhood Analysis")
        print("="*100)
        
        if len(kolonaki_df) == 0:
            print("❌ No Kolonaki properties found in dataset")
            return None
        
        # Add energy numeric for sorting
        kolonaki_df['energy_numeric'] = kolonaki_df['energy_class'].apply(energy_class_to_numeric)
        
        # Sort by energy efficiency first, then by price per sqm
        kolonaki_df = kolonaki_df.sort_values(['energy_numeric', 'price_per_sqm'], ascending=[False, True])
        
        # Reset index for clean numbering
        kolonaki_df = kolonaki_df.reset_index(drop=True)
        
        # Display each property in detail
        print(f"\n🏠 INDIVIDUAL PROPERTY PROFILES")
        print("="*100)
        
        property_profiles = []
        
        for idx, property_data in kolonaki_df.iterrows():
            property_rank = idx + 1
            
            # Determine value category
            if property_data['energy_numeric'] >= 6:  # A or A+
                value_category = "🌟 PREMIUM ENERGY EFFICIENT"
            elif property_data['energy_numeric'] >= 4:  # B or B+
                value_category = "✅ GOOD ENERGY PERFORMANCE"
            elif property_data['energy_numeric'] >= 2:  # C or C+
                value_category = "⚠️ MODERATE ENERGY PERFORMANCE"
            else:
                value_category = "📉 ENERGY IMPROVEMENT NEEDED"
            
            # Price per sqm category
            price_per_sqm = property_data.get('price_per_sqm', 0)
            if price_per_sqm > 10000:
                price_category = "💎 ULTRA PREMIUM"
            elif price_per_sqm > 5000:
                price_category = "💰 PREMIUM"
            elif price_per_sqm > 3000:
                price_category = "💵 MODERATE"
            elif price_per_sqm > 1000:
                price_category = "💸 AFFORDABLE"
            else:
                price_category = "🔍 REQUIRES VERIFICATION"
            
            # Property profile
            profile = {
                'rank': property_rank,
                'property_id': property_data['property_id'],
                'url': property_data['url'],
                'title': property_data.get('title', 'N/A'),
                'property_type': property_data.get('property_type', 'N/A').title(),
                'listing_type': property_data.get('listing_type', 'N/A').title(),
                'sqm': property_data['sqm'],
                'energy_class': property_data['energy_class'],
                'energy_numeric': property_data['energy_numeric'],
                'rooms': property_data.get('rooms', 'N/A'),
                'floor': property_data.get('floor', 'N/A'),
                'price': property_data.get('price', 0),
                'price_per_sqm': price_per_sqm,
                'value_category': value_category,
                'price_category': price_category,
                'extraction_timestamp': property_data.get('extraction_timestamp', 'N/A')
            }
            
            property_profiles.append(profile)
            
            # Display property details
            print(f"\n🏠 PROPERTY #{property_rank:02d}: {profile['property_id']}")
            print("-" * 80)
            print(f"   📋 Title: {profile['title']}")
            print(f"   🔗 URL: {profile['url']}")
            print(f"   🏢 Type: {profile['property_type']} | 🏷️ Listing: {profile['listing_type']}")
            print(f"   📐 Size: {profile['sqm']}m² | 🚪 Rooms: {profile['rooms']} | 🏢 Floor: {profile['floor']}")
            print(f"   🔋 Energy Class: {profile['energy_class']} | ⭐ Energy Score: {profile['energy_numeric']}/7")
            print(f"   💰 Price: {format_price(profile['price'])}")
            print(f"   💵 Price/m²: {format_price_per_sqm(profile['price_per_sqm'])}")
            print(f"   🎯 Energy Category: {profile['value_category']}")
            print(f"   💎 Price Category: {profile['price_category']}")
            
            # Investment insight
            if profile['energy_numeric'] >= 6 and price_per_sqm < 5000:
                insight = "🚀 EXCELLENT INVESTMENT OPPORTUNITY - High efficiency, reasonable price"
            elif profile['energy_numeric'] >= 4 and price_per_sqm < 7000:
                insight = "✅ GOOD INVESTMENT POTENTIAL - Solid efficiency, fair pricing"
            elif profile['energy_numeric'] <= 3 and price_per_sqm > 8000:
                insight = "⚠️ OVERPRICED - Low efficiency for premium pricing"
            elif profile['sqm'] > 150 and profile['energy_numeric'] >= 5:
                insight = "🏛️ LUXURY OPTION - Large space with good efficiency"
            else:
                insight = "🔍 STANDARD MARKET OPTION - Evaluate based on specific needs"
            
            print(f"   💡 Investment Insight: {insight}")
        
        # Statistical Summary
        print(f"\n📊 KOLONAKI STATISTICAL SUMMARY")
        print("="*80)
        
        # Basic statistics
        total_properties = len(kolonaki_df)
        median_sqm = kolonaki_df['sqm'].median()
        mean_sqm = kolonaki_df['sqm'].mean()
        min_sqm = kolonaki_df['sqm'].min()
        max_sqm = kolonaki_df['sqm'].max()
        
        median_price_per_sqm = kolonaki_df['price_per_sqm'].median()
        mean_price_per_sqm = kolonaki_df['price_per_sqm'].mean()
        
        energy_distribution = Counter(kolonaki_df['energy_class'])
        property_type_distribution = Counter(kolonaki_df['property_type'])
        
        print(f"📈 Size Statistics:")
        print(f"   • Median SQM: {median_sqm}m² | Mean SQM: {mean_sqm:.1f}m²")
        print(f"   • Size Range: {min_sqm}m² - {max_sqm}m²")
        
        print(f"\n💰 Price Statistics:")
        print(f"   • Median Price/m²: {format_price_per_sqm(median_price_per_sqm)}")
        print(f"   • Mean Price/m²: {format_price_per_sqm(mean_price_per_sqm)}")
        
        print(f"\n🔋 Energy Efficiency Distribution:")
        for energy_class, count in sorted(energy_distribution.items(), key=lambda x: energy_class_to_numeric(x[0]), reverse=True):
            percentage = (count / total_properties) * 100
            print(f"   • {energy_class}: {count} properties ({percentage:.1f}%)")
        
        print(f"\n🏠 Property Type Distribution:")
        for prop_type, count in property_type_distribution.items():
            percentage = (count / total_properties) * 100
            print(f"   • {prop_type.title()}: {count} properties ({percentage:.1f}%)")
        
        # Top performers
        print(f"\n🏆 TOP PERFORMERS")
        print("-" * 50)
        
        # Best energy efficiency
        best_energy = kolonaki_df.iloc[0]
        print(f"🌟 Best Energy Efficiency: {best_energy['property_id']}")
        print(f"   Energy: {best_energy['energy_class']} | Size: {best_energy['sqm']}m² | Price/m²: {format_price_per_sqm(best_energy['price_per_sqm'])}")
        
        # Best value (good energy + reasonable price)
        value_properties = kolonaki_df[
            (kolonaki_df['energy_numeric'] >= 4) & 
            (kolonaki_df['price_per_sqm'] <= kolonaki_df['price_per_sqm'].median())
        ]
        
        if len(value_properties) > 0:
            best_value = value_properties.iloc[0]
            print(f"💎 Best Value: {best_value['property_id']}")
            print(f"   Energy: {best_value['energy_class']} | Size: {best_value['sqm']}m² | Price/m²: {format_price_per_sqm(best_value['price_per_sqm'])}")
        
        # Largest property
        largest = kolonaki_df.loc[kolonaki_df['sqm'].idxmax()]
        print(f"🏛️ Largest Property: {largest['property_id']}")
        print(f"   Energy: {largest['energy_class']} | Size: {largest['sqm']}m² | Price/m²: {format_price_per_sqm(largest['price_per_sqm'])}")
        
        # Investment recommendations
        print(f"\n💡 INVESTMENT RECOMMENDATIONS")
        print("-" * 50)
        
        premium_efficient = kolonaki_df[kolonaki_df['energy_numeric'] >= 6]
        affordable_good = kolonaki_df[
            (kolonaki_df['energy_numeric'] >= 4) & 
            (kolonaki_df['price_per_sqm'] <= median_price_per_sqm)
        ]
        
        print(f"🌟 Premium Energy Efficient Options: {len(premium_efficient)} properties")
        print(f"✅ Affordable Good Efficiency Options: {len(affordable_good)} properties")
        print(f"⚠️ Properties Needing Energy Upgrades: {len(kolonaki_df[kolonaki_df['energy_numeric'] <= 3])} properties")
        
        # Save detailed analysis
        analysis_results = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'neighborhood': 'Κολωνάκι',
                'total_properties': total_properties,
                'median_sqm': float(median_sqm),
                'median_price_per_sqm': float(median_price_per_sqm),
                'energy_distribution': dict(energy_distribution)
            },
            'property_profiles': property_profiles,
            'statistical_summary': {
                'size_stats': {
                    'median_sqm': float(median_sqm),
                    'mean_sqm': float(mean_sqm),
                    'min_sqm': float(min_sqm),
                    'max_sqm': float(max_sqm)
                },
                'price_stats': {
                    'median_price_per_sqm': float(median_price_per_sqm),
                    'mean_price_per_sqm': float(mean_price_per_sqm)
                },
                'distributions': {
                    'energy_classes': dict(energy_distribution),
                    'property_types': dict(property_type_distribution)
                }
            }
        }
        
        output_file = f'outputs/kolonaki_detailed_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed Kolonaki analysis saved: {output_file}")
        print("="*100)
        
        return analysis_results
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find data file: {csv_file}")
        return None
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return None

if __name__ == "__main__":
    analyze_kolonaki_properties()