from if_model import Model, ModelOperation
from if_backend import BackendIface
from typing import List, Dict, Any, Optional
# import random colors for 3d model rendeoing
import random
from matplotlib.colors import CSS4_COLORS as colors
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

class BackendMatplot(BackendIface):
    def __init__(self, name: str):
        """
        Initialize the Matplotlib backend with a name.
        :param name: Name of the backend.
        """
        super().__init__(name)
        self.name = name
    def transform(self, model: List[Model], operation: ModelOperation) -> List[Model]:
        """
        Transform the given model using the specified operation.
        :param model: List of models to be transformed.
        :param operation: The operation to apply to the models.
        :return: List of transformed models.
        """
        for o in operation:
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
        # Return the transformed model
        return model  # No transformation in this backend
    
    def render(self, model: List[Model]) -> str:
        """
        Render the given model to a string representation using Matplotlib.
        :param model: List of models to be rendered.
        :return: String representation of the rendered model.
        """
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        
        for m in model:
            # Generate attributes for rendering
            x, y, z = m.coord_x, m.coord_y, m.coord_z
            color = random.choice(list(colors.values()))
            alpha = random.uniform(0.5, 0.8)  # Random transparency

            if m.type == "cube":
                """
                Render a cube model in 3D space with orientation.
                :param m: Model object containing cube data.
                """
                dx, dy, dz = m.box_size
                print(f"Rendering cube at ({x}, {y}, {z}) with size ({dx}, {dy}, {dz}) and color {color}")

                # Create a 3D cube using vertices centered at origin
                vertices = np.array([
                    [-dx/2, -dy/2, -dz/2], [dx/2, -dy/2, -dz/2], [dx/2, dy/2, -dz/2], [-dx/2, dy/2, -dz/2],  # bottom face
                    [-dx/2, -dy/2, dz/2], [dx/2, -dy/2, dz/2], [dx/2, dy/2, dz/2], [-dx/2, dy/2, dz/2]  # top face
                ])
                
                # Apply rotation transformations (pitch, yaw, roll)
                pitch, yaw, roll = np.radians(m.orientation_pitch), np.radians(m.orientation_yaw), np.radians(m.orientation_roll)
                
                # Rotation matrices
                Rx = np.array([[1, 0, 0], [0, np.cos(pitch), -np.sin(pitch)], [0, np.sin(pitch), np.cos(pitch)]])
                Ry = np.array([[np.cos(yaw), 0, np.sin(yaw)], [0, 1, 0], [-np.sin(yaw), 0, np.cos(yaw)]])
                Rz = np.array([[np.cos(roll), -np.sin(roll), 0], [np.sin(roll), np.cos(roll), 0], [0, 0, 1]])
                
                # Combined rotation matrix (order: Rz * Ry * Rx)
                R = Rz @ Ry @ Rx
                
                # Apply rotation to vertices
                rotated_vertices = vertices @ R.T
                
                # Translate to final position
                final_vertices = rotated_vertices + np.array([x, y, z])
                
                # Define the 6 faces of the cube
                faces = [
                    [final_vertices[0], final_vertices[1], final_vertices[2], final_vertices[3]],  # bottom
                    [final_vertices[4], final_vertices[5], final_vertices[6], final_vertices[7]],  # top
                    [final_vertices[0], final_vertices[1], final_vertices[5], final_vertices[4]],  # front
                    [final_vertices[2], final_vertices[3], final_vertices[7], final_vertices[6]],  # back
                    [final_vertices[1], final_vertices[2], final_vertices[6], final_vertices[5]],  # right
                    [final_vertices[0], final_vertices[3], final_vertices[7], final_vertices[4]]   # left
                ]
                
                # Draw each face
                ax.add_collection3d(Poly3DCollection(faces, alpha=alpha, facecolor=color, edgecolor='black'))
            elif m.type == "cylinder":
                """
                Render a cylinder model in 3D space with orientation.
                :param m: Model object containing cylinder data.
                """
                radius_x = m.model_data.get("radius_x", m.box_size[0]/2)
                radius_y = m.model_data.get("radius_y", m.box_size[1]/2)
                height = m.model_data.get("height", m.box_size[2])
                print(f"Rendering cylinder at ({x}, {y}, {z}) with radii ({radius_x}, {radius_y}), height {height} and color {color}")

                # Create cylinder geometry
                theta = np.linspace(0, 2*np.pi, 30)
                z_cyl = np.linspace(-height/2, height/2, 20)
                theta_mesh, z_mesh = np.meshgrid(theta, z_cyl)

                # Generate cylinder surface points
                x_cyl = radius_x * np.cos(theta_mesh)
                y_cyl = radius_y * np.sin(theta_mesh)

                # Stack all surface points for rotation
                surface_points = np.stack([x_cyl.flatten(), y_cyl.flatten(), z_mesh.flatten()], axis=1)

                # Create top and bottom circles
                theta_circle = np.linspace(0, 2*np.pi, 30)
                x_circle = radius_x * np.cos(theta_circle)
                y_circle = radius_y * np.sin(theta_circle)

                # Top circle (z = height/2)
                top_circle = np.stack([x_circle, y_circle, np.full_like(x_circle, height/2)], axis=1)
                # Bottom circle (z = -height/2)
                bottom_circle = np.stack([x_circle, y_circle, np.full_like(x_circle, -height/2)], axis=1)

                # Combine all points
                all_points = np.vstack([surface_points, top_circle, bottom_circle])

                # Apply rotation transformations (pitch, yaw, roll)
                pitch, yaw, roll = np.radians(m.orientation_pitch), np.radians(m.orientation_yaw), np.radians(m.orientation_roll)

                # Rotation matrices
                Rx = np.array([[1, 0, 0], [0, np.cos(pitch), -np.sin(pitch)], [0, np.sin(pitch), np.cos(pitch)]])
                Ry = np.array([[np.cos(yaw), 0, np.sin(yaw)], [0, 1, 0], [-np.sin(yaw), 0, np.cos(yaw)]])
                Rz = np.array([[np.cos(roll), -np.sin(roll), 0], [np.sin(roll), np.cos(roll), 0], [0, 0, 1]])

                # Combined rotation matrix (order: Rz * Ry * Rx)
                R = Rz @ Ry @ Rx

                # Apply rotation to all points
                rotated_points = all_points @ R.T

                # Translate to final position
                final_points = rotated_points + np.array([x, y, z])

                # Extract rotated surface points
                surface_count = surface_points.shape[0]
                rotated_surface = final_points[:surface_count]
                rotated_x_cyl = rotated_surface[:, 0].reshape(x_cyl.shape)
                rotated_y_cyl = rotated_surface[:, 1].reshape(y_cyl.shape)
                rotated_z_cyl = rotated_surface[:, 2].reshape(z_mesh.shape)

                # Extract rotated circles
                rotated_top = final_points[surface_count:surface_count+len(theta_circle)]
                rotated_bottom = final_points[surface_count+len(theta_circle):]

                # Draw cylinder surface
                ax.plot_surface(rotated_x_cyl, rotated_y_cyl, rotated_z_cyl, alpha=alpha, color=color)

                # Draw top and bottom circles

                # Create filled circles for top and bottom
                top_poly = [rotated_top]
                bottom_poly = [rotated_bottom]

                ax.add_collection3d(Poly3DCollection(top_poly, alpha=alpha, facecolor=color, edgecolor='black'))
                ax.add_collection3d(Poly3DCollection(bottom_poly, alpha=alpha, facecolor=color, edgecolor='black'))
            elif m.type == "half cylinder":
                """
                Render a half cylinder model in 3D space with orientation.
                :param m: Model object containing half cylinder data.
                """
                radius_x = m.model_data.get("radius_x", m.box_size[0]/2)
                radius_y = m.model_data.get("radius_y", m.box_size[1]/2)
                height = m.model_data.get("height", m.box_size[2])
                print(f"Rendering half cylinder at ({x}, {y}, {z}) with radii ({radius_x}, {radius_y}), height {height} and color {color}")

                # Create half cylinder geometry (0 to pi)
                theta = np.linspace(0, np.pi, 15)  # Half circle
                z_cyl = np.linspace(-height/2, height/2, 20)
                theta_mesh, z_mesh = np.meshgrid(theta, z_cyl)

                # Generate half cylinder surface points
                x_cyl = radius_x * np.cos(theta_mesh)
                y_cyl = radius_y * np.sin(theta_mesh)

                # Stack all surface points for rotation
                surface_points = np.stack([x_cyl.flatten(), y_cyl.flatten(), z_mesh.flatten()], axis=1)

                # Create top and bottom half circles
                theta_circle = np.linspace(0, np.pi, 15)
                x_circle = radius_x * np.cos(theta_circle)
                y_circle = radius_y * np.sin(theta_circle)

                # Top half circle (z = height/2)
                top_circle = np.stack([x_circle, y_circle, np.full_like(x_circle, height/2)], axis=1)
                # Bottom half circle (z = -height/2)
                bottom_circle = np.stack([x_circle, y_circle, np.full_like(x_circle, -height/2)], axis=1)

                # Create flat rectangular surfaces to close the half cylinder
                # Front flat surface (y = 0)
                x_flat = np.linspace(-radius_x, radius_x, 10)
                z_flat = np.linspace(-height/2, height/2, 20)
                x_flat_mesh, z_flat_mesh = np.meshgrid(x_flat, z_flat)
                y_flat_mesh = np.zeros_like(x_flat_mesh)

                # Only keep points inside the semicircle
                mask = (x_flat_mesh**2 / radius_x**2) <= 1
                x_flat_mesh = x_flat_mesh[mask]
                y_flat_mesh = y_flat_mesh[mask]
                z_flat_mesh = z_flat_mesh[mask]

                flat_surface = np.stack([x_flat_mesh, y_flat_mesh, z_flat_mesh], axis=1)

                # Combine all points
                all_points = np.vstack([surface_points, top_circle, bottom_circle, flat_surface])

                # Apply rotation transformations (pitch, yaw, roll)
                pitch, yaw, roll = np.radians(m.orientation_pitch), np.radians(m.orientation_yaw), np.radians(m.orientation_roll)

                # Rotation matrices
                Rx = np.array([[1, 0, 0], [0, np.cos(pitch), -np.sin(pitch)], [0, np.sin(pitch), np.cos(pitch)]])
                Ry = np.array([[np.cos(yaw), 0, np.sin(yaw)], [0, 1, 0], [-np.sin(yaw), 0, np.cos(yaw)]])
                Rz = np.array([[np.cos(roll), -np.sin(roll), 0], [np.sin(roll), np.cos(roll), 0], [0, 0, 1]])

                # Combined rotation matrix (order: Rz * Ry * Rx)
                R = Rz @ Ry @ Rx

                # Apply rotation to all points
                rotated_points = all_points @ R.T

                # Translate to final position
                final_points = rotated_points + np.array([x, y, z])

                # Extract rotated surface points
                surface_count = surface_points.shape[0]
                rotated_surface = final_points[:surface_count]
                rotated_x_cyl = rotated_surface[:, 0].reshape(x_cyl.shape)
                rotated_y_cyl = rotated_surface[:, 1].reshape(y_cyl.shape)
                rotated_z_cyl = rotated_surface[:, 2].reshape(z_mesh.shape)

                # Extract rotated circles
                circle_count = len(theta_circle)
                rotated_top = final_points[surface_count:surface_count+circle_count]
                rotated_bottom = final_points[surface_count+circle_count:surface_count+2*circle_count]

                # Draw half cylinder surface
                ax.plot_surface(rotated_x_cyl, rotated_y_cyl, rotated_z_cyl, alpha=alpha, color=color)

                # Draw top and bottom half circles
                top_poly = [rotated_top]
                bottom_poly = [rotated_bottom]

                ax.add_collection3d(Poly3DCollection(top_poly, alpha=alpha, facecolor=color, edgecolor='black'))
                ax.add_collection3d(Poly3DCollection(bottom_poly, alpha=alpha, facecolor=color, edgecolor='black'))

                # Draw flat surface
                flat_start_idx = surface_count + 2*circle_count
                rotated_flat = final_points[flat_start_idx:]
                if len(rotated_flat) > 0:
                    ax.scatter(rotated_flat[:, 0], rotated_flat[:, 1], rotated_flat[:, 2], alpha=alpha, color=color, s=1)
            else:
                print(f"Model type '{m.type}' not supported for rendering in Matplotlib.")
        plt.draw()
        plt.show()
        return "Rendered 3D model with Matplotlib."

if __name__ == "__main__":
    # Example usage
    cube = Model(
        name="TestCube",
        description="A test cube model",
        type="cube",
        coord_x=0.0,
        coord_y=0.0,
        coord_z=0.0,
        box_size=[1.0, 2.0, 4.0],
        orientation_pitch=0.0,
        orientation_yaw=0.0,
        orientation_roll=0.0,
        model_data=None
    )

    cylinder = Model(
        name="TestCylinder",
        description="A test cylinder model",
        type="cylinder",
        coord_x=1.0,
        coord_y=0.0,
        coord_z=0.0,
        box_size=[0.5, 0.5, 1.0],
        orientation_pitch=0.0,
        orientation_yaw=0.0,
        orientation_roll=0.0,
        model_data= {
            "radius_x": 0.5,
            "radius_y": 0.5,
            "height": 1.0
        }
    )

    half_cylinder = Model(
        name="TestHalfCylinder",
        description="A test half cylinder model",
        type="half cylinder",
        coord_x=2.0,
        coord_y=0.0,
        coord_z=0.0,
        box_size=[0.5, 0.5, 1.0],
        orientation_pitch=0.0,
        orientation_yaw=0.0,
        orientation_roll=0.0,
        model_data={
            "radius_x": 0.5,
            "radius_y": 0.5,
            "height": 1.0
        }
    )
    
    backend = BackendMatplot(name="MatplotlibBackend")
    backend.render([cube, cylinder, half_cylinder])