#!/usr/bin/env python3
"""
Data Validity Auditor
Investigate suspicious energy class patterns and validate real vs synthetic data
"""

import asyncio
import logging
import json
from typing import List, Dict, Any
from datetime import datetime

from scraper_100_percent_real import HundredPercentRealDataScraper

logging.basicConfig(level=logging.INFO)

class DataValidityAuditor:
    """Audit extracted data for validity and authenticity"""
    
    def __init__(self):
        self.scraper = HundredPercentRealDataScraper()
        logging.info("🔍 Data Validity Auditor initialized")
    
    async def comprehensive_data_audit(self, area_name: str) -> Dict[str, Any]:
        """Perform comprehensive audit of extracted data"""
        
        logging.info(f"🔍 COMPREHENSIVE DATA VALIDITY AUDIT for {area_name}")
        logging.info(f"=" * 60)
        
        # Extract properties for audit
        properties = await self.scraper.get_real_properties_only(area_name)
        
        if not properties:
            logging.error(f"❌ No properties extracted for audit")
            return {}
        
        audit_results = {
            'area_name': area_name,
            'total_properties': len(properties),
            'audit_timestamp': datetime.now().isoformat(),
            'suspicions': [],
            'data_patterns': {},
            'sample_properties': [],
            'recommendations': []
        }
        
        # Audit 1: Energy class distribution analysis
        logging.info(f"\n🔍 AUDIT 1: Energy Class Distribution Analysis")
        energy_audit = self._audit_energy_class_distribution(properties)
        audit_results['energy_class_audit'] = energy_audit
        
        # Audit 2: Raw data inspection
        logging.info(f"\n🔍 AUDIT 2: Raw Data Inspection")
        raw_data_audit = self._audit_raw_data_extraction(properties)
        audit_results['raw_data_audit'] = raw_data_audit
        
        # Audit 3: Price vs Area correlation
        logging.info(f"\n🔍 AUDIT 3: Price vs Area Correlation")
        correlation_audit = self._audit_price_area_correlation(properties)
        audit_results['correlation_audit'] = correlation_audit
        
        # Audit 4: Text content analysis
        logging.info(f"\n🔍 AUDIT 4: Source Text Analysis")
        text_audit = self._audit_source_text_patterns(properties)
        audit_results['text_audit'] = text_audit
        
        # Generate final assessment
        final_assessment = self._generate_final_assessment(audit_results)
        audit_results['final_assessment'] = final_assessment
        
        # Save audit report
        audit_file = f"outputs/data_validity_audit_{area_name.lower()}.json"
        with open(audit_file, 'w', encoding='utf-8') as f:
            json.dump(audit_results, f, indent=2, ensure_ascii=False, default=str)
        
        logging.info(f"\n💾 Audit report saved: {audit_file}")
        
        return audit_results
    
    def _audit_energy_class_distribution(self, properties: List) -> Dict[str, Any]:
        """Audit energy class distribution for realism"""
        
        energy_classes = [p.energy_class for p in properties if p.energy_class]
        energy_distribution = {}
        
        for ec in energy_classes:
            energy_distribution[ec] = energy_distribution.get(ec, 0) + 1
        
        total_with_energy = len(energy_classes)
        percentage_with_energy = (total_with_energy / len(properties)) * 100
        
        logging.info(f"   Properties with energy class: {total_with_energy}/{len(properties)} ({percentage_with_energy:.1f}%)")
        
        if energy_distribution:
            logging.info(f"   Energy distribution: {energy_distribution}")
            
            # Check for suspicious patterns
            suspicions = []
            
            # Too many A ratings is suspicious for Athens
            a_ratings = energy_distribution.get('A', 0) + energy_distribution.get('A+', 0)
            if a_ratings > total_with_energy * 0.3:  # More than 30% A-rated is suspicious
                suspicions.append(f"🚨 SUSPICIOUS: {a_ratings}/{total_with_energy} properties rated A/A+ ({a_ratings/total_with_energy*100:.1f}%)")
                suspicions.append("   Expected in Athens: Mostly C, D, E ratings for older buildings")
            
            # Too few low ratings is suspicious
            low_ratings = energy_distribution.get('D', 0) + energy_distribution.get('E', 0) + energy_distribution.get('F', 0)
            if low_ratings == 0 and total_with_energy > 5:
                suspicions.append("🚨 SUSPICIOUS: No D/E/F ratings found")
                suspicions.append("   Expected in Athens: Many older buildings should have low ratings")
            
            for suspicion in suspicions:
                logging.warning(suspicion)
        else:
            logging.warning("   ⚠️ No energy class data found")
        
        return {
            'total_properties': len(properties),
            'properties_with_energy': total_with_energy,
            'percentage_with_energy': percentage_with_energy,
            'distribution': energy_distribution,
            'suspicions': suspicions if 'suspicions' in locals() else []
        }
    
    def _audit_raw_data_extraction(self, properties: List) -> Dict[str, Any]:
        """Audit raw data extraction patterns"""
        
        # Sample first 5 properties for detailed inspection
        sample_properties = properties[:5]
        
        logging.info(f"   Inspecting {len(sample_properties)} sample properties:")
        
        extraction_patterns = {
            'common_descriptions': {},
            'price_patterns': [],
            'area_patterns': [],
            'energy_extraction_sources': [],
            'suspicious_duplicates': []
        }
        
        for i, prop in enumerate(sample_properties):
            logging.info(f"\n   🏠 Property {i+1} ({prop.id}):")
            logging.info(f"      Title: {prop.title}")
            logging.info(f"      Price: €{prop.price:,}" if prop.price else "      Price: N/A")
            logging.info(f"      Area: {prop.sqm}m²" if prop.sqm else "      Area: N/A")
            logging.info(f"      Energy: {prop.energy_class}" if prop.energy_class else "      Energy: N/A")
            logging.info(f"      Description: {prop.description[:100]}..." if prop.description else "      Description: N/A")
            logging.info(f"      Validation flags: {prop.validation_flags}")
            logging.info(f"      Confidence: {prop.confidence_score}")
            
            # Check for patterns that might indicate synthetic data
            if prop.description:
                desc_key = prop.description[:50]
                extraction_patterns['common_descriptions'][desc_key] = extraction_patterns['common_descriptions'].get(desc_key, 0) + 1
            
            # Check price patterns
            if prop.price:
                extraction_patterns['price_patterns'].append(prop.price)
            
            # Check area patterns  
            if prop.sqm:
                extraction_patterns['area_patterns'].append(prop.sqm)
        
        # Look for suspicious duplicate patterns
        for desc, count in extraction_patterns['common_descriptions'].items():
            if count > 1:
                extraction_patterns['suspicious_duplicates'].append(f"Description appears {count} times: {desc}...")
        
        if extraction_patterns['suspicious_duplicates']:
            logging.warning(f"   🚨 SUSPICIOUS DUPLICATES FOUND:")
            for dup in extraction_patterns['suspicious_duplicates']:
                logging.warning(f"      {dup}")
        
        return extraction_patterns
    
    def _audit_price_area_correlation(self, properties: List) -> Dict[str, Any]:
        """Audit price vs area correlation for realism"""
        
        valid_properties = [p for p in properties if p.price and p.sqm and p.price > 0 and p.sqm > 0]
        
        if len(valid_properties) < 5:
            logging.warning(f"   ⚠️ Insufficient price/area data for correlation analysis")
            return {'status': 'insufficient_data'}
        
        price_per_sqm_values = [p.price / p.sqm for p in valid_properties]
        
        min_price_per_sqm = min(price_per_sqm_values)
        max_price_per_sqm = max(price_per_sqm_values)
        avg_price_per_sqm = sum(price_per_sqm_values) / len(price_per_sqm_values)
        
        logging.info(f"   Properties with price & area: {len(valid_properties)}")
        logging.info(f"   Price per m² range: €{min_price_per_sqm:.0f} - €{max_price_per_sqm:.0f}")
        logging.info(f"   Average price per m²: €{avg_price_per_sqm:.0f}")
        
        # Check for suspicious patterns
        suspicions = []
        
        # Unrealistic price ranges
        if max_price_per_sqm > 10000:  # More than €10k per sqm is suspicious
            suspicions.append(f"🚨 SUSPICIOUS: Very high price per sqm (€{max_price_per_sqm:.0f})")
        
        if min_price_per_sqm < 100:  # Less than €100 per sqm is suspicious
            suspicions.append(f"🚨 SUSPICIOUS: Very low price per sqm (€{min_price_per_sqm:.0f})")
        
        # Check for identical values (might indicate synthetic data)
        unique_values = len(set(price_per_sqm_values))
        if unique_values < len(price_per_sqm_values) * 0.8:  # Less than 80% unique values
            suspicions.append(f"🚨 SUSPICIOUS: Many duplicate price/sqm ratios ({unique_values}/{len(price_per_sqm_values)} unique)")
        
        for suspicion in suspicions:
            logging.warning(f"   {suspicion}")
        
        return {
            'properties_analyzed': len(valid_properties),
            'price_per_sqm_range': [min_price_per_sqm, max_price_per_sqm],
            'average_price_per_sqm': avg_price_per_sqm,
            'unique_ratios': unique_values,
            'suspicions': suspicions
        }
    
    def _audit_source_text_patterns(self, properties: List) -> Dict[str, Any]:
        """Audit source text patterns for extraction accuracy"""
        
        # Look at raw descriptions for actual energy class mentions
        energy_mentions = []
        actual_energy_extractions = []
        
        for prop in properties:
            if prop.description:
                # Look for energy-related text in descriptions
                desc_lower = prop.description.lower()
                
                if any(keyword in desc_lower for keyword in ['energy', 'ενεργ', 'κλάση', 'class']):
                    energy_mentions.append({
                        'property_id': prop.id,
                        'description': prop.description[:200],
                        'extracted_energy': prop.energy_class,
                        'confidence': prop.confidence_score
                    })
                
                # Check if extracted energy class actually appears in description
                if prop.energy_class:
                    if prop.energy_class.lower() in desc_lower:
                        actual_energy_extractions.append(prop.energy_class)
        
        logging.info(f"   Properties with energy-related text: {len(energy_mentions)}")
        logging.info(f"   Energy classes actually found in text: {len(actual_energy_extractions)}")
        
        if energy_mentions:
            logging.info(f"   Sample energy mentions:")
            for mention in energy_mentions[:3]:
                logging.info(f"     - ID: {mention['property_id']}")
                logging.info(f"       Text: {mention['description'][:100]}...")
                logging.info(f"       Extracted: {mention['extracted_energy']}")
        
        # Check for patterns that might indicate incorrect extraction
        suspicions = []
        
        if len(energy_mentions) == 0 and len([p for p in properties if p.energy_class]) > 0:
            suspicions.append("🚨 CRITICAL: Energy classes extracted but no energy-related text found in descriptions")
            suspicions.append("   This strongly suggests synthetic or incorrect data")
        
        extraction_accuracy = len(actual_energy_extractions) / len([p for p in properties if p.energy_class]) if len([p for p in properties if p.energy_class]) > 0 else 0
        
        if extraction_accuracy < 0.5:  # Less than 50% accuracy
            suspicions.append(f"🚨 SUSPICIOUS: Low extraction accuracy ({extraction_accuracy*100:.1f}%)")
            suspicions.append("   Extracted energy classes don't match source text")
        
        for suspicion in suspicions:
            logging.warning(f"   {suspicion}")
        
        return {
            'energy_mentions_found': len(energy_mentions),
            'accurate_extractions': len(actual_energy_extractions),
            'extraction_accuracy': extraction_accuracy,
            'sample_mentions': energy_mentions[:3],
            'suspicions': suspicions
        }
    
    def _generate_final_assessment(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final data validity assessment"""
        
        logging.info(f"\n" + "="*60)
        logging.info(f"📋 FINAL DATA VALIDITY ASSESSMENT")
        logging.info(f"="*60)
        
        # Count total suspicions
        all_suspicions = []
        
        for audit_type, results in audit_results.get('energy_class_audit', {}).items():
            if audit_type == 'suspicions' and isinstance(results, list):
                all_suspicions.extend(results)
        
        correlation_suspicions = audit_results.get('correlation_audit', {}).get('suspicions', [])
        all_suspicions.extend(correlation_suspicions)
        
        text_suspicions = audit_results.get('text_audit', {}).get('suspicions', [])
        all_suspicions.extend(text_suspicions)
        
        # Generate overall assessment
        total_suspicions = len(all_suspicions)
        
        if total_suspicions == 0:
            validity_score = "HIGH"
            assessment = "Data appears to be authentic and accurately extracted"
        elif total_suspicions <= 2:
            validity_score = "MEDIUM"
            assessment = "Some suspicious patterns detected, requires investigation"
        else:
            validity_score = "LOW"
            assessment = "Multiple suspicious patterns detected, data may be synthetic or incorrectly extracted"
        
        logging.info(f"\n🎯 OVERALL ASSESSMENT:")
        logging.info(f"   Validity Score: {validity_score}")
        logging.info(f"   Total Suspicions: {total_suspicions}")
        logging.info(f"   Assessment: {assessment}")
        
        if all_suspicions:
            logging.info(f"\n🚨 ALL SUSPICIONS DETECTED:")
            for i, suspicion in enumerate(all_suspicions, 1):
                logging.info(f"   {i}. {suspicion}")
        
        # Recommendations
        recommendations = []
        
        if validity_score == "LOW":
            recommendations.extend([
                "❌ CRITICAL: Stop using this data for analysis",
                "🔧 Fix extraction patterns to capture real energy class data",
                "🧐 Investigate why energy class extraction is inaccurate",
                "📊 Validate extraction against actual website content"
            ])
        elif validity_score == "MEDIUM":
            recommendations.extend([
                "⚠️ CAUTION: Review extraction accuracy",
                "🔍 Manual verification of sample properties recommended",
                "📈 Consider improving extraction patterns"
            ])
        else:
            recommendations.append("✅ Data appears valid for analysis")
        
        logging.info(f"\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            logging.info(f"   {rec}")
        
        return {
            'validity_score': validity_score,
            'total_suspicions': total_suspicions,
            'assessment': assessment,
            'recommendations': recommendations,
            'all_suspicions': all_suspicions
        }


async def main():
    """Run comprehensive data validity audit"""
    
    print("🔍 DATA VALIDITY AUDIT")
    print("=" * 50)
    print("Investigating suspicious energy class patterns...")
    
    auditor = DataValidityAuditor()
    
    # Audit Kolonaki data (where we saw mostly A ratings)
    audit_results = await auditor.comprehensive_data_audit("Kolonaki")
    
    print(f"\n📊 AUDIT COMPLETE")
    print(f"Check the detailed report for full analysis")

if __name__ == "__main__":
    asyncio.run(main())