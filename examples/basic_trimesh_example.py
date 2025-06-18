#!/usr/bin/env python3
"""
Simple example demonstrating Trimesh backend usage.
This example shows basic model creation and rendering.
"""

import sys
import os
# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_trimesh import BackendTrimesh
from models import ModelCube, ModelCylinder, ModelHalfCylinder


def basic_example():
    """Basic example of using the Trimesh backend."""
    print("=== Basic Trimesh Backend Example ===\n")
    
    # Create backend
    backend = BackendTrimesh("example")
    
    # Create models
    print("Creating 3D models...")
    
    # Cube
    cube = ModelCube()
    cube_model = cube.call(name="example_cube", width=2, height=2, depth=2)
    cube_model.coord_x = 0
    cube_model.coord_y = 0
    cube_model.coord_z = 0
    
    # Cylinder
    cylinder = ModelCylinder()
    cylinder_model = cylinder.call(
        name="example_cylinder", 
        radius_x=1, radius_y=1, height=3,
        coord_x=4, coord_y=0, coord_z=0
    )
    
    # Half cylinder
    half_cylinder = ModelHalfCylinder()
    half_cylinder_model = half_cylinder.call(
        name="example_half_cylinder",
        radius_x=1, radius_y=1, height=2
    )
    half_cylinder_model.coord_x = -4
    half_cylinder_model.coord_y = 0
    half_cylinder_model.coord_z = 0
    
    models = [cube_model, cylinder_model, half_cylinder_model]
    
    print(f"Created {len(models)} models:")
    for model in models:
        print(f"  - {model.name}: {model.type}")
    
    # Render models
    print("\nRendering models...")
    try:
        result = backend.render(models)
        print(f"✓ {result}")
    except Exception as e:
        print(f"⚠ Rendering note: {e}")
        print("  (3D display might not be available in this environment)")
    
    # Demonstrate boolean operations
    print("\nDemonstrating boolean operations...")
    cube_mesh = backend._create_mesh_from_model(cube_model)
    cylinder_mesh = backend._create_mesh_from_model(cylinder_model)
    
    if cube_mesh and cylinder_mesh:
        try:
            union_mesh = backend.perform_boolean_operations(cube_mesh, cylinder_mesh, 'union')
            print(f"✓ Union: {union_mesh.faces.shape[0]} faces")
            
            intersection_mesh = backend.perform_boolean_operations(cube_mesh, cylinder_mesh, 'intersection') 
            print(f"✓ Intersection: {intersection_mesh.faces.shape[0]} faces")
            
            difference_mesh = backend.perform_boolean_operations(cube_mesh, cylinder_mesh, 'difference')
            print(f"✓ Difference: {difference_mesh.faces.shape[0]} faces")
        except Exception as e:
            print(f"⚠ Boolean operations note: {e}")
    
    # Export example
    print("\nExporting to file...")
    try:
        backend.export_scene("example_output.stl", "stl")
        print("✓ Exported to example_output.stl")
    except Exception as e:
        print(f"⚠ Export note: {e}")
    
    print("\n=== Example Complete ===")


def comparison_info():
    """Show comparison information between backends."""
    print("\n=== Why Trimesh Backend? ===\n")
    
    advantages = [
        "✓ Professional-grade 3D geometry processing",
        "✓ Full boolean operations support (union, intersection, difference)",
        "✓ Multiple file export formats (STL, OBJ, PLY, etc.)",
        "✓ Higher precision and better performance",
        "✓ Better CAD workflow integration",
        "✓ Mesh analysis and repair capabilities"
    ]
    
    for advantage in advantages:
        print(advantage)
    
    print("\nThe Matplotlib backend was limited in boolean operations,")
    print("which is crucial for complex 3D modeling tasks.")


if __name__ == "__main__":
    basic_example()
    comparison_info()
