from if_model import Model, ModelOperation
from if_backend import BackendIface
from typing import List, Dict, Any, Optional
import trimesh
import numpy as np
import random

class BackendTrimesh(BackendIface):
    def __init__(self, name: str):
        """
        Initialize the Trimesh backend with a name.
        :param name: Name of the backend.
        """
        super().__init__(name)
        self.name = name
        self.scene = trimesh.Scene()
    
    def transform(self, model: List[Model], operations: List[ModelOperation]) -> List[Model]:
        """
        Transform the given model using the specified operations.
        :param model: List of models to be transformed.
        :param operations: List of operations to apply to the models.
        :return: List of transformed models.
        """
        for o in operations:
            if o.type == "transform_rigid":
                # Apply rigid transformation to each model
                for m in model:
                    if m.name == o.models[0]:
                        t = o.parameters.get("translation", [0.0, 0.0, 0.0])
                        r = o.parameters.get("rotation", [0.0, 0.0, 0.0])
                        s = o.parameters.get("scale", 1.0)
                        m.coord_x += t[0]
                        m.coord_y += t[1]
                        m.coord_z += t[2]
                        m.orientation_pitch += r[0]
                        m.orientation_yaw += r[1]
                        m.orientation_roll += r[2]
                        m.box_size = [dim * s for dim in m.box_size]
        return model
    
    def render(self, models: List[Model]) -> str:
        """
        Render the given models using Trimesh and display them.
        :param models: List of models to be rendered.
        :return: String representation of the rendered models.
        """
        # Clear previous scene
        self.scene = trimesh.Scene()
        
        for i, m in enumerate(models):
            mesh = self._create_mesh_from_model(m)
            if mesh is not None:
                # Generate random color for each model
                color = [random.randint(0, 255) for _ in range(3)] + [200]  # RGB + Alpha
                mesh.visual.face_colors = color
                
                # Add mesh to scene with a unique name
                self.scene.add_geometry(mesh, node_name=f"{m.name}_{i}")
        
        # Show the scene
        try:
            self.scene.show()
        except Exception as e:
            print(f"Error displaying scene: {e}")
            print("Scene created successfully but display failed. This might be due to missing display dependencies.")
          # Return a string representation
        return f"Rendered {len(models)} models using Trimesh backend"
    
    def _create_mesh_from_model(self, model: Model) -> Optional[trimesh.Trimesh]:
        """
        Create a trimesh object from a Model.
        :param model: Model to convert to mesh.
        :return: Trimesh object or None if model type is not supported.
        """
        x, y, z = model.coord_x, model.coord_y, model.coord_z
        
        if model.type == "cube":
            return self._create_cube_mesh(model)
        elif model.type == "cylinder":
            return self._create_cylinder_mesh(model)
        elif model.type == "half cylinder":
            return self._create_half_cylinder_mesh(model)
        elif model.type == "naca4":
            return self._create_naca4_mesh(model)
        else:
            print(f"Unsupported model type: {model.type}")
            return None
    
    def _create_cube_mesh(self, model: Model) -> trimesh.Trimesh:
        """
        Create a cube mesh from model data.
        :param model: Model containing cube data.
        :return: Trimesh cube object.
        """
        dx, dy, dz = model.box_size
        
        # Create a box using trimesh
        box = trimesh.creation.box(extents=[dx, dy, dz])
        
        # Apply transformations
        transform_matrix = self._get_transform_matrix(model)
        box.apply_transform(transform_matrix)
        
        return box
    
    def _create_cylinder_mesh(self, model: Model) -> trimesh.Trimesh:
        """
        Create a cylinder mesh from model data.
        :param model: Model containing cylinder data.
        :return: Trimesh cylinder object.
        """
        radius_x = model.model_data.get("radius_x", model.box_size[0]/2)
        radius_y = model.model_data.get("radius_y", model.box_size[1]/2)
        height = model.model_data.get("height", model.box_size[2])
        
        # For elliptical cylinder, we'll use the average radius and then scale
        avg_radius = (radius_x + radius_y) / 2
        
        # Create a cylinder using trimesh
        cylinder = trimesh.creation.cylinder(radius=avg_radius, height=height)
        
        # Scale to create elliptical cross-section if needed
        if abs(radius_x - radius_y) > 1e-6:  # If radii are different
            scale_matrix = np.eye(4)
            scale_matrix[0, 0] = radius_x / avg_radius
            scale_matrix[1, 1] = radius_y / avg_radius
            cylinder.apply_transform(scale_matrix)
          # Apply transformations
        transform_matrix = self._get_transform_matrix(model)
        cylinder.apply_transform(transform_matrix)
        
        return cylinder
    
    def _create_half_cylinder_mesh(self, model: Model) -> trimesh.Trimesh:
        """
        Create a half cylinder mesh from model data.
        :param model: Model containing half cylinder data.
        :return: Trimesh half cylinder object.
        """
        radius_x = model.model_data.get("radius_x", model.box_size[0]/2)
        radius_y = model.model_data.get("radius_y", model.box_size[1]/2)
        height = model.model_data.get("height", model.box_size[2])
        
        # Use a simpler approach: create a full cylinder and cut it in half
        # Create a full cylinder first
        avg_radius = (radius_x + radius_y) / 2
        full_cylinder = trimesh.creation.cylinder(radius=avg_radius, height=height)
        
        # Scale to create elliptical cross-section if needed
        if abs(radius_x - radius_y) > 1e-6:
            scale_matrix = np.eye(4)
            scale_matrix[0, 0] = radius_x / avg_radius
            scale_matrix[1, 1] = radius_y / avg_radius
            full_cylinder.apply_transform(scale_matrix)
        
        # Create a cutting plane to make it half cylinder
        # Create a box that will cut the cylinder in half
        cutting_box = trimesh.creation.box(extents=[radius_x*4, radius_y*2, height*2])
        cutting_transform = trimesh.transformations.translation_matrix([radius_x, 0, 0])
        cutting_box.apply_transform(cutting_transform)
        
        try:
            # Use boolean difference to cut the cylinder
            half_cylinder = full_cylinder.difference(cutting_box)
        except Exception as e:
            print(f"Warning: Boolean operation failed for half cylinder: {e}")
            # Fallback: return the full cylinder if boolean operation fails
            half_cylinder = full_cylinder          # Apply transformations
        transform_matrix = self._get_transform_matrix(model)
        half_cylinder.apply_transform(transform_matrix)
        
        return half_cylinder
    
    def _create_naca4_mesh(self, model: Model) -> trimesh.Trimesh:
        """
        Create a NACA 4-digit airfoil mesh from model data.
        
        Uses standardized orientation from model_orientation_config:
        - Chord direction: X-axis (airfoil points along X-axis)
        - Span direction: Y-axis (stackable along Y-axis)
        - Thickness direction: Z-axis (airfoil thickness along Z-axis)
        - Section normal: Y-axis direction (perpendicular to airfoil surface)
        
        :param model: Model containing NACA airfoil data.
        :return: Trimesh airfoil object (thin sheet).
        """
        from models import ModelNACA4
        
        # Extract NACA parameters from model data
        naca_digits = model.model_data.get("naca_digits", "0012")
        chord_length = model.model_data.get("chord_length", 1.0)
        thickness = model.model_data.get("sheet_thickness", 0.01)
        resolution = model.model_data.get("resolution", 50)
        
        # Generate NACA airfoil coordinates (in 2D: x=chord, y=thickness)
        x, x_upper, y_upper, x_lower, y_lower = ModelNACA4.generate_naca4_coordinates(
            naca_digits, chord_length, resolution
        )
        
        # Create vertices for the airfoil sheet
        # We'll create a thin 3D airfoil by extruding the 2D profile along Y-axis
        vertices = []
        faces = []
        
        # Number of points around the airfoil
        n_points = len(x_upper)
        
        # Create vertices for both sides of the thin sheet
        # The airfoil lies in X-Z plane, extruded along Y-axis
        # Front side (y = -thickness/2)
        for i in range(n_points):
            vertices.append([x_upper[i], -thickness/2, y_upper[i]])
        for i in range(n_points-1, -1, -1):  # Reverse order for lower surface
            vertices.append([x_lower[i], -thickness/2, y_lower[i]])
          # Back side (y = +thickness/2)
        for i in range(n_points):
            vertices.append([x_upper[i], thickness/2, y_upper[i]])
        for i in range(n_points-1, -1, -1):  # Reverse order for lower surface
            vertices.append([x_lower[i], thickness/2, y_lower[i]])
        
        vertices = np.array(vertices)
        
        # Create faces
        n_airfoil_points = 2 * n_points  # Total points around airfoil perimeter
        
        # Front face (y = -thickness/2) - fan triangulation from first vertex
        for i in range(n_airfoil_points - 2):
            faces.append([0, i + 2, i + 1])  # Reversed winding for correct normal
        
        # Back face (y = +thickness/2) - fan triangulation from first vertex
        offset = n_airfoil_points
        for i in range(n_airfoil_points - 2):
            faces.append([offset, offset + i + 1, offset + i + 2])
        
        # Side faces (connecting front and back)
        for i in range(n_airfoil_points):
            next_i = (i + 1) % n_airfoil_points
            
            # Create two triangles for each side edge
            v1 = i  # Front vertex i
            v2 = next_i  # Front vertex i+1
            v3 = offset + i  # Back vertex i
            v4 = offset + next_i  # Back vertex i+1
            
            # Triangle 1: v1, v3, v2 (correct winding for outward normal)
            faces.append([v1, v3, v2])
            # Triangle 2: v2, v3, v4
            faces.append([v2, v3, v4])
        
        faces = np.array(faces)
        
        # Create the mesh
        try:
            airfoil = trimesh.Trimesh(vertices=vertices, faces=faces)
            
            # Ensure proper normals
            airfoil.fix_normals()
            
            # Apply transformations
            transform_matrix = self._get_transform_matrix(model)
            airfoil.apply_transform(transform_matrix)
            
            return airfoil
        except Exception as e:
            print(f"Warning: Failed to create NACA airfoil mesh: {e}")
            # Fallback: create a simple flat rectangle
            fallback = trimesh.creation.box(extents=[chord_length, thickness, chord_length*0.1])
            transform_matrix = self._get_transform_matrix(model)
            fallback.apply_transform(transform_matrix)
            return fallback
    
    def _get_transform_matrix(self, model: Model) -> np.ndarray:
        """
        Get the transformation matrix for a model based on its position and orientation.
        :param model: Model to get transformation for.
        :return: 4x4 transformation matrix.
        """
        # Translation
        translation = np.array([model.coord_x, model.coord_y, model.coord_z])
        
        # Rotation (pitch, yaw, roll in degrees)
        pitch = np.radians(model.orientation_pitch)
        yaw = np.radians(model.orientation_yaw)
        roll = np.radians(model.orientation_roll)
        
        # Create rotation matrices
        Rx = trimesh.transformations.rotation_matrix(pitch, [1, 0, 0])
        Ry = trimesh.transformations.rotation_matrix(yaw, [0, 1, 0])
        Rz = trimesh.transformations.rotation_matrix(roll, [0, 0, 1])
        
        # Combined rotation (order: Rz * Ry * Rx)
        rotation_matrix = np.dot(np.dot(Rz, Ry), Rx)
        
        # Apply translation
        rotation_matrix[:3, 3] = translation
        
        return rotation_matrix
    
    def export_scene(self, filename: str, file_format: str = 'stl'):
        """
        Export the current scene to a file.
        :param filename: Name of the file to export to.
        :param file_format: File format ('stl', 'obj', 'ply', etc.)
        """
        try:
            if file_format.lower() == 'stl':
                # For STL, we need to combine all meshes into one
                combined_mesh = None
                for geometry_name, geometry in self.scene.geometry.items():
                    if isinstance(geometry, trimesh.Trimesh):
                        if combined_mesh is None:
                            combined_mesh = geometry.copy()
                        else:
                            combined_mesh = combined_mesh.union(geometry)
                
                if combined_mesh is not None:
                    combined_mesh.export(filename)
                    print(f"Scene exported to {filename}")
                else:
                    print("No geometry to export")
            else:
                # For other formats, export the scene directly
                self.scene.export(filename)
                print(f"Scene exported to {filename}")
        except Exception as e:
            print(f"Error exporting scene: {e}")
    
    def perform_boolean_operations(self, mesh1: trimesh.Trimesh, mesh2: trimesh.Trimesh, operation: str) -> trimesh.Trimesh:
        """
        Perform boolean operations between two meshes.
        :param mesh1: First mesh.
        :param mesh2: Second mesh.
        :param operation: Type of boolean operation ('union', 'intersection', 'difference').
        :return: Result mesh.
        """
        try:
            if operation == 'union':
                return mesh1.union(mesh2)
            elif operation == 'intersection':
                return mesh1.intersection(mesh2)
            elif operation == 'difference':
                return mesh1.difference(mesh2)
            else:
                raise ValueError(f"Unsupported boolean operation: {operation}")
        except Exception as e:
            print(f"Error performing boolean operation {operation}: {e}")
            return mesh1  # Return original mesh if operation fails
