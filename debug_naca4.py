#!/usr/bin/env python3
"""
Debug script for NACA 4-digit airfoil generation.
This script will analyze and visualize the generated NACA airfoil coordinates
to identify any issues with the geometry.
"""

import numpy as np
import matplotlib.pyplot as plt
from models import ModelNACA4

def debug_naca4_coordinates():
    """Debug NACA4 coordinate generation."""
    print("=== NACA4 Coordinate Generation Debug ===")
    
    # Test different NACA airfoils
    test_cases = [
        {"naca": "0012", "name": "NACA 0012 (Symmetric, 12% thick)"},
        {"naca": "2412", "name": "NACA 2412 (2% camber at 40%, 12% thick)"},
        {"naca": "4412", "name": "NACA 4412 (4% camber at 40%, 12% thick)"}
    ]
    
    fig, axes = plt.subplots(len(test_cases), 2, figsize=(15, 4*len(test_cases)))
    if len(test_cases) == 1:
        axes = [axes]
    
    for i, test_case in enumerate(test_cases):
        naca_digits = test_case["naca"]
        name = test_case["name"]
        
        print(f"\n--- Testing {name} ---")
        
        # Generate coordinates
        chord_length = 1.0
        resolution = 100
        
        x, x_upper, y_upper, x_lower, y_lower = ModelNACA4.generate_naca4_coordinates(
            naca_digits, chord_length, resolution
        )
        
        # Parse NACA parameters for verification
        m = int(naca_digits[0]) / 100.0  # Max camber
        p = int(naca_digits[1]) / 10.0   # Position of max camber
        t = int(naca_digits[2:4]) / 100.0  # Thickness ratio
        
        print(f"  NACA parameters:")
        print(f"    Max camber: {m*100:.1f}% at {p*100:.0f}% chord")
        print(f"    Thickness: {t*100:.1f}%")
        
        # Analyze generated coordinates
        print(f"  Generated coordinates:")
        print(f"    Number of points: {len(x)}")
        print(f"    X range: [{np.min(x):.3f}, {np.max(x):.3f}]")
        print(f"    Y upper range: [{np.min(y_upper):.3f}, {np.max(y_upper):.3f}]")
        print(f"    Y lower range: [{np.min(y_lower):.3f}, {np.max(y_lower):.3f}]")
        
        # Check thickness at various points
        thickness_at_quarter = None
        thickness_at_half = None
        max_thickness = 0
        
        for j in range(len(x)):
            thickness = y_upper[j] - y_lower[j]
            max_thickness = max(max_thickness, thickness)
            
            if abs(x[j] - 0.25) < 0.01:  # Near 25% chord
                thickness_at_quarter = thickness
            if abs(x[j] - 0.5) < 0.01:   # Near 50% chord
                thickness_at_half = thickness
        
        print(f"  Thickness analysis:")
        print(f"    Max thickness: {max_thickness:.3f} ({max_thickness*100:.1f}% of chord)")
        print(f"    Expected max thickness: {t:.3f} ({t*100:.1f}% of chord)")
        if thickness_at_quarter:
            print(f"    Thickness at 25% chord: {thickness_at_quarter:.3f}")
        if thickness_at_half:
            print(f"    Thickness at 50% chord: {thickness_at_half:.3f}")
        
        # Check camber
        if m > 0:
            camber_line = (y_upper + y_lower) / 2
            max_camber = np.max(np.abs(camber_line))
            max_camber_pos = x[np.argmax(np.abs(camber_line))]
            print(f"  Camber analysis:")
            print(f"    Max camber: {max_camber:.3f} ({max_camber*100:.1f}% of chord)")
            print(f"    Expected max camber: {m:.3f} ({m*100:.1f}% of chord)")
            print(f"    Max camber position: {max_camber_pos:.3f} ({max_camber_pos*100:.1f}% chord)")
            print(f"    Expected position: {p:.3f} ({p*100:.1f}% chord)")
        
        # Plot airfoil profile
        axes[i][0].plot(x_upper, y_upper, 'b-', label='Upper surface', linewidth=2)
        axes[i][0].plot(x_lower, y_lower, 'r-', label='Lower surface', linewidth=2)
        axes[i][0].plot([x_upper[0], x_lower[0]], [y_upper[0], y_lower[0]], 'k-', linewidth=2, label='Leading edge')
        axes[i][0].plot([x_upper[-1], x_lower[-1]], [y_upper[-1], y_lower[-1]], 'k-', linewidth=2, label='Trailing edge')
        axes[i][0].set_aspect('equal')
        axes[i][0].grid(True, alpha=0.3)
        axes[i][0].set_xlabel('X/c')
        axes[i][0].set_ylabel('Y/c')
        axes[i][0].set_title(f'{name} - Profile View')
        axes[i][0].legend()
        
        # Plot thickness distribution
        thickness_dist = y_upper - y_lower
        axes[i][1].plot(x, thickness_dist, 'g-', linewidth=2, label='Thickness')
        axes[i][1].axhline(y=t, color='k', linestyle='--', alpha=0.7, label=f'Expected max: {t:.3f}')
        axes[i][1].grid(True, alpha=0.3)
        axes[i][1].set_xlabel('X/c')
        axes[i][1].set_ylabel('Thickness/c')
        axes[i][1].set_title(f'{name} - Thickness Distribution')
        axes[i][1].legend()
    
    plt.tight_layout()
    plt.savefig('naca4_debug_analysis.png', dpi=150, bbox_inches='tight')
    print(f"\n=== Analysis complete ===")
    print("Saved analysis plots to 'naca4_debug_analysis.png'")
    plt.show()

def test_3d_mesh_generation():
    """Test 3D mesh generation for NACA4."""
    print("\n=== 3D Mesh Generation Test ===")
    
    try:
        # Test creating a NACA4 model
        naca4_tool = ModelNACA4()
        model = naca4_tool.call(
            name="test_naca4",
            naca_digits="2412",
            chord_length=1.0,
            thickness=0.05,
            resolution=50
        )
        print(f"✓ Model created: {model.name}")
        print(f"  Type: {model.type}")
        print(f"  NACA: {model.model_data.get('naca_digits')}")
        print(f"  Chord: {model.model_data.get('chord_length')}")
        print(f"  Sheet thickness: {model.model_data.get('sheet_thickness')}")
          # Test backend mesh generation
        from backend_trimesh import BackendTrimesh
        backend = BackendTrimesh("debug_backend")
        
        print("  Generating 3D mesh...")
        mesh = backend._create_naca4_mesh(model)
        print(f"✓ Mesh created successfully")
        print(f"  Vertices: {len(mesh.vertices)}")
        print(f"  Faces: {len(mesh.faces)}")
        print(f"  Volume: {mesh.volume:.6f}")
        print(f"  Surface area: {mesh.area:.6f}")
        print(f"  Is watertight: {mesh.is_watertight}")
        print(f"  Is winding consistent: {mesh.is_winding_consistent}")
        
        # Export for inspection
        mesh.export('debug_naca4_mesh.stl')
        print("  Exported mesh to 'debug_naca4_mesh.stl'")
        
    except Exception as e:
        print(f"✗ Error in 3D mesh generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_naca4_coordinates()
    test_3d_mesh_generation()
