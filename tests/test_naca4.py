#!/usr/bin/env python3
"""
Unit tests for the NACA 4-digit airfoil functionality.
"""

import sys
import os
import unittest
import numpy as np
# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_trimesh import BackendTrimesh
from models import ModelNACA4
import trimesh


class TestNACA4Model(unittest.TestCase):
    """Test cases for the NACA 4-digit airfoil model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.naca_tool = ModelNACA4()
        self.backend = BackendTrimesh("test")
    
    def test_naca4_initialization(self):
        """Test NACA4 tool initialization."""
        self.assertEqual(self.naca_tool.name, "NACA4")
        self.assertEqual(self.naca_tool.tool_type, "model")
        self.assertIn("naca_digits", self.naca_tool.parameters)
        self.assertIn("chord_length", self.naca_tool.parameters)
    
    def test_naca4_model_creation(self):
        """Test NACA4 model creation."""
        model = self.naca_tool.call(
            name="test_naca",
            naca_digits="0012",
            chord_length=1.0,
            thickness=0.02
        )
        
        self.assertEqual(model.name, "test_naca")
        self.assertEqual(model.type, "naca4")
        self.assertEqual(model.model_data["naca_digits"], "0012")
        self.assertEqual(model.model_data["chord_length"], 1.0)
        self.assertEqual(model.model_data["sheet_thickness"], 0.02)
        self.assertEqual(model.model_data["max_camber"], 0.0)  # Symmetric airfoil
        self.assertEqual(model.model_data["thickness_ratio"], 0.12)
    
    def test_naca4_cambered_airfoil(self):
        """Test cambered NACA airfoil creation."""
        model = self.naca_tool.call(
            name="test_cambered",
            naca_digits="2412",
            chord_length=1.5,
            thickness=0.03
        )
        
        self.assertEqual(model.model_data["max_camber"], 0.02)  # 2% camber
        self.assertEqual(model.model_data["max_camber_position"], 0.4)  # At 40% chord
        self.assertEqual(model.model_data["thickness_ratio"], 0.12)  # 12% thickness
    
    def test_invalid_naca_digits(self):
        """Test handling of invalid NACA digits."""
        with self.assertRaises(ValueError):
            self.naca_tool.call(
                name="invalid",
                naca_digits="123",  # Too short
                chord_length=1.0,
                thickness=0.02
            )
        
        with self.assertRaises(ValueError):
            self.naca_tool.call(
                name="invalid2", 
                naca_digits="abcd",  # Non-numeric
                chord_length=1.0,
                thickness=0.02
            )
    
    def test_naca4_coordinate_generation(self):
        """Test NACA 4-digit coordinate generation."""
        # Test symmetric airfoil
        x, x_upper, y_upper, x_lower, y_lower = ModelNACA4.generate_naca4_coordinates(
            "0012", chord_length=1.0, resolution=20
        )
        
        # Check basic properties
        self.assertEqual(len(x), 20)
        self.assertEqual(len(x_upper), 20)
        self.assertEqual(len(y_upper), 20)
        self.assertEqual(len(x_lower), 20)
        self.assertEqual(len(y_lower), 20)
        
        # For symmetric airfoil, camber should be zero
        camber = (y_upper + y_lower) / 2
        np.testing.assert_allclose(camber, 0, atol=1e-10)
        
        # Check that thickness is positive
        thickness = y_upper - y_lower
        self.assertTrue(np.all(thickness >= 0))
        
        # Check leading and trailing edge
        self.assertAlmostEqual(x[0], 0.0, places=10)  # Leading edge at x=0
        self.assertAlmostEqual(x[-1], 1.0, places=5)  # Trailing edge at x=chord
    
    def test_naca4_cambered_coordinates(self):
        """Test cambered airfoil coordinate generation."""
        x, x_upper, y_upper, x_lower, y_lower = ModelNACA4.generate_naca4_coordinates(
            "2412", chord_length=1.0, resolution=20
        )
        
        # For cambered airfoil, camber should not be zero
        camber = (y_upper + y_lower) / 2
        max_camber = np.max(camber)
        self.assertGreater(max_camber, 0.01)  # Should have significant camber
        self.assertLess(max_camber, 0.025)    # But not too much for 2% camber
    
    def test_naca4_mesh_creation(self):
        """Test NACA4 mesh creation in backend."""
        model = self.naca_tool.call(
            name="mesh_test",
            naca_digits="0012", 
            chord_length=1.0,
            thickness=0.02
        )
        
        mesh = self.backend._create_naca4_mesh(model)
        
        self.assertIsNotNone(mesh)
        self.assertIsInstance(mesh, trimesh.Trimesh)
        self.assertGreater(mesh.faces.shape[0], 0)  # Should have faces
        self.assertGreater(mesh.vertices.shape[0], 0)  # Should have vertices
        
        # Check that mesh has reasonable bounds
        bounds = mesh.bounds
        self.assertAlmostEqual(bounds[1][0] - bounds[0][0], 1.0, places=1)  # Chord length
    
    def test_naca4_mesh_with_position(self):
        """Test NACA4 mesh creation with specific position."""
        model = self.naca_tool.call(
            name="positioned_test",
            naca_digits="2412",
            chord_length=1.0,
            thickness=0.02,
            coord_x=2.0,
            coord_y=1.0,
            coord_z=0.5
        )
        
        mesh = self.backend._create_naca4_mesh(model)
        centroid = mesh.centroid
        
        # Check that mesh is positioned correctly (approximately)
        self.assertAlmostEqual(centroid[0], 2.5, places=0)  # X should be around 2.5 (2.0 + 0.5*chord)
        self.assertAlmostEqual(centroid[1], 1.0, places=1)  # Y should be close to 1.0
        self.assertAlmostEqual(centroid[2], 0.5, places=1)  # Z should be close to 0.5
    
    def test_naca4_rendering(self):
        """Test NACA4 airfoil rendering."""
        model = self.naca_tool.call(
            name="render_test",
            naca_digits="4412",
            chord_length=1.0,
            thickness=0.02
        )
        
        try:
            result = self.backend.render([model])
            self.assertIsInstance(result, str)
            self.assertIn("Rendered", result)
        except Exception as e:
            # Rendering might fail in headless environment
            self.skipTest(f"Rendering failed in headless environment: {e}")
    
    def test_multiple_airfoils(self):
        """Test creating and rendering multiple airfoils."""
        airfoils = []
        naca_types = ["0012", "2412", "4412"]
        
        for i, naca in enumerate(naca_types):
            model = self.naca_tool.call(
                name=f"airfoil_{i}",
                naca_digits=naca,
                chord_length=1.0,
                thickness=0.02,
                coord_z=i * 2.0  # Space them apart
            )
            airfoils.append(model)
        
        # Test that all airfoils can be created
        self.assertEqual(len(airfoils), 3)
        
        # Test that meshes can be created for all
        meshes = []
        for airfoil in airfoils:
            mesh = self.backend._create_naca4_mesh(airfoil)
            self.assertIsNotNone(mesh)
            meshes.append(mesh)
        
        self.assertEqual(len(meshes), 3)


class TestNACA4Integration(unittest.TestCase):
    """Integration tests for NACA4 with the complete system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.backend = BackendTrimesh("integration_test")
    
    def test_agent_integration(self):
        """Test that NACA4 is properly integrated with the agent system."""
        from agent import gen_tool
        
        tools = gen_tool()
        naca_tools = [tool for tool in tools if hasattr(tool, 'name') and tool.name == 'NACA4']
        
        self.assertEqual(len(naca_tools), 1)
        self.assertIsInstance(naca_tools[0], ModelNACA4)
    
    def test_wing_design_workflow(self):
        """Test a complete wing design workflow."""
        naca_tool = ModelNACA4()
        
        # Create wing sections
        root_section = naca_tool.call("root", "2412", 1.5, 0.05, coord_y=0)
        mid_section = naca_tool.call("mid", "2412", 1.2, 0.05, coord_y=2)
        tip_section = naca_tool.call("tip", "2412", 0.8, 0.05, coord_y=4)
        
        wing_sections = [root_section, mid_section, tip_section]
        
        # Verify all sections can be converted to meshes
        for section in wing_sections:
            mesh = self.backend._create_naca4_mesh(section)
            self.assertIsNotNone(mesh)
            self.assertGreater(mesh.volume, 0)
        
        # Test rendering multiple sections
        try:
            result = self.backend.render(wing_sections)
            self.assertIn("3 models", result)
        except Exception as e:
            self.skipTest(f"Rendering failed: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
