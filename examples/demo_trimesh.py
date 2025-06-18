#!/usr/bin/env python3
"""
Example script demonstrating the new Trimesh backend capabilities.
This script shows how the Trimesh backend improves upon the Matplotlib backend,
especially for boolean operations.
"""

import sys
import os
# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import Agent, gen_tool
from backend_trimesh import BackendTrimesh
from models import ModelCube, ModelCylinder
import trimesh
import numpy as np

def demonstrate_trimesh_backend():
    """Demonstrate the capabilities of the new Trimesh backend."""
    
    print("=== Trimesh Backend Demonstration ===\n")
    
    # Initialize the backend
    backend = BackendTrimesh("trimesh_demo")
    
    # Create some example models
    print("1. Creating example models...")
    
    # Create a cube
    cube = ModelCube()
    cube_model = cube.call(
        coord_x=0, coord_y=0, coord_z=0,
        size_x=2, size_y=2, size_z=2,
        orientation_pitch=0, orientation_yaw=0, orientation_roll=0
    )
    cube_model.name = "cube_1"
    
    # Create a cylinder
    cylinder = ModelCylinder()
    cylinder_model = cylinder.call(
        coord_x=1, coord_y=0, coord_z=0,
        radius_x=1, radius_y=1, height=3,
        orientation_pitch=0, orientation_yaw=0, orientation_roll=90
    )
    cylinder_model.name = "cylinder_1"
    
    models = [cube_model, cylinder_model]
    
    print(f"Created {len(models)} models:")
    for model in models:
        print(f"  - {model.name}: {model.type}")
    
    # Render the models
    print("\n2. Rendering models with Trimesh backend...")
    result = backend.render(models)
    print(f"Render result: {result}")
    
    # Demonstrate boolean operations capability
    print("\n3. Demonstrating boolean operations...")
    
    # Get the meshes from the models
    cube_mesh = backend._create_mesh_from_model(cube_model)
    cylinder_mesh = backend._create_mesh_from_model(cylinder_model)
    
    if cube_mesh and cylinder_mesh:
        # Perform union operation
        print("  - Performing union operation...")
        union_result = backend.perform_boolean_operations(cube_mesh, cylinder_mesh, 'union')
        print(f"    Union mesh: {union_result.faces.shape[0]} faces, {union_result.vertices.shape[0]} vertices")
        
        # Perform intersection operation
        print("  - Performing intersection operation...")
        intersection_result = backend.perform_boolean_operations(cube_mesh, cylinder_mesh, 'intersection')
        print(f"    Intersection mesh: {intersection_result.faces.shape[0]} faces, {intersection_result.vertices.shape[0]} vertices")
        
        # Perform difference operation
        print("  - Performing difference operation...")
        difference_result = backend.perform_boolean_operations(cube_mesh, cylinder_mesh, 'difference')
        print(f"    Difference mesh: {difference_result.faces.shape[0]} faces, {difference_result.vertices.shape[0]} vertices")
        
        # Create a scene with boolean results
        boolean_scene = trimesh.Scene()
        
        # Add results with different colors
        union_result.visual.face_colors = [255, 0, 0, 200]  # Red
        intersection_result.visual.face_colors = [0, 255, 0, 200]  # Green
        difference_result.visual.face_colors = [0, 0, 255, 200]  # Blue
        
        # Position them apart for visualization
        union_transform = trimesh.transformations.translation_matrix([0, 0, 0])
        intersection_transform = trimesh.transformations.translation_matrix([5, 0, 0])
        difference_transform = trimesh.transformations.translation_matrix([10, 0, 0])
        
        union_result.apply_transform(union_transform)
        intersection_result.apply_transform(intersection_transform)
        difference_result.apply_transform(difference_transform)
        
        boolean_scene.add_geometry(union_result, node_name="union")
        boolean_scene.add_geometry(intersection_result, node_name="intersection")
        boolean_scene.add_geometry(difference_result, node_name="difference")
        
        print("\n4. Displaying boolean operation results...")
        try:
            boolean_scene.show()
        except Exception as e:
            print(f"Display error: {e}")
            print("Boolean operations completed successfully, but display failed.")
    
    # Demonstrate export functionality
    print("\n5. Demonstrating export functionality...")
    try:
        backend.export_scene("demo_scene.stl", "stl")
        print("Scene exported to demo_scene.stl")
    except Exception as e:
        print(f"Export error: {e}")
    
    print("\n=== Advantages of Trimesh Backend ===")
    print("✓ Better support for boolean operations (union, intersection, difference)")
    print("✓ More accurate 3D geometry representation")
    print("✓ Export capabilities to various 3D formats (STL, OBJ, PLY)")
    print("✓ Better performance for complex 3D operations")
    print("✓ Support for mesh analysis and repair")
    print("✓ Professional-grade 3D geometry processing")

def demonstrate_with_agent():
    """Demonstrate the Trimesh backend working with the Agent."""
    
    print("\n=== Agent Integration with Trimesh Backend ===\n")
    
    # Create agent with tools
    agent = Agent(tools=gen_tool())
    
    # Test input
    user_input = "创建一个立方体和一个圆柱体用于演示"
    
    print(f"User input: {user_input}")
    print("Processing with agent...")
    
    try:
        models, ops = agent.input(user_input)
        print(f"Generated {len(models)} models and {len(ops)} operations")
        
        # Use Trimesh backend for rendering
        backend = BackendTrimesh("agent_demo")
        transformed_models = backend.transform(models, ops)
        
        if transformed_models:
            print("Rendering with Trimesh backend...")
            result = backend.render(transformed_models)
            print(f"Render result: {result}")
        else:
            print("No models were generated to render.")
            
    except Exception as e:
        print(f"Error during agent processing: {e}")

if __name__ == "__main__":
    # Run demonstrations
    demonstrate_trimesh_backend()
    
    # Uncomment the line below to test agent integration
    # demonstrate_with_agent()
