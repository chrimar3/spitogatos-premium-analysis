#!/usr/bin/env python3
"""
City Block Analysis Generator
Generate realistic city blocks with multiple properties for building block analysis
Focus: sqm, energy class, and geographic clustering
"""

import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
import statistics

from utils import PropertyData, BuildingBlock, generate_property_id

@dataclass
class CityBlock:
    """Represents a city block (geographic area) with multiple properties"""
    id: str
    area_name: str
    block_boundaries: Dict[str, str]  # North, South, East, West streets
    center_lat: float
    center_lon: float
    properties: List[PropertyData]
    median_energy_class: str
    avg_sqm: float
    historical_data: List[Dict[str, Any]]
    
class CityBlockAnalysisGenerator:
    """Generate realistic city blocks for analysis"""
    
    def __init__(self):
        # Athens area coordinates and realistic city block data
        self.area_configs = {
            'Pangrati': {
                'center': (37.9652, 23.7415),
                'blocks': [
                    {'streets': {'north': 'Ymittou', 'south': 'Plastira', 'east': 'Archimidous', 'west': 'Damareos'}, 'premium': 1.0},
                    {'streets': {'north': 'Plastira', 'south': 'Formionos', 'east': 'Damareos', 'west': 'Spyrou Merkouri'}, 'premium': 1.1},
                    {'streets': {'north': 'Formionos', 'south': 'Eftichidou', 'east': 'Spyrou Merkouri', 'west': 'Erregentadon'}, 'premium': 0.9},
                    {'streets': {'north': 'Eftichidou', 'south': 'Konstantinou Palaiologou', 'east': 'Erregentadon', 'west': 'Praxitelous'}, 'premium': 1.0},
                    {'streets': {'north': 'Konstantinou Palaiologou', 'south': 'Artemidos', 'east': 'Praxitelous', 'west': 'Efroniou'}, 'premium': 0.95},
                ]
            },
            'Kolonaki': {
                'center': (37.9755, 23.7348),
                'blocks': [
                    {'streets': {'north': 'Voukourestiou', 'south': 'Skoufa', 'east': 'Anagnostopoulou', 'west': 'Patriarchou Ioakim'}, 'premium': 1.8},
                    {'streets': {'north': 'Skoufa', 'south': 'Dimokritou', 'east': 'Patriarchou Ioakim', 'west': 'Solonos'}, 'premium': 1.7},
                    {'streets': {'north': 'Dimokritou', 'south': 'Kleomenous', 'east': 'Solonos', 'west': 'Massalias'}, 'premium': 1.6},
                    {'streets': {'north': 'Kleomenous', 'south': 'Loukianou', 'east': 'Massalias', 'west': 'Koumbari'}, 'premium': 1.5},
                    {'streets': {'north': 'Loukianou', 'south': 'Plutarchou', 'east': 'Koumbari', 'west': 'Irodotou'}, 'premium': 1.4},
                ]
            },
            'Exarchia': {
                'center': (37.9838, 23.7335),
                'blocks': [
                    {'streets': {'north': 'Themistokleous', 'south': 'Kallidromiou', 'east': 'Solonos', 'west': 'Tositsa'}, 'premium': 1.0},
                    {'streets': {'north': 'Kallidromiou', 'south': 'Methonis', 'east': 'Tositsa', 'west': 'Emmanouil Benaki'}, 'premium': 0.9},
                    {'streets': {'north': 'Methonis', 'south': 'Messolongiou', 'east': 'Emmanouil Benaki', 'west': 'Didotou'}, 'premium': 1.1},
                    {'streets': {'north': 'Messolongiou', 'south': 'Zacharitsa', 'east': 'Didotou', 'west': 'Valtetsiou'}, 'premium': 0.95},
                    {'streets': {'north': 'Zacharitsa', 'south': 'Arachovis', 'east': 'Valtetsiou', 'west': 'Drossopoulou'}, 'premium': 1.0},
                ]
            },
            'Psyrri': {
                'center': (37.9758, 23.7255),
                'blocks': [
                    {'streets': {'north': 'Miaouli', 'south': 'Karaiskaki', 'east': 'Aristophanous', 'west': 'Lepeniotou'}, 'premium': 1.3},
                    {'streets': {'north': 'Karaiskaki', 'south': 'Agiou Dimitriou', 'east': 'Lepeniotou', 'west': 'Pittakou'}, 'premium': 1.2},
                    {'streets': {'north': 'Agiou Dimitriou', 'south': 'Sarri', 'east': 'Pittakou', 'west': 'Protogenous'}, 'premium': 1.4},
                    {'streets': {'north': 'Sarri', 'south': 'Agion Asomaton', 'east': 'Protogenous', 'west': 'Taki'}, 'premium': 1.1},
                    {'streets': {'north': 'Agion Asomaton', 'south': 'Kerameikou', 'east': 'Taki', 'west': 'Megalou Alexandrou'}, 'premium': 1.0},
                ]
            }
        }
        
        # Energy class distributions based on building age and area
        self.energy_distributions = {
            'new_building': ['A', 'A+', 'B+', 'B'],
            'renovated': ['B', 'B+', 'C+', 'C'],
            'standard': ['C', 'C+', 'D', 'D+'],
            'old': ['D', 'D+', 'E', 'F']
        }
        
        # Realistic apartment sizes by building type
        self.apartment_sizes = {
            'luxury': [80, 95, 110, 130, 150, 180, 220],
            'standard': [45, 55, 65, 75, 85, 95, 110],
            'compact': [35, 40, 45, 50, 55, 60, 70],
            'mixed': [40, 50, 60, 70, 80, 95, 110, 130]
        }
        
        logging.info("🏙️ City Block Analysis Generator initialized")
    
    def generate_city_blocks_for_area(self, area_name: str, num_blocks: int = 10) -> List[CityBlock]:
        """Generate complete city blocks for analysis"""
        
        logging.info(f"🏗️ Generating {num_blocks} city blocks for {area_name}")
        
        if area_name not in self.area_configs:
            area_name = 'Pangrati'  # Default fallback
        
        area_config = self.area_configs[area_name]
        city_blocks = []
        
        # Generate more blocks than available in config if needed
        available_blocks = area_config['blocks']
        
        for i in range(num_blocks):
            # Cycle through available block configs
            block_config = available_blocks[i % len(available_blocks)]
            
            # Generate unique block ID
            block_id = f"{area_name}_Block_{i+1:02d}"
            
            # Generate geographic center with variation
            base_lat, base_lon = area_config['center']
            # Add small geographic variation for each block
            lat_offset = random.uniform(-0.01, 0.01) + (i * 0.002)
            lon_offset = random.uniform(-0.01, 0.01) + (i * 0.002)
            
            center_lat = base_lat + lat_offset
            center_lon = base_lon + lon_offset
            
            # Generate properties for this city block
            properties = self._generate_properties_for_city_block(
                block_id, area_name, center_lat, center_lon, 
                block_config['premium']
            )
            
            # Calculate median energy class
            median_energy = self._calculate_median_energy_class(properties)
            
            # Calculate average sqm
            sqms = [p.sqm for p in properties if p.sqm]
            avg_sqm = statistics.mean(sqms) if sqms else 0
            
            # Generate historical data
            historical_data = self._generate_historical_data(properties)
            
            city_block = CityBlock(
                id=block_id,
                area_name=area_name,
                block_boundaries=block_config['streets'],
                center_lat=center_lat,
                center_lon=center_lon,
                properties=properties,
                median_energy_class=median_energy,
                avg_sqm=avg_sqm,
                historical_data=historical_data
            )
            
            city_blocks.append(city_block)
            
            logging.info(f"   ✅ {block_id}: {len(properties)} properties, median energy: {median_energy}")
        
        logging.info(f"🎉 Generated {len(city_blocks)} complete city blocks for {area_name}")
        return city_blocks
    
    def _generate_properties_for_city_block(self, block_id: str, area_name: str, 
                                          center_lat: float, center_lon: float, 
                                          premium_factor: float) -> List[PropertyData]:
        """Generate 15-30 properties within a city block"""
        
        # Random number of properties per city block
        num_properties = random.randint(15, 30)
        properties = []
        
        # Determine building types in this block
        building_types = self._determine_building_types_for_block(area_name, premium_factor)
        
        for i in range(num_properties):
            # Select building type for this property
            building_type = random.choice(building_types)
            
            # Generate realistic apartment size
            sqm = random.choice(self.apartment_sizes[building_type])
            sqm += random.randint(-5, 10)  # Add variation
            
            # Generate energy class based on building type
            energy_class = self._generate_energy_class_for_building_type(building_type)
            
            # Generate realistic address within the city block
            address = self._generate_address_in_city_block(area_name, block_id, i)
            
            # Generate property coordinates within city block (small area)
            lat = center_lat + random.uniform(-0.002, 0.002)
            lon = center_lon + random.uniform(-0.002, 0.002)
            
            # Generate realistic price based on sqm, energy, and area
            price = self._calculate_realistic_price(sqm, energy_class, area_name, premium_factor)
            
            # Generate property ID and URL
            property_url = f"https://www.spitogatos.gr/property/{block_id}_{i+1}"
            property_id = generate_property_id(property_url, address)
            
            # Generate other details
            floor = self._generate_realistic_floor()
            rooms = self._calculate_rooms_from_sqm(sqm)
            
            property_data = PropertyData(
                id=property_id,
                url=property_url,
                title=f"{sqm}τ.μ. διαμέρισμα - {area_name}",
                address=address,
                price=price,
                sqm=sqm,
                energy_class=energy_class,
                floor=floor,
                rooms=rooms,
                latitude=lat,
                longitude=lon,
                description=f"Διαμέρισμα {sqm}τ.μ. ενεργειακής κλάσης {energy_class}",
                images=[],
                scraped_at=datetime.now(),
                confidence_score=0.95,
                validation_flags=[]
            )
            
            properties.append(property_data)
        
        return properties
    
    def _determine_building_types_for_block(self, area_name: str, premium_factor: float) -> List[str]:
        """Determine realistic building types for a city block"""
        
        if area_name == 'Kolonaki' or premium_factor > 1.5:
            return ['luxury', 'luxury', 'standard', 'mixed']
        elif area_name == 'Exarchia':
            return ['standard', 'standard', 'compact', 'mixed']
        elif premium_factor > 1.2:
            return ['standard', 'standard', 'luxury', 'mixed']
        else:
            return ['standard', 'standard', 'compact', 'mixed']
    
    def _generate_energy_class_for_building_type(self, building_type: str) -> str:
        """Generate realistic energy class based on building type"""
        
        if building_type == 'luxury':
            # Luxury buildings tend to have better energy efficiency
            options = self.energy_distributions['new_building'] + self.energy_distributions['renovated']
        elif building_type == 'standard':
            options = self.energy_distributions['renovated'] + self.energy_distributions['standard']
        elif building_type == 'compact':
            # Compact apartments are often newer or renovated
            options = self.energy_distributions['renovated'] + self.energy_distributions['new_building']
        else:  # mixed
            # Mixed building types have varied energy classes
            all_classes = []
            for dist in self.energy_distributions.values():
                all_classes.extend(dist)
            options = all_classes
        
        return random.choice(options)
    
    def _generate_address_in_city_block(self, area_name: str, block_id: str, property_index: int) -> str:
        """Generate realistic address within city block"""
        
        # Get some street names for the area
        area_config = self.area_configs.get(area_name, self.area_configs['Pangrati'])
        
        # Pick a random street from one of the blocks
        block_config = random.choice(area_config['blocks'])
        street_name = random.choice(list(block_config['streets'].values()))
        
        # Generate building number
        building_number = random.randint(1, 150)
        
        # Some properties might be in the same building (different floors)
        if property_index > 0 and random.random() < 0.3:  # 30% chance same building
            # Use a previous building number occasionally
            building_number = random.randint(max(1, building_number - 20), building_number)
        
        return f"{street_name} {building_number}, {area_name}, Athens"
    
    def _calculate_realistic_price(self, sqm: int, energy_class: str, area_name: str, premium_factor: float) -> int:
        """Calculate realistic price based on sqm, energy class, and location"""
        
        # Base price per sqm by area
        base_prices = {
            'Kolonaki': 8000,
            'Pangrati': 4500,
            'Exarchia': 3500,
            'Psyrri': 5000
        }
        
        base_price_per_sqm = base_prices.get(area_name, 4000)
        
        # Energy class multiplier
        energy_multipliers = {
            'A+': 1.15, 'A': 1.10, 'B+': 1.05, 'B': 1.00,
            'C+': 0.95, 'C': 0.90, 'D+': 0.85, 'D': 0.80,
            'E': 0.75, 'F': 0.70
        }
        
        energy_mult = energy_multipliers.get(energy_class, 0.90)
        
        # Calculate total price
        total_price = sqm * base_price_per_sqm * premium_factor * energy_mult
        
        # Add realistic market variation
        variation = random.uniform(0.85, 1.15)
        total_price *= variation
        
        return int(total_price)
    
    def _generate_realistic_floor(self) -> int:
        """Generate realistic floor number"""
        # Greek buildings typically 1-6 floors
        return random.choices([1, 2, 3, 4, 5, 6], weights=[15, 20, 20, 20, 15, 10])[0]
    
    def _calculate_rooms_from_sqm(self, sqm: int) -> int:
        """Calculate realistic room count based on square meters"""
        if sqm < 50:
            return random.choice([1, 2])
        elif sqm < 75:
            return random.choice([2, 3])
        elif sqm < 100:
            return random.choice([2, 3, 4])
        elif sqm < 130:
            return random.choice([3, 4])
        else:
            return random.choice([4, 5])
    
    def _calculate_median_energy_class(self, properties: List[PropertyData]) -> str:
        """
        Calculate weighted median energy class for city block
        Method: Sum energy classes weighted by apartment square meters, then find median
        """
        
        if not properties:
            return 'C'
        
        # Convert energy classes to numeric values
        energy_values = {
            'A+': 10, 'A': 9, 'B+': 8, 'B': 7, 'C+': 6, 'C': 5,
            'D+': 4, 'D': 3, 'E': 2, 'F': 1
        }
        
        # Reverse mapping
        value_to_class = {v: k for k, v in energy_values.items()}
        
        # Create weighted values list: each apartment contributes its energy value * sqm times
        weighted_values = []
        
        for prop in properties:
            if prop.energy_class and prop.sqm:
                energy_numeric = energy_values.get(prop.energy_class, 5)
                # Add the energy value sqm times (weighted by square meters)
                weighted_values.extend([energy_numeric] * prop.sqm)
        
        if not weighted_values:
            return 'C'
        
        # Calculate median of the weighted values
        median_value = statistics.median(weighted_values)
        
        # Find closest energy class to the median value
        closest_value = min(value_to_class.keys(), key=lambda x: abs(x - median_value))
        
        return value_to_class[closest_value]
    
    def _generate_historical_data(self, properties: List[PropertyData]) -> List[Dict[str, Any]]:
        """Generate historical data for properties (simplified)"""
        
        historical_data = []
        
        # Generate historical snapshots (6 months ago, 1 year ago)
        for months_back in [6, 12]:
            historical_date = datetime.now() - timedelta(days=months_back * 30)
            
            # Historical prices were typically lower
            price_factor = 0.95 if months_back == 6 else 0.90
            
            historical_snapshot = {
                'date': historical_date.isoformat(),
                'months_back': months_back,
                'total_properties': len(properties),
                'avg_price_factor': price_factor,
                'energy_improvement': random.choice([True, False])  # Some buildings improved energy rating
            }
            
            historical_data.append(historical_snapshot)
        
        return historical_data
    
    def save_city_blocks_analysis(self, city_blocks: List[CityBlock], filename: str) -> None:
        """Save city blocks analysis to file"""
        
        analysis_data = {
            'analysis_date': datetime.now().isoformat(),
            'total_city_blocks': len(city_blocks),
            'city_blocks': []
        }
        
        for block in city_blocks:
            block_data = {
                'id': block.id,
                'area_name': block.area_name,
                'block_boundaries': block.block_boundaries,
                'center_coordinates': {'lat': block.center_lat, 'lon': block.center_lon},
                'median_energy_class': block.median_energy_class,
                'avg_sqm': block.avg_sqm,
                'total_properties': len(block.properties),
                'energy_class_distribution': self._get_energy_distribution(block.properties),
                'sqm_distribution': self._get_sqm_distribution(block.properties),
                'price_statistics': self._get_price_statistics(block.properties),
                'historical_data': block.historical_data,
                'properties': [
                    {
                        'id': p.id,
                        'address': p.address,
                        'sqm': p.sqm,
                        'energy_class': p.energy_class,
                        'price': p.price,
                        'floor': p.floor,
                        'rooms': p.rooms,
                        'coordinates': {'lat': p.latitude, 'lon': p.longitude}
                    }
                    for p in block.properties
                ]
            }
            
            analysis_data['city_blocks'].append(block_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"💾 City blocks analysis saved to {filename}")
    
    def _get_energy_distribution(self, properties: List[PropertyData]) -> Dict[str, int]:
        """Get energy class distribution for properties"""
        distribution = {}
        for prop in properties:
            if prop.energy_class:
                distribution[prop.energy_class] = distribution.get(prop.energy_class, 0) + 1
        return distribution
    
    def _get_sqm_distribution(self, properties: List[PropertyData]) -> Dict[str, Any]:
        """Get sqm distribution statistics"""
        sqms = [p.sqm for p in properties if p.sqm]
        if not sqms:
            return {}
        
        return {
            'min': min(sqms),
            'max': max(sqms),
            'avg': statistics.mean(sqms),
            'median': statistics.median(sqms)
        }
    
    def _get_price_statistics(self, properties: List[PropertyData]) -> Dict[str, Any]:
        """Get price statistics"""
        prices = [p.price for p in properties if p.price]
        if not prices:
            return {}
        
        return {
            'min': min(prices),
            'max': max(prices),
            'avg': statistics.mean(prices),
            'median': statistics.median(prices)
        }

def main():
    """Test the city block generator"""
    
    print("🏙️ CITY BLOCK ANALYSIS GENERATOR")
    print("=" * 60)
    
    generator = CityBlockAnalysisGenerator()
    
    # Test areas
    areas = ['Pangrati', 'Kolonaki']
    
    for area in areas:
        print(f"\n🏗️ Generating city blocks for {area}")
        print("-" * 40)
        
        city_blocks = generator.generate_city_blocks_for_area(area, num_blocks=10)
        
        print(f"✅ Generated {len(city_blocks)} city blocks")
        
        # Show summary
        total_properties = sum(len(block.properties) for block in city_blocks)
        print(f"📊 Total properties: {total_properties}")
        
        # Show sample city block details
        if city_blocks:
            sample_block = city_blocks[0]
            print(f"\n🏢 Sample City Block: {sample_block.id}")
            print(f"   📍 Boundaries: {sample_block.block_boundaries}")
            print(f"   🏠 Properties: {len(sample_block.properties)}")
            print(f"   ⚡ Median Energy Class: {sample_block.median_energy_class}")
            print(f"   📐 Average sqm: {sample_block.avg_sqm:.1f}")
            
            # Sample properties
            print(f"   🏘️ Sample Properties:")
            for i, prop in enumerate(sample_block.properties[:3]):
                print(f"     {i+1}. {prop.sqm}m² - {prop.energy_class} - €{prop.price:,}")
        
        # Save analysis
        filename = f"outputs/city_blocks_analysis_{area.lower()}.json"
        generator.save_city_blocks_analysis(city_blocks, filename)

if __name__ == "__main__":
    main()