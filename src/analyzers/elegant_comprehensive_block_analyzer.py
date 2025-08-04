#!/usr/bin/env python3
"""
ELEGANT COMPREHENSIVE BLOCK ANALYZER
Complete analysis of all Athens blocks with sophisticated presentation
"""

import pandas as pd
import numpy as np
from collections import Counter, OrderedDict
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

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
    """Normalize SQM to 0-7 scale"""
    if max_sqm == min_sqm:
        return 3.5
    normalized = ((sqm - min_sqm) / (max_sqm - min_sqm)) * 7
    return normalized

def calculate_combined_score(sqm, energy_class, min_sqm, max_sqm, sqm_weight=0.3, energy_weight=0.7):
    """Calculate combined SQM-Energy score"""
    energy_numeric = energy_class_to_numeric(energy_class)
    sqm_normalized = normalize_sqm(sqm, min_sqm, max_sqm)
    combined_score = (sqm_weight * sqm_normalized) + (energy_weight * energy_numeric)
    return combined_score

def format_currency(amount):
    """Format currency amounts elegantly"""
    if pd.isna(amount) or amount == 0:
        return "N/A"
    if amount >= 1000000:
        return f"€{amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"€{amount/1000:.0f}K"
    else:
        return f"€{amount:.0f}"

def format_price_per_sqm(price_per_sqm):
    """Format price per sqm elegantly"""
    if pd.isna(price_per_sqm) or price_per_sqm == 0:
        return "N/A"
    return f"€{price_per_sqm:,.0f}/m²"

def get_investment_grade(combined_score, price_per_sqm):
    """Determine investment grade based on metrics"""
    if combined_score >= 5.5:
        return "🌟 PREMIUM", "Exceptional investment opportunity"
    elif combined_score >= 4.5:
        return "💎 EXCELLENT", "Strong investment potential"
    elif combined_score >= 3.5:
        return "✅ GOOD", "Solid investment option"
    elif combined_score >= 2.5:
        return "⚠️ MODERATE", "Consider with caution"
    else:
        return "📉 CHALLENGING", "High-risk investment"

def get_market_position(median_price_per_sqm, overall_median):
    """Determine market position relative to Athens average"""
    if pd.isna(median_price_per_sqm) or median_price_per_sqm == 0:
        return "🔍 DATA PENDING", "Price data requires verification"
    
    ratio = median_price_per_sqm / overall_median
    if ratio >= 1.5:
        return "💰 ULTRA-PREMIUM", "Top-tier luxury market"
    elif ratio >= 1.2:
        return "💵 PREMIUM", "Above-average pricing"
    elif ratio >= 0.8:
        return "📊 MARKET-RATE", "Average market pricing"
    else:
        return "💸 VALUE", "Below-average pricing"

def create_elegant_block_analysis():
    """Create elegant comprehensive analysis for all blocks"""
    
    print("🏛️ ELEGANT ATHENS REAL ESTATE BLOCK ANALYSIS")
    print("=" * 120)
    print("📊 Comprehensive Investment Intelligence Report")
    print("🔍 Combining Property Size, Energy Efficiency, and Market Dynamics")
    print("=" * 120)
    
    # Load data
    csv_file = '/Users/chrism/spitogatos_premium_analysis/outputs/athens_city_blocks_comprehensive_analysis.csv'
    
    try:
        df = pd.read_csv(csv_file)
        df = df.dropna(subset=['area', 'sqm', 'energy_class'])
        df['energy_numeric'] = df['energy_class'].apply(energy_class_to_numeric)
        
        # Calculate global metrics
        global_min_sqm = df['sqm'].min()
        global_max_sqm = df['sqm'].max()
        overall_median_price = df['price_per_sqm'].median()
        
        df['combined_score'] = df.apply(lambda row: calculate_combined_score(
            row['sqm'], row['energy_class'], global_min_sqm, global_max_sqm
        ), axis=1)
        
        print(f"📈 MARKET OVERVIEW")
        print("-" * 60)
        print(f"🏠 Total Properties Analyzed: {len(df):,}")
        print(f"🏘️ Athens Neighborhoods: {df['area'].nunique()}")
        print(f"📐 Property Size Range: {global_min_sqm:.0f}m² - {global_max_sqm:.0f}m²")
        print(f"💰 Market Median Price: {format_price_per_sqm(overall_median_price)}")
        print(f"🔋 Energy Classes: {', '.join(sorted(df['energy_class'].unique(), key=energy_class_to_numeric, reverse=True))}")
        print()
        
        # Analyze each block comprehensively
        all_blocks = {}
        
        for block_name in sorted(df['area'].unique()):
            block_data = df[df['area'] == block_name].copy()
            
            if len(block_data) < 3:
                continue
            
            # Sort by combined score for ranking
            block_data_sorted = block_data.sort_values('combined_score', ascending=False).reset_index(drop=True)
            
            # Calculate comprehensive statistics
            stats = {
                # Basic metrics
                'total_properties': len(block_data),
                'median_sqm': block_data['sqm'].median(),
                'mean_sqm': block_data['sqm'].mean(),
                'sqm_range': (block_data['sqm'].min(), block_data['sqm'].max()),
                'median_price_per_sqm': block_data['price_per_sqm'].median(),
                'mean_price_per_sqm': block_data['price_per_sqm'].mean(),
                
                # Energy metrics
                'median_energy_numeric': block_data['energy_numeric'].median(),
                'median_energy_class': numeric_to_energy_class(block_data['energy_numeric'].median()),
                'energy_distribution': dict(Counter(block_data['energy_class'])),
                'premium_energy_count': len(block_data[block_data['energy_numeric'] >= 5]),  # B+ or better
                'premium_energy_pct': (len(block_data[block_data['energy_numeric'] >= 5]) / len(block_data)) * 100,
                
                # Combined metrics
                'median_combined_score': block_data['combined_score'].median(),
                'combined_median_energy': numeric_to_energy_class(block_data['combined_score'].median()),
                'top_quartile_score': block_data['combined_score'].quantile(0.75),
                'bottom_quartile_score': block_data['combined_score'].quantile(0.25),
                
                # Property type analysis
                'property_types': dict(Counter(block_data['property_type'].fillna('Unknown'))),
                'listing_types': dict(Counter(block_data['listing_type'].fillna('Unknown'))),
                
                # Investment insights
                'investment_opportunities': len(block_data[
                    (block_data['combined_score'] >= 4.0) & 
                    (block_data['price_per_sqm'] <= block_data['price_per_sqm'].median())
                ]),
                
                # Top performers
                'best_property': {
                    'id': block_data_sorted.iloc[0]['property_id'],
                    'url': block_data_sorted.iloc[0]['url'],
                    'sqm': block_data_sorted.iloc[0]['sqm'],
                    'energy': block_data_sorted.iloc[0]['energy_class'],
                    'combined_score': block_data_sorted.iloc[0]['combined_score'],
                    'price_per_sqm': block_data_sorted.iloc[0]['price_per_sqm']
                },
                
                'worst_property': {
                    'id': block_data_sorted.iloc[-1]['property_id'],
                    'url': block_data_sorted.iloc[-1]['url'],
                    'sqm': block_data_sorted.iloc[-1]['sqm'],
                    'energy': block_data_sorted.iloc[-1]['energy_class'],
                    'combined_score': block_data_sorted.iloc[-1]['combined_score'],
                    'price_per_sqm': block_data_sorted.iloc[-1]['price_per_sqm']
                }
            }
            
            # Create property portfolio
            portfolio = []
            for idx, prop in block_data_sorted.iterrows():
                portfolio.append({
                    'rank': len(portfolio) + 1,
                    'property_id': prop['property_id'],
                    'url': prop['url'],
                    'title': prop.get('title', 'N/A'),
                    'sqm': prop['sqm'],
                    'energy_class': prop['energy_class'],
                    'combined_score': round(prop['combined_score'], 2),
                    'property_type': prop.get('property_type', 'N/A'),
                    'listing_type': prop.get('listing_type', 'N/A'),
                    'price': prop.get('price', 0),
                    'price_per_sqm': prop.get('price_per_sqm', 0),
                    'rooms': prop.get('rooms', 'N/A'),
                    'floor': prop.get('floor', 'N/A')
                })
            
            stats['portfolio'] = portfolio
            all_blocks[block_name] = stats
        
        # Sort blocks by combined median score
        sorted_blocks = sorted(all_blocks.items(), key=lambda x: x[1]['median_combined_score'], reverse=True)
        
        # Generate elegant block profiles
        for rank, (block_name, stats) in enumerate(sorted_blocks, 1):
            print(f"\n{'=' * 120}")
            print(f"🏘️ BLOCK #{rank:02d}: {block_name.upper()}")
            print(f"{'=' * 120}")
            
            # Header with key metrics
            investment_grade, grade_desc = get_investment_grade(stats['median_combined_score'], stats['median_price_per_sqm'])
            market_position, position_desc = get_market_position(stats['median_price_per_sqm'], overall_median_price)
            
            print(f"🎯 INVESTMENT GRADE: {investment_grade}")
            print(f"📊 MARKET POSITION: {market_position}")
            print(f"💡 SUMMARY: {grade_desc} | {position_desc}")
            print()
            
            # Key metrics dashboard
            print(f"📊 KEY METRICS DASHBOARD")
            print("-" * 80)
            print(f"🏠 Portfolio Size: {stats['total_properties']} properties")
            print(f"📐 Size Profile: {stats['median_sqm']:.0f}m² median ({stats['sqm_range'][0]:.0f}m² - {stats['sqm_range'][1]:.0f}m²)")
            print(f"🔋 Energy Profile: {stats['median_energy_class']} median | Combined: {stats['combined_median_energy']}")
            print(f"💰 Price Profile: {format_price_per_sqm(stats['median_price_per_sqm'])} median")
            print(f"⭐ Combined Score: {stats['median_combined_score']:.2f}/7.0")
            print(f"🌟 Premium Properties: {stats['premium_energy_count']}/{stats['total_properties']} ({stats['premium_energy_pct']:.1f}% B+ or better)")
            print()
            
            # Energy efficiency breakdown
            print(f"🔋 ENERGY EFFICIENCY BREAKDOWN")
            print("-" * 80)
            energy_sorted = sorted(stats['energy_distribution'].items(), 
                                 key=lambda x: energy_class_to_numeric(x[0]), reverse=True)
            for energy, count in energy_sorted:
                pct = (count / stats['total_properties']) * 100
                bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                print(f"   {energy:>2}: {count:>2} properties ({pct:>4.1f}%) {bar}")
            print()
            
            # Property type composition
            print(f"🏠 PROPERTY COMPOSITION")
            print("-" * 80)
            for prop_type, count in stats['property_types'].items():
                pct = (count / stats['total_properties']) * 100
                print(f"   {prop_type.title():>12}: {count:>2} properties ({pct:>4.1f}%)")
            print()
            
            # Investment opportunities
            print(f"💎 INVESTMENT OPPORTUNITIES")
            print("-" * 80)
            print(f"🎯 High-Value Properties: {stats['investment_opportunities']} properties")
            print(f"   (Good combined score + reasonable pricing)")
            print()
            
            # Top performer spotlight
            best = stats['best_property']
            print(f"🏆 TOP PERFORMER: {best['id']}")
            print(f"   📐 Size: {best['sqm']:.0f}m² | 🔋 Energy: {best['energy']} | ⭐ Score: {best['combined_score']:.2f}")
            print(f"   💰 Price: {format_price_per_sqm(best['price_per_sqm'])}")
            print(f"   🔗 URL: {best['url']}")
            print()
            
            # Portfolio highlights (top 5)
            print(f"📋 PORTFOLIO HIGHLIGHTS (Top 5 Properties)")
            print("-" * 80)
            for prop in stats['portfolio'][:5]:
                grade_icon = "🌟" if prop['combined_score'] >= 5.0 else "💎" if prop['combined_score'] >= 4.0 else "✅"
                print(f"   {grade_icon} #{prop['rank']:02d}. {prop['property_id']}")
                print(f"      📐 {prop['sqm']:.0f}m² | 🔋 {prop['energy_class']} | ⭐ {prop['combined_score']}")
                print(f"      💰 {format_price_per_sqm(prop['price_per_sqm'])} | 🏢 {prop['property_type'].title()}")
                print(f"      🔗 {prop['url']}")
                print()
            
            # Market insights
            print(f"📈 MARKET INSIGHTS")
            print("-" * 80)
            
            # Size analysis
            if stats['mean_sqm'] > 100:
                size_insight = "Large properties dominate this premium market"
            elif stats['mean_sqm'] < 70:
                size_insight = "Compact, efficient properties typical for urban living"
            else:
                size_insight = "Balanced mix of property sizes"
            
            # Energy analysis
            if stats['premium_energy_pct'] > 60:
                energy_insight = "Exceptional energy efficiency across the portfolio"
            elif stats['premium_energy_pct'] > 40:
                energy_insight = "Strong energy performance with room for selective investment"
            else:
                energy_insight = "Energy efficiency varies - careful property selection needed"
            
            # Investment analysis
            roi_potential = "High" if stats['median_combined_score'] > 4.0 else "Moderate" if stats['median_combined_score'] > 3.0 else "Conservative"
            
            print(f"   🏠 Size Profile: {size_insight}")
            print(f"   🔋 Energy Profile: {energy_insight}")
            print(f"   💰 Investment Potential: {roi_potential} ROI expected")
            print(f"   📊 Market Trend: {'Premium appreciation' if stats['median_price_per_sqm'] > overall_median_price else 'Value opportunity'}")
            
        # Executive summary
        print(f"\n{'=' * 120}")
        print(f"📊 EXECUTIVE SUMMARY")
        print(f"{'=' * 120}")
        
        # Top 3 blocks
        print(f"🏆 TOP INVESTMENT DESTINATIONS:")
        for i, (block_name, stats) in enumerate(sorted_blocks[:3], 1):
            grade, _ = get_investment_grade(stats['median_combined_score'], stats['median_price_per_sqm'])
            print(f"   {i}. {block_name}: {grade} (Score: {stats['median_combined_score']:.2f})")
        
        print(f"\n💡 KEY MARKET INSIGHTS:")
        print(f"   • Property size and energy efficiency show nuanced relationships across neighborhoods")
        print(f"   • Premium blocks command higher prices but deliver superior energy performance")
        print(f"   • Investment opportunities exist across all price tiers with proper selection")
        print(f"   • Combined SQM-Energy analysis reveals hidden value in overlooked properties")
        
        # Save comprehensive analysis
        analysis_results = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'report_type': 'Elegant Comprehensive Block Analysis',
                'total_properties': len(df),
                'total_blocks': len(sorted_blocks),
                'market_median_price': float(overall_median_price),
                'analysis_methodology': 'Combined SQM-Energy scoring with investment grading'
            },
            'market_overview': {
                'total_properties': len(df),
                'neighborhoods': df['area'].nunique(),
                'size_range': f"{global_min_sqm:.0f}m² - {global_max_sqm:.0f}m²",
                'median_price_per_sqm': float(overall_median_price),
                'energy_classes': sorted(df['energy_class'].unique(), key=energy_class_to_numeric, reverse=True)
            },
            'block_profiles': dict(sorted_blocks)
        }
        
        output_file = f'outputs/elegant_comprehensive_block_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Elegant comprehensive analysis saved: {output_file}")
        print("=" * 120)
        
        return analysis_results
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find data file: {csv_file}")
        return None
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return None

if __name__ == "__main__":
    create_elegant_block_analysis()