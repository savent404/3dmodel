#!/usr/bin/env python3
"""
Verification script to demonstrate the corrected NACA4 airfoil orientation.
This shows that airfoils now point along X-axis and stack along Y-axis.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend_trimesh import BackendTrimesh
from models import ModelNACA4
import trimesh


def verify_naca4_orientation():
    """Verify that NACA4 airfoils are correctly oriented."""
    print("=== NACA4 Airfoil Orientation Verification ===\n")
    
    backend = BackendTrimesh("orientation_test")
    naca_tool = ModelNACA4()
    
    # Create multiple NACA airfoils at different Y positions (span direction)
    airfoils = []
    
    print("Creating NACA airfoil sections with correct orientation:")
    print("  - X-axis: Chord direction (leading edge to trailing edge)")
    print("  - Y-axis: Span direction (wing spread)")
    print("  - Z-axis: Thickness direction (bottom to top)")
    print()
    
    # Root section at Y=0
    root = naca_tool.call(
        name="Root_Section",
        naca_digits="2412",
        chord_length=1.0,
        thickness=0.02,
        coord_x=0, coord_y=0, coord_z=0
    )
    airfoils.append(root)
    
    # Mid section at Y=1
    mid = naca_tool.call(
        name="Mid_Section", 
        naca_digits="2412",
        chord_length=0.8,
        thickness=0.02,
        coord_x=0, coord_y=1, coord_z=0
    )
    airfoils.append(mid)
    
    # Tip section at Y=2
    tip = naca_tool.call(
        name="Tip_Section",
        naca_digits="2412", 
        chord_length=0.6,
        thickness=0.02,
        coord_x=0, coord_y=2, coord_z=0
    )
    airfoils.append(tip)
    
    print("Created airfoil sections:")
    for airfoil in airfoils:
        print(f"  - {airfoil.name}: Y={airfoil.coord_y}, chord={airfoil.model_data['chord_length']}")
    
    # Create meshes and check their bounding boxes
    print("\nMesh bounding box analysis:")
    for airfoil in airfoils:
        mesh = backend._create_naca4_mesh(airfoil)
        bounds = mesh.bounds
        center = mesh.centroid
        
        print(f"\n{airfoil.name}:")
        print(f"  Center: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})")
        print(f"  X-range: {bounds[0][0]:.2f} to {bounds[1][0]:.2f} (chord: {bounds[1][0] - bounds[0][0]:.2f})")
        print(f"  Y-range: {bounds[0][1]:.2f} to {bounds[1][1]:.2f} (thickness: {bounds[1][1] - bounds[0][1]:.2f})")
        print(f"  Z-range: {bounds[0][2]:.2f} to {bounds[1][2]:.2f} (height: {bounds[1][2] - bounds[0][2]:.2f})")
        print(f"  Volume: {mesh.volume:.6f}")
    
    # Render all airfoils
    print("\nRendering airfoils...")
    try:
        result = backend.render(airfoils)
        print(f"✓ Successfully rendered: {result}")
    except Exception as e:
        print(f"⚠ Rendering issue: {e}")
    
    # Export for verification
    print("\nExporting for verification...")
    try:
        backend.export_scene("naca4_orientation_verification.stl", "stl")
        print("✓ Exported to naca4_orientation_verification.stl")
        print("\nYou can open this file in a 3D viewer to verify:")
        print("  - Airfoils should point along X-axis (chord direction)")
        print("  - Multiple sections should be arranged along Y-axis")
        print("  - Airfoil thickness should be along Z-axis")
    except Exception as e:
        print(f"⚠ Export issue: {e}")
    
    return airfoils


def coordinate_system_summary():
    """Print a summary of the coordinate system."""
    print("\n" + "="*50)
    print("NACA4 AIRFOIL COORDINATE SYSTEM SUMMARY")
    print("="*50)
    print()
    print("CORRECTED ORIENTATION:")
    print("  ✓ X-axis: Chord direction (leading edge → trailing edge)")
    print("  ✓ Y-axis: Span direction (wing root → wing tip)")
    print("  ✓ Z-axis: Thickness direction (bottom → top)")
    print()
    print("AIRFOIL STACKING:")
    print("  ✓ Multiple airfoils stack along Y-axis (span direction)")
    print("  ✓ Each airfoil section lies in the X-Z plane")
    print("  ✓ Section normal points along Y-axis")
    print()
    print("USAGE:")
    print("  - Create airfoils with different coord_y values")
    print("  - No rotation needed - airfoils are generated in correct orientation")
    print("  - Chord length controls X-axis extent")
    print("  - Thickness controls sheet thickness along Y-axis")
    print("  - Airfoil shape height extends along Z-axis")


if __name__ == "__main__":
    verify_naca4_orientation()
    coordinate_system_summary()
