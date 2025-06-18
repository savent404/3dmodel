#!/usr/bin/env python3
"""
NACA 4-digit airfoil example demonstrating wing design capabilities.
This example shows how to create airfoil sections that can be used to build wing structures.
"""

import sys
import os
# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_trimesh import BackendTrimesh
from models import ModelNACA4
from operations import ModelRigidTransform


def basic_naca4_example():
    """Basic example of creating NACA 4-digit airfoils."""
    print("=== NACA 4-Digit Airfoil Example ===\n")
    
    # Create backend
    backend = BackendTrimesh("naca4_example")
    
    print("Creating NACA airfoil sections...")
    print("Airfoils oriented with:")
    print("  - Chord direction: X-axis (airfoil points along X-axis)")
    print("  - Span direction: Y-axis (stackable along Y-axis)")
    print("  - Thickness direction: Z-axis (airfoil thickness along Z-axis)")
    print("  - Section normal: Y-axis direction")
    
    # Create different NACA airfoils for demonstration
    naca_tool = ModelNACA4()
    
    # NACA 0012 - Symmetric airfoil (common for vertical stabilizers)
    naca_0012 = naca_tool.call(
        name="NACA_0012",
        naca_digits="0012",
        chord_length=1.0,
        thickness=0.02,
        coord_x=0, coord_y=0, coord_z=0
    )
    
    # NACA 2412 - Cambered airfoil (common for main wings)
    # Positioned 2 units along Y-axis (span direction)
    naca_2412 = naca_tool.call(
        name="NACA_2412", 
        naca_digits="2412",
        chord_length=1.2,
        thickness=0.02,
        coord_x=0, coord_y=2, coord_z=0    )
    
    # NACA 4412 - Higher camber airfoil (for high lift)
    # Positioned 4 units along Y-axis (span direction)
    naca_4412 = naca_tool.call(
        name="NACA_4412",
        naca_digits="4412", 
        chord_length=0.8,
        thickness=0.02,
        coord_x=0, coord_y=4, coord_z=0
    )
    
    airfoils = [naca_0012, naca_2412, naca_4412]
    
    print(f"Created {len(airfoils)} airfoil sections:")
    for airfoil in airfoils:
        naca = airfoil.model_data['naca_digits']
        chord = airfoil.model_data['chord_length']
        camber = airfoil.model_data['max_camber']
        thickness_ratio = airfoil.model_data['thickness_ratio']
        print(f"  - {airfoil.name}: NACA {naca}, chord={chord:.2f}, camber={camber:.1%}, thickness={thickness_ratio:.1%}")
    
    # Render the airfoils
    print("\nRendering airfoils...")
    try:
        result = backend.render(airfoils)
        print(f"✓ {result}")
    except Exception as e:
        print(f"⚠ Rendering note: {e}")
    
    # Export example
    print("\nExporting airfoils...")
    try:
        backend.export_scene("naca_airfoils.stl", "stl")
        print("✓ Exported to naca_airfoils.stl")
    except Exception as e:
        print(f"⚠ Export note: {e}")


def wing_construction_example():
    """Example showing how to use airfoils to construct a wing."""
    print("\n=== Wing Construction Example ===\n")
    
    backend = BackendTrimesh("wing_construction")
    naca_tool = ModelNACA4()
    
    print("Creating wing sections at different spans...")
    print("Wing orientation:")
    print("  - Chord direction: X-axis (airfoil points along X-axis)")
    print("  - Span direction: Y-axis (wing spread direction)")
    print("  - Thickness direction: Z-axis (up/down)")
    print("  - Section normal: Y-axis direction")
    
    wing_sections = []
    
    # Root section (largest, at wing root)
    root_section = naca_tool.call(
        name="Wing_Root",
        naca_digits="2412", 
        chord_length=1.5,
        thickness=0.05,
        coord_x=0, coord_y=0, coord_z=0
    )
    wing_sections.append(root_section)
      # Mid sections (tapering)
    for i in range(1, 4):
        span_position = i * 1.0  # 1 meter apart along Y-axis (wing span)
        chord_taper = 1.5 - (i * 0.3)  # Taper from 1.5 to 0.6
        
        section = naca_tool.call(
            name=f"Wing_Section_{i}",
            naca_digits="2412",
            chord_length=chord_taper,
            thickness=0.05,
            coord_x=0, coord_y=span_position, coord_z=0
        )
        wing_sections.append(section)
    
    # Tip section (smallest)
    tip_section = naca_tool.call(
        name="Wing_Tip",
        naca_digits="2412",
        chord_length=0.6, 
        thickness=0.05,
        coord_x=0, coord_y=4.0, coord_z=0
    )
    wing_sections.append(tip_section)
    
    print(f"Created {len(wing_sections)} wing sections:")
    for section in wing_sections:
        chord = section.model_data['chord_length']
        y_pos = section.coord_y
        print(f"  - {section.name}: chord={chord:.2f}m at span y={y_pos:.1f}m")
    
    # Render the wing
    print("\nRendering wing structure...")
    try:
        result = backend.render(wing_sections)
        print(f"✓ {result}")
    except Exception as e:
        print(f"⚠ Rendering note: {e}")
    
    # Export wing
    print("\nExporting wing structure...")
    try:
        backend.export_scene("wing_structure.stl", "stl")
        print("✓ Exported to wing_structure.stl")
    except Exception as e:
        print(f"⚠ Export note: {e}")


def naca_theory_info():
    """Display information about NACA 4-digit designation."""
    print("\n=== NACA 4-Digit Airfoil Theory ===\n")
    
    print("NACA 4-digit designation format: MPXX")
    print("  M = Maximum camber as % of chord (first digit)")
    print("  P = Position of max camber as % of chord (second digit)")
    print("  XX = Maximum thickness as % of chord (last two digits)")
    print()
    print("Examples:")
    print("  NACA 0012: Symmetric, 12% thickness")
    print("  NACA 2412: 2% camber at 40% chord, 12% thickness")
    print("  NACA 4412: 4% camber at 40% chord, 12% thickness")
    print()
    print("Applications:")
    print("  - Symmetric airfoils (0XXX): Vertical stabilizers, control surfaces")
    print("  - Low camber (1XXX-2XXX): General aviation, efficient cruise")
    print("  - High camber (3XXX-4XXX): High lift applications, aerobatic aircraft")
    print()
    print("Wing Construction Workflow:")
    print("  1. Create airfoil sections at different span positions (along Y-axis)")
    print("  2. Airfoils automatically oriented with chord along X-axis")
    print("  3. Use different chord lengths for wing taper")
    print("  4. Apply twist (orientation changes) as needed for aerodynamics")
    print("  5. Connect sections to form complete wing structure")
    print()
    print("Coordinate System for Wings:")
    print("  - X-axis: Chord direction (leading edge to trailing edge)")
    print("  - Y-axis: Span direction (wing tip to wing tip)")
    print("  - Z-axis: Thickness direction (bottom to top of airfoil)")


if __name__ == "__main__":
    basic_naca4_example()
    wing_construction_example()
    naca_theory_info()
