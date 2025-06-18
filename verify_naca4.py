#!/usr/bin/env python3
"""
Quick verification that NACA4 functionality is working.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_naca4_basic():
    """Basic test of NACA4 functionality."""
    print("=== NACA4 Basic Functionality Test ===\n")
    
    try:
        # Test import
        from models import ModelNACA4
        print("✓ ModelNACA4 import successful")
        
        # Test tool creation
        naca_tool = ModelNACA4()
        print("✓ NACA4 tool creation successful")
        
        # Test model creation
        model = naca_tool.call(
            name="test_naca",
            naca_digits="0012",
            chord_length=1.0,
            thickness=0.02
        )
        print("✓ NACA4 model creation successful")
        print(f"  - Model name: {model.name}")
        print(f"  - NACA digits: {model.model_data['naca_digits']}")
        print(f"  - Chord length: {model.model_data['chord_length']}")
        print(f"  - Max camber: {model.model_data['max_camber']}")
        print(f"  - Thickness ratio: {model.model_data['thickness_ratio']}")
        
        # Test coordinate generation
        x, x_upper, y_upper, x_lower, y_lower = ModelNACA4.generate_naca4_coordinates("0012", 1.0, 20)
        print("✓ NACA4 coordinate generation successful")
        print(f"  - Generated {len(x)} coordinate points")
        
        # Test backend integration
        from backend_trimesh import BackendTrimesh
        backend = BackendTrimesh("test")
        print("✓ Backend creation successful")
        
        mesh = backend._create_naca4_mesh(model)
        if mesh:
            print("✓ NACA4 mesh creation successful")
            print(f"  - Mesh has {mesh.faces.shape[0]} faces and {mesh.vertices.shape[0]} vertices")
        else:
            print("✗ NACA4 mesh creation failed")
            return False
        
        # Test agent integration
        from agent import gen_tool
        tools = gen_tool()
        naca_tools = [tool for tool in tools if hasattr(tool, 'name') and tool.name == 'NACA4']
        if len(naca_tools) == 1:
            print("✓ Agent integration successful")
        else:
            print("✗ Agent integration failed")
            return False
        
        print("\n🎉 All NACA4 tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_naca4_examples():
    """Test different NACA airfoils."""
    print("\n=== NACA4 Examples ===\n")
    
    try:
        from models import ModelNACA4
        naca_tool = ModelNACA4()
        
        examples = [
            ("0012", "Symmetric airfoil, 12% thickness"),
            ("2412", "2% camber at 40% chord, 12% thickness"), 
            ("4412", "4% camber at 40% chord, 12% thickness"),
            ("6409", "6% camber at 40% chord, 9% thickness")
        ]
        
        for naca_digits, description in examples:
            model = naca_tool.call(
                name=f"NACA_{naca_digits}",
                naca_digits=naca_digits,
                chord_length=1.0,
                thickness=0.02
            )
            
            camber = model.model_data['max_camber']
            camber_pos = model.model_data['max_camber_position']
            thickness = model.model_data['thickness_ratio']
            
            print(f"NACA {naca_digits}: {description}")
            print(f"  - Max camber: {camber:.1%} at {camber_pos:.0%} chord")
            print(f"  - Thickness: {thickness:.1%}")
            print()
        
        return True
    except Exception as e:
        print(f"✗ Examples error: {e}")
        return False

if __name__ == "__main__":
    success1 = test_naca4_basic()
    success2 = test_naca4_examples()
    
    if success1 and success2:
        print("🚀 NACA4 feature is ready for use!")
        print("\nUsage examples:")
        print("  python examples/naca4_airfoil_example.py")
        print("  python tests/test_naca4.py")
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)
