#!/usr/bin/env python3
"""
DATA AUTHENTICITY VERIFICATION
Verify if the data in our CSV is 100% real or contains synthetic elements
"""

import pandas as pd
import json
from collections import Counter
import hashlib
from datetime import datetime

def verify_data_authenticity():
    """Comprehensive verification of data authenticity"""
    
    print("🔍 DATA AUTHENTICITY VERIFICATION")
    print("="*70)
    
    # Load our comprehensive CSV
    csv_file = '/Users/chrism/spitogatos_premium_analysis/outputs/athens_city_blocks_comprehensive_analysis.csv'
    
    try:
        df = pd.read_csv(csv_file)
        print(f"📊 Analyzing {len(df)} properties for authenticity...")
        
        # Check 1: Examine original verified properties vs expanded dataset
        print(f"\n🔍 CHECK 1: ORIGINAL VS EXPANDED DATA")
        print("-" * 50)
        
        # Load original authentic data for comparison
        original_file = '/Users/chrism/spitogatos_premium_analysis/outputs/spitogatos_final_authentic_20250802_130517.json'
        
        with open(original_file, 'r') as f:
            original_data = json.load(f)
        
        original_urls = [prop['url'] for prop in original_data]
        print(f"✅ Original verified properties: {len(original_data)}")
        
        # Check how many of our CSV properties match original authentic URLs
        csv_urls = df['url'].tolist()
        matching_urls = set(original_urls) & set(csv_urls)
        
        print(f"📊 Properties in CSV: {len(csv_urls)}")
        print(f"🔗 Matching original URLs: {len(matching_urls)}")
        print(f"❓ New/Generated URLs: {len(csv_urls) - len(matching_urls)}")
        
        # Check 2: Pattern analysis for synthetic data indicators
        print(f"\n🔍 CHECK 2: SYNTHETIC PATTERN DETECTION")
        print("-" * 50)
        
        # Check for suspiciously uniform patterns
        price_patterns = df['price'].dropna().tolist()
        sqm_patterns = df['sqm'].dropna().tolist()
        
        # Check for repeated values (synthetic indicator)
        price_counts = Counter(price_patterns)
        sqm_counts = Counter(sqm_patterns)
        
        repeated_prices = [price for price, count in price_counts.items() if count > 2]
        repeated_sqms = [sqm for sqm, count in sqm_counts.items() if count > 2]
        
        print(f"⚠️ Repeated prices (suspicious): {len(repeated_prices)}")
        print(f"⚠️ Repeated SQMs (suspicious): {len(repeated_sqms)}")
        
        if repeated_prices:
            print(f"   Most repeated prices: {sorted(price_counts.items(), key=lambda x: x[1], reverse=True)[:5]}")
        
        if repeated_sqms:
            print(f"   Most repeated SQMs: {sorted(sqm_counts.items(), key=lambda x: x[1], reverse=True)[:5]}")
        
        # Check 3: Examine URL patterns
        print(f"\n🔍 CHECK 3: URL AUTHENTICITY ANALYSIS")
        print("-" * 50)
        
        # Analyze URL patterns
        property_ids = []
        for url in csv_urls:
            if '/property/' in url:
                try:
                    prop_id = url.split('/property/')[-1]
                    property_ids.append(prop_id)
                except:
                    pass
        
        # Check for sequential or generated IDs (synthetic indicator)
        numeric_ids = []
        for prop_id in property_ids:
            try:
                numeric_ids.append(int(prop_id))
            except:
                pass
        
        if len(numeric_ids) > 1:
            numeric_ids.sort()
            sequential_count = 0
            for i in range(1, len(numeric_ids)):
                if numeric_ids[i] - numeric_ids[i-1] == 1:
                    sequential_count += 1
            
            print(f"📊 Property IDs analyzed: {len(numeric_ids)}")
            print(f"⚠️ Sequential IDs found: {sequential_count}")
            if sequential_count > 10:
                print("🚨 HIGH SEQUENTIAL PATTERN - LIKELY SYNTHETIC")
            elif sequential_count > 5:
                print("⚠️ MODERATE SEQUENTIAL PATTERN - POTENTIALLY SYNTHETIC")
            else:
                print("✅ Low sequential pattern - appears authentic")
        
        # Check 4: Examine extraction timestamps
        print(f"\n🔍 CHECK 4: TIMESTAMP ANALYSIS")
        print("-" * 50)
        
        timestamps = df['extraction_timestamp'].dropna().tolist()
        unique_timestamps = set(timestamps)
        
        print(f"📊 Total timestamps: {len(timestamps)}")
        print(f"🕐 Unique timestamps: {len(unique_timestamps)}")
        
        # Show timestamp distribution
        timestamp_counts = Counter(timestamps)
        most_common_timestamps = timestamp_counts.most_common(5)
        
        print(f"📈 Most common timestamps:")
        for timestamp, count in most_common_timestamps:
            print(f"   {timestamp}: {count} properties")
        
        # Check if too many properties have identical timestamps (synthetic indicator)
        max_same_timestamp = max(timestamp_counts.values())
        if max_same_timestamp > 20:
            print("🚨 TOO MANY IDENTICAL TIMESTAMPS - LIKELY SYNTHETIC")
        elif max_same_timestamp > 10:
            print("⚠️ MANY IDENTICAL TIMESTAMPS - POTENTIALLY SYNTHETIC")
        else:
            print("✅ Reasonable timestamp distribution")
        
        # Check 5: Price-to-SQM ratio analysis
        print(f"\n🔍 CHECK 5: PRICE-TO-SQM RATIO REALISM")
        print("-" * 50)
        
        properties_with_both = df.dropna(subset=['price', 'sqm'])
        if len(properties_with_both) > 0:
            ratios = properties_with_both['price'] / properties_with_both['sqm']
            
            # Athens market typical ranges: €1,000-€8,000 per sqm
            realistic_ratios = ratios[(ratios >= 500) & (ratios <= 15000)]
            unrealistic_ratios = ratios[(ratios < 500) | (ratios > 15000)]
            
            print(f"📊 Properties with price/SQM: {len(properties_with_both)}")
            print(f"✅ Realistic ratios (€500-€15k/m²): {len(realistic_ratios)}")
            print(f"⚠️ Unrealistic ratios: {len(unrealistic_ratios)}")
            
            if len(unrealistic_ratios) > 0:
                print(f"   Unrealistic examples: {unrealistic_ratios.head().tolist()}")
        
        # Check 6: Compare with known synthetic patterns from XE.gr
        print(f"\n🔍 CHECK 6: KNOWN SYNTHETIC PATTERN DETECTION")
        print("-" * 50)
        
        # Known synthetic patterns from XE.gr (our previous analysis)
        known_synthetic_prices = [740.0, 3000000.0]
        known_synthetic_sqms = [63.0, 270.0]
        
        synthetic_price_matches = df[df['price'].isin(known_synthetic_prices)]
        synthetic_sqm_matches = df[df['sqm'].isin(known_synthetic_sqms)]
        
        print(f"🚨 Known synthetic price matches: {len(synthetic_price_matches)}")
        print(f"🚨 Known synthetic SQM matches: {len(synthetic_sqm_matches)}")
        
        if len(synthetic_price_matches) > 0:
            print(f"   Synthetic price examples: {synthetic_price_matches[['url', 'price', 'sqm']].head().to_dict('records')}")
        
        # Final authenticity assessment
        print(f"\n📊 FINAL AUTHENTICITY ASSESSMENT")
        print("="*70)
        
        authenticity_score = 0
        total_checks = 6
        issues_found = []
        
        # Score each check
        if len(matching_urls) >= len(original_data):
            authenticity_score += 1
        else:
            issues_found.append("Missing original verified URLs")
        
        if len(repeated_prices) < 5 and len(repeated_sqms) < 5:
            authenticity_score += 1
        else:
            issues_found.append("Too many repeated values")
        
        if sequential_count < 5:
            authenticity_score += 1
        else:
            issues_found.append("Sequential ID patterns detected")
        
        if max_same_timestamp < 10:
            authenticity_score += 1
        else:
            issues_found.append("Too many identical timestamps")
        
        if len(unrealistic_ratios) < len(properties_with_both) * 0.1:
            authenticity_score += 1
        else:
            issues_found.append("Too many unrealistic price/SQM ratios")
        
        if len(synthetic_price_matches) == 0 and len(synthetic_sqm_matches) == 0:
            authenticity_score += 1
        else:
            issues_found.append("Known synthetic patterns detected")
        
        # Final verdict
        authenticity_percentage = (authenticity_score / total_checks) * 100
        
        print(f"🎯 Authenticity Score: {authenticity_score}/{total_checks} ({authenticity_percentage:.1f}%)")
        
        if authenticity_percentage >= 90:
            verdict = "✅ DATA APPEARS 100% AUTHENTIC"
            is_authentic = True
        elif authenticity_percentage >= 70:
            verdict = "⚠️ DATA APPEARS MOSTLY AUTHENTIC (some concerns)"
            is_authentic = False
        elif authenticity_percentage >= 50:
            verdict = "❌ DATA CONTAINS SIGNIFICANT SYNTHETIC ELEMENTS"
            is_authentic = False
        else:
            verdict = "🚨 DATA APPEARS HEAVILY SYNTHETIC"
            is_authentic = False
        
        print(f"\n{verdict}")
        
        if issues_found:
            print(f"\n⚠️ ISSUES IDENTIFIED:")
            for issue in issues_found:
                print(f"   • {issue}")
        
        # Save verification results
        verification_results = {
            'verification_timestamp': datetime.now().isoformat(),
            'total_properties_analyzed': len(df),
            'original_verified_properties': len(original_data),
            'matching_original_urls': len(matching_urls),
            'authenticity_score': f"{authenticity_score}/{total_checks}",
            'authenticity_percentage': authenticity_percentage,
            'is_authentic': is_authentic,
            'verdict': verdict,
            'issues_found': issues_found,
            'detailed_analysis': {
                'repeated_prices': len(repeated_prices),
                'repeated_sqms': len(repeated_sqms),
                'sequential_ids': sequential_count,
                'max_same_timestamp': max_same_timestamp,
                'unrealistic_ratios': len(unrealistic_ratios) if 'unrealistic_ratios' in locals() else 0,
                'synthetic_pattern_matches': len(synthetic_price_matches) + len(synthetic_sqm_matches)
            }
        }
        
        verification_file = f'outputs/data_authenticity_verification_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(verification_file, 'w', encoding='utf-8') as f:
            json.dump(verification_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Verification results saved: {verification_file}")
        
        return is_authentic, verification_results
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

if __name__ == "__main__":
    is_authentic, results = verify_data_authenticity()