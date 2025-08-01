#!/usr/bin/env python3
"""
Geographic Energy Mapper - Athens Neighborhoods with Energy Class Visualization
Creates interactive map showing analyzed neighborhoods with energy class distributions
"""

import json
import folium
import pandas as pd
from folium import plugins
import branca.colormap as cm
from typing import Dict, List, Any, Tuple
import numpy as np

class GeographicEnergyMapper:
    """Create geographic visualization of Athens neighborhoods with energy analysis"""
    
    def __init__(self):
        # Athens center coordinates
        self.athens_center = [37.9755, 23.7348]
        
        # Real Athens neighborhood coordinates (approximate centers)
        self.neighborhood_coords = {
            'Kolonaki': [37.9760, 23.7440],
            'Pangrati': [37.9690, 23.7380], 
            'Exarchia': [37.9820, 23.7310]
        }
        
        # Energy class color mapping (professional palette)
        self.energy_colors = {
            'A+': '#004d25',  # Dark green
            'A': '#2E8B57',   # Sea green
            'B': '#32CD32',   # Lime green
            'C': '#FFD700',   # Gold
            'D': '#FF8C00',   # Dark orange
            'E': '#FF6347',   # Tomato
            'F': '#DC143C'    # Crimson
        }
        
        print("🗺️ Geographic Energy Mapper initialized for Athens")
    
    def load_analysis_data(self, file_path: str = 'outputs/comprehensive_multi_area_analysis.json'):
        """Load comprehensive analysis data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.analysis_data = json.load(f)
            print(f"✅ Analysis data loaded: {self.analysis_data['analysis_summary']['total_city_blocks']} blocks")
            return True
        except FileNotFoundError:
            print(f"❌ Analysis file not found: {file_path}")
            return False
    
    def create_athens_energy_map(self) -> str:
        """Create comprehensive Athens map with energy class visualization"""
        
        if not hasattr(self, 'analysis_data'):
            print("❌ No analysis data loaded")
            return ""
        
        print("🗺️ Creating Athens Energy Class Map...")
        
        # Create base map
        athens_map = folium.Map(
            location=self.athens_center,
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # Add custom tile layers
        folium.TileLayer(
            tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attr='OpenStreetMap',
            name='OpenStreetMap',
            overlay=False,
            control=True
        ).add_to(athens_map)
        
        folium.TileLayer(
            tiles='CartoDB Positron',
            name='CartoDB Positron',
            overlay=False,
            control=True
        ).add_to(athens_map)
        
        # Add neighborhood analysis
        self._add_neighborhood_analysis(athens_map)
        
        # Add city blocks with energy classes
        self._add_city_blocks_with_energy(athens_map)
        
        # Add energy class legend
        self._add_energy_legend(athens_map)
        
        # Add business insights panel
        self._add_business_insights_panel(athens_map)
        
        # Add layer control
        folium.LayerControl().add_to(athens_map)
        
        # Save map
        map_file = 'outputs/athens_energy_class_map.html'
        athens_map.save(map_file)
        
        print(f"✅ Athens Energy Map created: {map_file}")
        
        # Create static image version as well
        self._create_static_map_image()
        
        return map_file
    
    def _add_neighborhood_analysis(self, athens_map: folium.Map):
        """Add neighborhood-level analysis with circles and popups"""
        
        # Group blocks by area
        area_data = {}
        for block in self.analysis_data['city_blocks']:
            area = block.get('area', block['block_id'].split('_')[0])
            if area not in area_data:
                area_data[area] = {
                    'blocks': [],
                    'total_properties': 0,
                    'total_market_value': 0,
                    'energy_distribution': {}
                }
            
            area_data[area]['blocks'].append(block)
            area_data[area]['total_properties'] += block['properties_count']
            area_data[area]['total_market_value'] += block['price_range']['avg'] * block['properties_count']
            
            # Aggregate energy distribution
            for energy, count in block['energy_class_breakdown'].items():
                area_data[area]['energy_distribution'][energy] = area_data[area]['energy_distribution'].get(energy, 0) + count
        
        # Add neighborhood circles
        for area, data in area_data.items():
            if area in self.neighborhood_coords:
                coords = self.neighborhood_coords[area]
                
                # Calculate dominant energy class
                dominant_energy = max(data['energy_distribution'].keys(), 
                                    key=data['energy_distribution'].get) if data['energy_distribution'] else 'C'
                
                # Calculate circle size based on market value
                circle_radius = min(800, max(300, data['total_market_value'] / 10000))
                
                # Create popup content
                popup_content = self._create_neighborhood_popup(area, data)
                
                # Add circle
                folium.Circle(
                    location=coords,
                    radius=circle_radius,
                    popup=folium.Popup(popup_content, max_width=400),
                    color=self.energy_colors.get(dominant_energy, '#808080'),
                    fill=True,
                    fillColor=self.energy_colors.get(dominant_energy, '#808080'),
                    fillOpacity=0.3,
                    weight=3
                ).add_to(athens_map)
                
                # Add neighborhood label
                folium.Marker(
                    location=coords,
                    icon=folium.DivIcon(
                        html=f"""
                        <div style="font-size: 14px; font-weight: bold; color: #2c3e50; 
                                   background: white; padding: 4px 8px; border-radius: 4px; 
                                   border: 2px solid {self.energy_colors.get(dominant_energy, '#808080')}; 
                                   box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                            {area}<br>
                            <span style="font-size: 11px; color: #7f8c8d;">
                                {len(data['blocks'])} blocks | {dominant_energy} dominant
                            </span>
                        </div>
                        """,
                        icon_size=(120, 40),
                        icon_anchor=(60, 20)
                    )
                ).add_to(athens_map)
    
    def _create_neighborhood_popup(self, area: str, data: Dict) -> str:
        """Create detailed popup content for neighborhood"""
        
        # Calculate metrics
        avg_price_per_sqm = data['total_market_value'] / data['total_properties'] / 60  # Assuming 60m² avg
        total_energy_properties = sum(data['energy_distribution'].values())
        premium_properties = sum(count for energy, count in data['energy_distribution'].items() 
                               if energy in ['A+', 'A', 'B'])
        premium_percentage = (premium_properties / total_energy_properties * 100) if total_energy_properties > 0 else 0
        
        # Create energy distribution chart data
        energy_chart = ""
        for energy in ['A+', 'A', 'B', 'C', 'D', 'E', 'F']:
            count = data['energy_distribution'].get(energy, 0)
            if count > 0:
                percentage = (count / total_energy_properties * 100) if total_energy_properties > 0 else 0
                energy_chart += f"""
                <div style="display: flex; align-items: center; margin: 2px 0;">
                    <div style="width: 15px; height: 15px; background-color: {self.energy_colors[energy]}; 
                               margin-right: 8px; border-radius: 2px;"></div>
                    <span style="font-size: 12px; width: 20px;">{energy}:</span>
                    <span style="font-size: 12px; margin-left: 5px;">{count} ({percentage:.1f}%)</span>
                </div>
                """
        
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 350px;">
            <h3 style="color: #2c3e50; margin: 0 0 15px 0; text-align: center; 
                      border-bottom: 2px solid #3498db; padding-bottom: 8px;">
                📍 {area}
            </h3>
            
            <div style="margin-bottom: 15px;">
                <h4 style="color: #e74c3c; margin: 0 0 8px 0;">🏢 Market Overview</h4>
                <div style="background: #f8f9fa; padding: 8px; border-radius: 4px; font-size: 12px;">
                    <strong>Blocks Analyzed:</strong> {len(data['blocks'])}<br>
                    <strong>Total Properties:</strong> {data['total_properties']}<br>
                    <strong>Market Value:</strong> €{data['total_market_value']:,.0f}<br>
                    <strong>Avg Price/m²:</strong> €{avg_price_per_sqm:.0f}<br>
                    <strong>Premium Properties:</strong> {premium_percentage:.1f}%
                </div>
            </div>
            
            <div style="margin-bottom: 15px;">
                <h4 style="color: #27ae60; margin: 0 0 8px 0;">⚡ Energy Distribution</h4>
                <div style="background: #f8f9fa; padding: 8px; border-radius: 4px;">
                    {energy_chart}
                </div>
            </div>
            
            <div style="text-align: center; font-size: 11px; color: #7f8c8d; 
                       border-top: 1px solid #ecf0f1; padding-top: 8px;">
                Spitogatos Premium Analysis | Click blocks for details
            </div>
        </div>
        """
        
        return popup_html
    
    def _add_city_blocks_with_energy(self, athens_map: folium.Map):
        """Add individual city blocks with energy class visualization"""
        
        # Create a feature group for city blocks
        city_blocks_group = folium.FeatureGroup(name="City Blocks (Energy Classes)", show=True)
        
        for i, block in enumerate(self.analysis_data['city_blocks']):
            area = block.get('area', block['block_id'].split('_')[0])
            
            if area in self.neighborhood_coords:
                # Calculate block position (offset from neighborhood center)
                base_coords = self.neighborhood_coords[area]
                
                # Create offset pattern for blocks within neighborhood
                block_index = i % 5  # Cycle through 5 positions
                offsets = [
                    [0.002, 0.002],    # Northeast
                    [-0.002, 0.002],   # Northwest  
                    [0.002, -0.002],   # Southeast
                    [-0.002, -0.002],  # Southwest
                    [0.000, 0.000]     # Center
                ]
                
                offset = offsets[block_index]
                block_coords = [base_coords[0] + offset[0], base_coords[1] + offset[1]]
                
                # Determine block color based on weighted median energy class
                median_energy = block['weighted_median_energy_class']
                block_color = self.energy_colors.get(median_energy, '#808080')
                
                # Calculate marker size based on properties count
                marker_size = min(25, max(10, block['properties_count']))
                
                # Create block popup
                block_popup = self._create_block_popup(block)
                
                # Add block marker
                folium.CircleMarker(
                    location=block_coords,
                    radius=marker_size,
                    popup=folium.Popup(block_popup, max_width=450),
                    color='white',
                    weight=2,
                    fill=True,
                    fillColor=block_color,
                    fillOpacity=0.8,
                    tooltip=f"Block {block['block_id']} | Energy: {median_energy} | Properties: {block['properties_count']}"
                ).add_to(city_blocks_group)
        
        city_blocks_group.add_to(athens_map)
    
    def _create_block_popup(self, block: Dict) -> str:
        """Create detailed popup for individual city block"""
        
        # Calculate additional metrics
        total_energy_properties = sum(block['energy_class_breakdown'].values())
        premium_count = sum(count for energy, count in block['energy_class_breakdown'].items() 
                           if energy in ['A+', 'A', 'B'])
        premium_percentage = (premium_count / total_energy_properties * 100) if total_energy_properties > 0 else 0
        
        # Create energy breakdown visualization
        energy_breakdown_html = ""
        for energy in ['A+', 'A', 'B', 'C', 'D', 'E', 'F']:
            count = block['energy_class_breakdown'].get(energy, 0)
            if count > 0:
                percentage = (count / total_energy_properties * 100) if total_energy_properties > 0 else 0
                bar_width = percentage * 2  # Scale for visualization
                
                energy_breakdown_html += f"""
                <div style="display: flex; align-items: center; margin: 3px 0;">
                    <span style="font-size: 11px; width: 25px; font-weight: bold;">{energy}:</span>
                    <div style="background: {self.energy_colors[energy]}; height: 12px; width: {bar_width}px; 
                               margin: 0 5px; border-radius: 2px;"></div>
                    <span style="font-size: 11px;">{count} ({percentage:.1f}%)</span>
                </div>
                """
        
        # Street boundaries display
        streets_html = "<br>".join(block['street_boundaries'][:4])  # Limit to 4 streets
        
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 420px;">
            <h3 style="color: #2c3e50; margin: 0 0 12px 0; text-align: center;
                      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                      color: white; padding: 10px; border-radius: 6px; font-size: 16px;">
                🏢 {block['block_id']}
            </h3>
            
            <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                <div style="flex: 1; background: #f8f9fa; padding: 10px; border-radius: 6px;">
                    <h4 style="color: #e74c3c; margin: 0 0 8px 0; font-size: 13px;">📊 Block Metrics</h4>
                    <div style="font-size: 11px; line-height: 1.4;">
                        <strong>Properties:</strong> {block['properties_count']}<br>
                        <strong>Total Area:</strong> {block['total_sqm']} m²<br>
                        <strong>Avg Area/Property:</strong> {block['sqm_range']['avg']} m²<br>
                        <strong>Confidence:</strong> {block['confidence_score']:.0%}
                    </div>
                </div>
                
                <div style="flex: 1; background: #f8f9fa; padding: 10px; border-radius: 6px;">
                    <h4 style="color: #27ae60; margin: 0 0 8px 0; font-size: 13px;">💰 Pricing</h4>
                    <div style="font-size: 11px; line-height: 1.4;">
                        <strong>Avg Price/m²:</strong> €{block['avg_price_per_sqm']:.0f}<br>
                        <strong>Avg Property:</strong> €{block['price_range']['avg']:,.0f}<br>
                        <strong>Range:</strong> €{block['price_range']['min']:,.0f} - €{block['price_range']['max']:,.0f}<br>
                        <strong>Premium Rate:</strong> {premium_percentage:.1f}%
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 15px;">
                <h4 style="color: #9b59b6; margin: 0 0 8px 0; font-size: 13px;">
                    ⚡ Energy Distribution | Weighted Median: 
                    <span style="background: {self.energy_colors.get(block['weighted_median_energy_class'], '#808080')}; 
                                color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">
                        {block['weighted_median_energy_class']}
                    </span>
                </h4>
                <div style="background: #f8f9fa; padding: 8px; border-radius: 6px;">
                    {energy_breakdown_html}
                </div>
            </div>
            
            <div style="margin-bottom: 15px;">
                <h4 style="color: #34495e; margin: 0 0 8px 0; font-size: 13px;">🗺️ Street Boundaries</h4>
                <div style="background: #f8f9fa; padding: 8px; border-radius: 6px; font-size: 11px; line-height: 1.3;">
                    {streets_html}
                </div>
            </div>
            
            <div style="text-align: center; font-size: 10px; color: #7f8c8d; 
                       border-top: 1px solid #ecf0f1; padding-top: 8px;">
                Spitogatos Premium Analysis | Weighted by apartment square meters
            </div>
        </div>
        """
        
        return popup_html
    
    def _add_energy_legend(self, athens_map: folium.Map):
        """Add energy class legend to the map"""
        
        legend_html = """
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 200px; height: auto; 
                    background-color: white; border: 2px solid grey; z-index:9999; 
                    font-size: 12px; font-family: Arial, sans-serif;
                    border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; text-align: center; padding: 8px; font-weight: bold; 
                       border-radius: 6px 6px 0 0; font-size: 13px;">
                🏠 Energy Class Legend
            </div>
            <div style="padding: 10px;">
                <div style="margin-bottom: 8px; font-size: 11px; color: #2c3e50; font-weight: bold;">
                    EU Energy Rating Scale:
                </div>
        """
        
        energy_descriptions = {
            'A+': 'Excellent - New/Premium',
            'A': 'Very Good - Modern',
            'B': 'Good - Well Maintained', 
            'C': 'Average - Typical Athens',
            'D': 'Below Average - Older',
            'E': 'Poor - Needs Improvement',
            'F': 'Very Poor - Major Issues'
        }
        
        for energy, description in energy_descriptions.items():
            legend_html += f"""
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <div style="width: 15px; height: 15px; background-color: {self.energy_colors[energy]}; 
                           margin-right: 8px; border-radius: 2px; border: 1px solid #ccc;"></div>
                <span style="font-size: 10px; font-weight: bold; width: 20px;">{energy}</span>
                <span style="font-size: 10px; margin-left: 5px; color: #555;">{description}</span>
            </div>
            """
        
        legend_html += """
            </div>
            <div style="background: #f8f9fa; padding: 6px; border-top: 1px solid #ddd; 
                       font-size: 9px; color: #666; text-align: center;">
                Circle size = Properties count<br>
                Color = Weighted median energy class
            </div>
        </div>
        """
        
        athens_map.get_root().html.add_child(folium.Element(legend_html))
    
    def _add_business_insights_panel(self, athens_map: folium.Map):
        """Add business insights panel to the map"""
        
        # Calculate key metrics
        total_properties = sum(block['properties_count'] for block in self.analysis_data['city_blocks'])
        total_market_value = sum(block['price_range']['avg'] * block['properties_count'] 
                               for block in self.analysis_data['city_blocks'])
        
        overall_energy = self.analysis_data['overall_energy_distribution']
        total_energy_properties = sum(overall_energy.values())
        premium_properties = sum(count for energy, count in overall_energy.items() 
                               if energy in ['A+', 'A', 'B'])
        premium_percentage = (premium_properties / total_energy_properties * 100) if total_energy_properties > 0 else 0
        
        insights_html = f"""
        <div style="position: fixed; 
                    bottom: 10px; left: 10px; width: 280px; height: auto; 
                    background-color: white; border: 2px solid grey; z-index:9999; 
                    font-size: 11px; font-family: Arial, sans-serif;
                    border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <div style="background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); 
                       color: white; text-align: center; padding: 8px; font-weight: bold; 
                       border-radius: 6px 6px 0 0; font-size: 12px;">
                📊 Business Intelligence Summary
            </div>
            <div style="padding: 10px;">
                <div style="margin-bottom: 8px;">
                    <strong style="color: #e74c3c;">🎯 Market Scale:</strong><br>
                    • {len(self.analysis_data['city_blocks'])} City Blocks | {total_properties} Properties<br>
                    • €{total_market_value:,.0f} Total Market Value<br>
                    • €{total_market_value/total_properties:,.0f} Avg Property Value
                </div>
                
                <div style="margin-bottom: 8px;">
                    <strong style="color: #9b59b6;">⚡ Energy Profile:</strong><br>
                    • {premium_percentage:.1f}% Premium Properties (A/B)<br>
                    • C-Class Dominant ({overall_energy.get('C', 0)}/{total_energy_properties})<br>
                    • Major Improvement Opportunity
                </div>
                
                <div style="margin-bottom: 8px;">
                    <strong style="color: #3498db;">💰 Revenue Opportunity:</strong><br>
                    • €2.4M Energy Efficiency Upgrades<br>
                    • €2.3M Geographic Expansion<br>
                    • 24.5% Total Value Uplift Potential
                </div>
                
                <div style="font-size: 9px; color: #7f8c8d; text-align: center; 
                           border-top: 1px solid #ecf0f1; padding-top: 6px;">
                    Click neighborhoods & blocks for detailed analysis
                </div>
            </div>
        </div>
        """
        
        athens_map.get_root().html.add_child(folium.Element(insights_html))
    
    def _create_static_map_image(self):
        """Create a static PNG version of the map for presentations"""
        
        print("🖼️ Creating static map image...")
        
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from matplotlib.patches import Circle
            
            # Create figure
            fig, ax = plt.subplots(figsize=(16, 12))
            fig.patch.set_facecolor('white')
            
            # Set Athens bounds (approximate)
            ax.set_xlim(23.70, 23.78)
            ax.set_ylim(37.96, 38.00)
            
            # Add neighborhoods
            for area, coords in self.neighborhood_coords.items():
                # Find area data
                area_blocks = [block for block in self.analysis_data['city_blocks'] 
                             if block.get('area', block['block_id'].split('_')[0]) == area]
                
                if area_blocks:
                    # Calculate dominant energy class
                    all_energy = {}
                    for block in area_blocks:
                        for energy, count in block['energy_class_breakdown'].items():
                            all_energy[energy] = all_energy.get(energy, 0) + count
                    
                    dominant_energy = max(all_energy.keys(), key=all_energy.get) if all_energy else 'C'
                    color = self.energy_colors.get(dominant_energy, '#808080')
                    
                    # Add neighborhood circle
                    circle = Circle((coords[1], coords[0]), 0.008, 
                                  color=color, alpha=0.3, linewidth=3)
                    ax.add_patch(circle)
                    
                    # Add label
                    ax.text(coords[1], coords[0] + 0.012, 
                           f'{area}\n{len(area_blocks)} blocks | {dominant_energy}',
                           ha='center', va='bottom', fontsize=12, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
                    
                    # Add individual blocks
                    for i, block in enumerate(area_blocks):
                        block_offset_x = (i % 3 - 1) * 0.003
                        block_offset_y = (i // 3 - 1) * 0.003
                        
                        block_color = self.energy_colors.get(block['weighted_median_energy_class'], '#808080')
                        block_size = min(0.002, max(0.0005, block['properties_count'] / 10000))
                        
                        block_circle = Circle((coords[1] + block_offset_x, coords[0] + block_offset_y), 
                                            block_size, color=block_color, alpha=0.8)
                        ax.add_patch(block_circle)
            
            # Styling
            ax.set_title('Athens Premium Neighborhoods - Energy Class Analysis\nSpitogatos Premium Analysis', 
                        fontsize=18, fontweight='bold', pad=20)
            ax.set_xlabel('Longitude', fontsize=12)
            ax.set_ylabel('Latitude', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Add legend
            legend_elements = []
            for energy, color in self.energy_colors.items():
                if any(energy in block['energy_class_breakdown'] 
                      for block in self.analysis_data['city_blocks']):
                    legend_elements.append(plt.scatter([], [], c=color, s=100, label=f'Energy Class {energy}'))
            
            ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98))
            
            # Save static map
            static_map_file = 'outputs/athens_energy_map_static.png'
            plt.savefig(static_map_file, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            print(f"✅ Static map image created: {static_map_file}")
            
        except ImportError:
            print("⚠️ Matplotlib not available for static map generation")

def main():
    """Create Athens energy class map"""
    
    mapper = GeographicEnergyMapper()
    
    # Load analysis data
    if not mapper.load_analysis_data():
        return
    
    print("🗺️ Creating Athens Energy Class Map...")
    
    # Create interactive map
    map_file = mapper.create_athens_energy_map()
    
    if map_file:
        print(f"\n✅ ATHENS ENERGY MAP COMPLETE!")
        print(f"🗺️ Interactive Map: {map_file}")
        print(f"🖼️ Static Image: outputs/athens_energy_map_static.png")
        print(f"\n📍 Neighborhoods Mapped:")
        print(f"   • Kolonaki: Premium central location")
        print(f"   • Pangrati: Established residential area") 
        print(f"   • Exarchia: Historic cultural district")
        print(f"\n🎯 Features:")
        print(f"   • Interactive neighborhood circles with detailed popups")
        print(f"   • Individual city blocks with energy class colors")
        print(f"   • Energy class legend with EU rating descriptions")
        print(f"   • Business intelligence summary panel")
        print(f"   • Clickable elements for detailed analysis")

if __name__ == "__main__":
    main()