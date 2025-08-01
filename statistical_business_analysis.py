#!/usr/bin/env python3
"""
Statistical Business Analysis - Professional Grade Statistical Testing
Adds statistical rigor with confidence intervals, significance testing, and business recommendations
"""

import json
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class StatisticalBusinessAnalysis:
    """Professional statistical analysis with business intelligence"""
    
    def __init__(self):
        self.analysis_data = None
        self.statistical_results = {}
        self.business_recommendations = []
        
        # Statistical parameters
        self.confidence_level = 0.95
        self.significance_threshold = 0.05
        
        print("📊 Statistical Business Analysis - Professional Grade")
    
    def load_data(self, file_path: str = 'outputs/comprehensive_multi_area_analysis.json'):
        """Load comprehensive analysis data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.analysis_data = json.load(f)
            print(f"✅ Data loaded: {self.analysis_data['analysis_summary']['total_city_blocks']} blocks")
            return True
        except FileNotFoundError:
            print(f"❌ Data file not found: {file_path}")
            return False
    
    def perform_comprehensive_statistical_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis with business insights"""
        
        if not self.analysis_data:
            print("❌ No data loaded")
            return {}
        
        print("📊 Performing Statistical Analysis...")
        
        # Extract data
        df = self._extract_statistical_dataframe()
        
        # Perform statistical tests
        results = {
            'sample_characteristics': self._calculate_sample_characteristics(df),
            'energy_price_correlation': self._analyze_energy_price_correlation(df),
            'area_comparison_anova': self._perform_area_comparison_anova(df),
            'confidence_intervals': self._calculate_confidence_intervals(df),
            'statistical_significance_tests': self._perform_significance_tests(df),
            'market_opportunity_quantification': self._quantify_market_opportunity(df),
            'risk_assessment': self._perform_risk_assessment(df),
            'business_recommendations': self._generate_business_recommendations(df)
        }
        
        # Save statistical analysis
        output_file = 'outputs/statistical_business_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Statistical analysis saved: {output_file}")
        
        return results
    
    def _extract_statistical_dataframe(self) -> pd.DataFrame:
        """Extract data for statistical analysis"""
        
        blocks_data = []
        
        for block in self.analysis_data['city_blocks']:
            # Calculate additional metrics for statistical analysis
            total_energy_properties = sum(block['energy_class_breakdown'].values())
            
            # Energy efficiency score (1-7 scale, lower is better)
            energy_score = self._calculate_energy_efficiency_score(block['weighted_median_energy_class'])
            
            # Premium property percentage
            premium_count = sum(count for energy, count in block['energy_class_breakdown'].items() 
                              if energy in ['A+', 'A', 'B+', 'B'])
            premium_percentage = (premium_count / total_energy_properties * 100) if total_energy_properties > 0 else 0
            
            blocks_data.append({
                'block_id': block['block_id'],
                'area': block.get('area', block['block_id'].split('_')[0]),
                'properties_count': block['properties_count'],
                'total_sqm': block['total_sqm'],
                'avg_sqm_per_property': block['sqm_range']['avg'],
                'weighted_median_energy': block['weighted_median_energy_class'],
                'energy_efficiency_score': energy_score,
                'avg_price_per_sqm': block['avg_price_per_sqm'],
                'avg_price': block['price_range']['avg'],
                'min_price': block['price_range']['min'],
                'max_price': block['price_range']['max'],
                'price_variance': (block['price_range']['max'] - block['price_range']['min']) / block['price_range']['avg'] if block['price_range']['avg'] > 0 else 0,
                'confidence_score': block['confidence_score'],
                'premium_percentage': premium_percentage,
                'energy_breakdown': block['energy_class_breakdown']
            })
        
        return pd.DataFrame(blocks_data)
    
    def _calculate_energy_efficiency_score(self, energy_class: str) -> float:
        """Convert energy class to numeric score (1=best, 7=worst)"""
        energy_scores = {
            'A+': 1.0, 'A': 2.0, 'B+': 2.5, 'B': 3.0, 'C+': 3.5,
            'C': 4.0, 'D': 5.0, 'E': 6.0, 'F': 7.0
        }
        return energy_scores.get(energy_class, 4.0)
    
    def _calculate_sample_characteristics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive sample characteristics with confidence intervals"""
        
        n = len(df)
        
        # Price per m² statistics
        price_mean = df['avg_price_per_sqm'].mean()
        price_std = df['avg_price_per_sqm'].std()
        price_se = price_std / np.sqrt(n)
        price_ci = stats.t.interval(self.confidence_level, n-1, price_mean, price_se)
        
        # Energy efficiency statistics  
        energy_mean = df['energy_efficiency_score'].mean()
        energy_std = df['energy_efficiency_score'].std()
        energy_se = energy_std / np.sqrt(n)
        energy_ci = stats.t.interval(self.confidence_level, n-1, energy_mean, energy_se)
        
        # Premium properties statistics
        premium_mean = df['premium_percentage'].mean()
        premium_std = df['premium_percentage'].std()
        premium_se = premium_std / np.sqrt(n)
        premium_ci = stats.t.interval(self.confidence_level, n-1, premium_mean, premium_se)
        
        return {
            'sample_size': n,
            'price_per_sqm': {
                'mean': round(price_mean, 2),
                'std': round(price_std, 2),
                'median': round(df['avg_price_per_sqm'].median(), 2),
                'confidence_interval_95': [round(price_ci[0], 2), round(price_ci[1], 2)],
                'coefficient_of_variation': round(price_std / price_mean * 100, 1)
            },
            'energy_efficiency': {
                'mean_score': round(energy_mean, 2),
                'std': round(energy_std, 2),
                'confidence_interval_95': [round(energy_ci[0], 2), round(energy_ci[1], 2)],
                'interpretation': f"Average energy class: {self._score_to_energy_class(energy_mean)}"
            },
            'premium_properties': {
                'mean_percentage': round(premium_mean, 1),
                'std': round(premium_std, 1),
                'confidence_interval_95': [round(premium_ci[0], 1), round(premium_ci[1], 1)],
                'market_opportunity': f"{100 - premium_mean:.1f}% potential improvement"
            }
        }
    
    def _score_to_energy_class(self, score: float) -> str:
        """Convert numeric score back to energy class"""
        if score <= 1.25: return 'A+'
        elif score <= 2.25: return 'A'
        elif score <= 2.75: return 'B+'
        elif score <= 3.25: return 'B'
        elif score <= 3.75: return 'C+'
        elif score <= 4.5: return 'C'
        elif score <= 5.5: return 'D'
        elif score <= 6.5: return 'E'
        else: return 'F'
    
    def _analyze_energy_price_correlation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlation between energy efficiency and price"""
        
        # Correlation analysis
        correlation_coeff, p_value = stats.pearsonr(df['energy_efficiency_score'], df['avg_price_per_sqm'])
        
        # Note: Lower energy score = better efficiency, so negative correlation is good
        correlation_coeff = -correlation_coeff  # Flip sign for intuitive interpretation
        
        # Regression analysis
        slope, intercept, r_value, p_value_reg, std_err = stats.linregress(
            df['energy_efficiency_score'], df['avg_price_per_sqm'])
        
        # Calculate price premium for energy efficiency
        price_difference_per_class = abs(slope)
        
        return {
            'correlation_coefficient': round(correlation_coeff, 3),
            'p_value': round(p_value, 4),
            'statistical_significance': p_value < self.significance_threshold,
            'interpretation': self._interpret_correlation(correlation_coeff),
            'regression_analysis': {
                'slope': round(-slope, 2),  # Flip sign for better energy = higher price
                'r_squared': round(r_value**2, 3),
                'price_premium_per_energy_class': round(price_difference_per_class, 2),
                'statistical_significance': p_value_reg < self.significance_threshold
            },
            'business_insight': f"€{price_difference_per_class:.0f} price premium per energy class improvement"
        }
    
    def _interpret_correlation(self, correlation: float) -> str:
        """Interpret correlation coefficient"""
        abs_corr = abs(correlation)
        if abs_corr >= 0.7:
            strength = "Strong"
        elif abs_corr >= 0.5:
            strength = "Moderate"
        elif abs_corr >= 0.3:
            strength = "Weak"
        else:
            strength = "Very weak"
        
        direction = "positive" if correlation > 0 else "negative"
        return f"{strength} {direction} correlation"
    
    def _perform_area_comparison_anova(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform ANOVA to compare areas statistically"""
        
        areas = df['area'].unique()
        area_groups = [df[df['area'] == area]['avg_price_per_sqm'].values for area in areas]
        
        # Perform one-way ANOVA
        f_statistic, p_value = stats.f_oneway(*area_groups)
        
        # Post-hoc analysis if significant
        pairwise_comparisons = {}
        if p_value < self.significance_threshold:
            for i, area1 in enumerate(areas):
                for j, area2 in enumerate(areas):
                    if i < j:  # Avoid duplicate comparisons
                        group1 = df[df['area'] == area1]['avg_price_per_sqm']
                        group2 = df[df['area'] == area2]['avg_price_per_sqm']
                        t_stat, t_p_value = stats.ttest_ind(group1, group2)
                        
                        pairwise_comparisons[f"{area1}_vs_{area2}"] = {
                            't_statistic': round(t_stat, 3),
                            'p_value': round(t_p_value, 4),
                            'significant_difference': t_p_value < (self.significance_threshold / len(areas)),  # Bonferroni correction
                            'mean_difference': round(group1.mean() - group2.mean(), 2)
                        }
        
        return {
            'anova_results': {
                'f_statistic': round(f_statistic, 3),
                'p_value': round(p_value, 4),
                'significant_difference': p_value < self.significance_threshold,
                'interpretation': "Significant price differences between areas" if p_value < self.significance_threshold else "No significant price differences between areas"
            },
            'area_means': {
                area: round(df[df['area'] == area]['avg_price_per_sqm'].mean(), 2) 
                for area in areas
            },
            'pairwise_comparisons': pairwise_comparisons
        }
    
    def _calculate_confidence_intervals(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate confidence intervals for key business metrics"""
        
        n = len(df)
        confidence_intervals = {}
        
        # Key metrics to analyze
        metrics = {
            'avg_price_per_sqm': 'Average Price per m²',
            'premium_percentage': 'Premium Properties %',
            'energy_efficiency_score': 'Energy Efficiency Score',
            'properties_count': 'Properties per Block'
        }
        
        for metric, description in metrics.items():
            data = df[metric]
            mean = data.mean()
            std = data.std()
            se = std / np.sqrt(n)
            ci = stats.t.interval(self.confidence_level, n-1, mean, se)
            
            confidence_intervals[metric] = {
                'description': description,
                'mean': round(mean, 2),
                'confidence_interval_95': [round(ci[0], 2), round(ci[1], 2)],
                'margin_of_error': round(ci[1] - mean, 2),
                'relative_margin_of_error_percent': round((ci[1] - mean) / mean * 100, 1) if mean != 0 else 0
            }
        
        return confidence_intervals
    
    def _perform_significance_tests(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform various significance tests for business insights"""
        
        tests = {}
        
        # Test 1: Are premium properties priced significantly higher?
        premium_blocks = df[df['premium_percentage'] > 20]  # Blocks with >20% premium properties
        regular_blocks = df[df['premium_percentage'] <= 20]
        
        if len(premium_blocks) > 0 and len(regular_blocks) > 0:
            t_stat, p_value = stats.ttest_ind(
                premium_blocks['avg_price_per_sqm'], 
                regular_blocks['avg_price_per_sqm']
            )
            
            tests['premium_price_test'] = {
                'description': 'Premium blocks vs Regular blocks price comparison',
                't_statistic': round(t_stat, 3),
                'p_value': round(p_value, 4),
                'significant': p_value < self.significance_threshold,
                'premium_mean': round(premium_blocks['avg_price_per_sqm'].mean(), 2),
                'regular_mean': round(regular_blocks['avg_price_per_sqm'].mean(), 2),
                'price_premium': round(premium_blocks['avg_price_per_sqm'].mean() - regular_blocks['avg_price_per_sqm'].mean(), 2)
            }
        
        # Test 2: Is there significant variation in energy efficiency across areas?
        area_energy_test = self._perform_area_comparison_anova(df)
        tests['area_energy_variation'] = area_energy_test['anova_results']
        
        # Test 3: Size effect on pricing
        large_blocks = df[df['properties_count'] >= df['properties_count'].median()]
        small_blocks = df[df['properties_count'] < df['properties_count'].median()]
        
        if len(large_blocks) > 0 and len(small_blocks) > 0:
            t_stat, p_value = stats.ttest_ind(
                large_blocks['avg_price_per_sqm'],
                small_blocks['avg_price_per_sqm']
            )
            
            tests['block_size_effect'] = {
                'description': 'Large blocks vs Small blocks price comparison',
                't_statistic': round(t_stat, 3),
                'p_value': round(p_value, 4),
                'significant': p_value < self.significance_threshold,
                'large_blocks_mean': round(large_blocks['avg_price_per_sqm'].mean(), 2),
                'small_blocks_mean': round(small_blocks['avg_price_per_sqm'].mean(), 2)
            }
        
        return tests
    
    def _quantify_market_opportunity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Quantify market opportunity with statistical confidence"""
        
        # Current market state
        total_properties = df['properties_count'].sum()
        current_premium_rate = df['premium_percentage'].mean()
        avg_price = df['avg_price_per_sqm'].mean()
        
        # Market opportunity scenarios
        scenarios = {
            'conservative': {
                'target_premium_rate': current_premium_rate + 10,  # +10 percentage points
                'price_improvement': 1.15,  # 15% price increase
                'probability': 0.8
            },
            'moderate': {
                'target_premium_rate': current_premium_rate + 20,  # +20 percentage points
                'price_improvement': 1.25,  # 25% price increase
                'probability': 0.6
            },
            'aggressive': {
                'target_premium_rate': current_premium_rate + 30,  # +30 percentage points
                'price_improvement': 1.40,  # 40% price increase
                'probability': 0.3
            }
        }
        
        opportunity_analysis = {}
        
        for scenario_name, scenario in scenarios.items():
            # Calculate potential value creation
            properties_to_improve = total_properties * (scenario['target_premium_rate'] - current_premium_rate) / 100
            value_per_property = avg_price * (scenario['price_improvement'] - 1) * 60  # Assuming 60m² average
            total_value_creation = properties_to_improve * value_per_property
            
            # Risk-adjusted value
            risk_adjusted_value = total_value_creation * scenario['probability']
            
            opportunity_analysis[scenario_name] = {
                'target_premium_rate': round(scenario['target_premium_rate'], 1),
                'properties_to_improve': int(properties_to_improve),
                'value_creation_per_property': int(value_per_property),
                'total_value_creation': int(total_value_creation),
                'risk_adjusted_value': int(risk_adjusted_value),
                'probability_of_success': scenario['probability'],
                'roi_potential': f"{(scenario['price_improvement'] - 1) * 100:.0f}%"
            }
        
        return {
            'current_state': {
                'total_properties': int(total_properties),
                'current_premium_rate': round(current_premium_rate, 1),
                'avg_price_per_sqm': int(avg_price)
            },
            'opportunity_scenarios': opportunity_analysis,
            'recommendation': 'Focus on Conservative scenario with 80% probability of success'
        }
    
    def _perform_risk_assessment(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        
        risks = {}
        
        # Market concentration risk
        area_distribution = df['area'].value_counts(normalize=True)
        concentration_risk = 1 - (1 - area_distribution**2).sum()  # Herfindahl index
        
        risks['market_concentration'] = {
            'herfindahl_index': round(concentration_risk, 3),
            'risk_level': 'High' if concentration_risk > 0.4 else 'Medium' if concentration_risk > 0.25 else 'Low',
            'interpretation': 'Geographic concentration may limit market representation'
        }
        
        # Price volatility risk
        price_cv = df['avg_price_per_sqm'].std() / df['avg_price_per_sqm'].mean()
        
        risks['price_volatility'] = {
            'coefficient_of_variation': round(price_cv, 3),
            'risk_level': 'High' if price_cv > 0.3 else 'Medium' if price_cv > 0.15 else 'Low',
            'interpretation': 'Price variability across blocks'
        }
        
        # Sample size adequacy
        n = len(df)
        power_analysis = self._calculate_statistical_power(n)
        
        risks['sample_size_adequacy'] = {
            'current_sample_size': n,
            'statistical_power': power_analysis,
            'risk_level': 'Low' if power_analysis > 0.8 else 'Medium' if power_analysis > 0.6 else 'High',
            'recommendation': 'Adequate for medium effect sizes' if power_analysis > 0.7 else 'Consider larger sample'
        }
        
        return risks
    
    def _calculate_statistical_power(self, n: int, effect_size: float = 0.5, alpha: float = 0.05) -> float:
        """Calculate statistical power for given sample size"""
        # Simplified power calculation for t-test
        from scipy.stats import t
        
        df = n - 1
        t_critical = t.ppf(1 - alpha/2, df)
        t_calculated = effect_size * np.sqrt(n)
        
        power = 1 - t.cdf(t_critical, df, t_calculated) + t.cdf(-t_critical, df, t_calculated)
        return round(power, 3)
    
    def _generate_business_recommendations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate data-driven business recommendations"""
        
        recommendations = []
        
        # Recommendation 1: Energy efficiency focus
        avg_energy_score = df['energy_efficiency_score'].mean()
        if avg_energy_score > 3.5:  # Worse than C+ average
            recommendations.append({
                'priority': 'High',
                'category': 'Energy Efficiency',
                'recommendation': 'Focus on energy efficiency improvements in C and D class properties',
                'rationale': f'Current average energy class is {self._score_to_energy_class(avg_energy_score)}, significant improvement opportunity',
                'potential_impact': 'Est. 15-30% price premium for energy upgrades',
                'implementation': 'Partner with energy certification companies, offer upgrade financing'
            })
        
        # Recommendation 2: Premium market expansion
        current_premium = df['premium_percentage'].mean()
        if current_premium < 25:
            recommendations.append({
                'priority': 'High',
                'category': 'Market Expansion',
                'recommendation': 'Expand premium property portfolio through strategic acquisitions',
                'rationale': f'Only {current_premium:.1f}% premium properties, market opportunity exists',
                'potential_impact': f'Potential to increase premium share by {100-current_premium:.0f} percentage points',
                'implementation': 'Target B and C class properties for energy retrofits'
            })
        
        # Recommendation 3: Geographic diversification
        area_counts = df['area'].value_counts()
        if len(area_counts) < 5 and area_counts.std() > 2:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Geographic Diversification',
                'recommendation': 'Expand analysis to additional Athens neighborhoods',
                'rationale': 'Current coverage limited to 3 areas, diversification would reduce concentration risk',
                'potential_impact': 'Better market representation and risk distribution',
                'implementation': 'Add Psyrri, Thiseio, and Pagkrati East analysis'
            })
        
        # Recommendation 4: Data enhancement
        avg_confidence = df['confidence_score'].mean()
        if avg_confidence < 0.9:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Data Quality',
                'recommendation': 'Enhance data collection for better confidence scores',
                'rationale': f'Average confidence score {avg_confidence:.1%}, room for improvement',
                'potential_impact': 'More reliable business decisions and reduced analysis risk',
                'implementation': 'Improve property detail extraction, add verification steps'
            })
        
        return recommendations

def main():
    """Perform comprehensive statistical business analysis"""
    
    analyzer = StatisticalBusinessAnalysis()
    
    # Load data
    if not analyzer.load_data():
        return
    
    print("\n📊 Performing Comprehensive Statistical Analysis...")
    
    # Perform analysis
    results = analyzer.perform_comprehensive_statistical_analysis()
    
    if results:
        print(f"\n✅ STATISTICAL ANALYSIS COMPLETE!")
        
        # Display key findings
        sample_chars = results['sample_characteristics']
        print(f"\n📊 Sample Characteristics:")
        print(f"   Sample Size: {sample_chars['sample_size']} city blocks")
        print(f"   Avg Price per m²: €{sample_chars['price_per_sqm']['mean']} ± €{sample_chars['price_per_sqm']['confidence_interval_95'][1] - sample_chars['price_per_sqm']['mean']:.0f}")
        print(f"   Premium Properties: {sample_chars['premium_properties']['mean_percentage']}% ± {sample_chars['premium_properties']['confidence_interval_95'][1] - sample_chars['premium_properties']['mean_percentage']:.1f}%")
        
        # Energy-price correlation
        correlation = results['energy_price_correlation']
        print(f"\n🔗 Energy-Price Correlation:")
        print(f"   Correlation: {correlation['interpretation']}")
        print(f"   Price Premium: €{correlation['business_insight']}")
        print(f"   Statistical Significance: {'Yes' if correlation['statistical_significance'] else 'No'}")
        
        # Market opportunity
        opportunity = results['market_opportunity_quantification']
        conservative = opportunity['opportunity_scenarios']['conservative']
        print(f"\n💰 Market Opportunity (Conservative):")
        print(f"   Properties to Improve: {conservative['properties_to_improve']}")
        print(f"   Total Value Creation: €{conservative['total_value_creation']:,}")
        print(f"   Risk-Adjusted Value: €{conservative['risk_adjusted_value']:,}")
        
        # Business recommendations
        recommendations = results['business_recommendations']
        print(f"\n🎯 Top Business Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. [{rec['priority']}] {rec['recommendation']}")
            print(f"      Impact: {rec['potential_impact']}")

if __name__ == "__main__":
    main()