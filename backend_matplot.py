from if_model import Model, ModelOperation
from if_backend import BackendIface
from typing import List, Dict, Any, Optional
# import random colors for 3d model rendeoing
import random
from matplotlib.colors import CSS4_COLORS as colors
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
                Render a cube model in 3D space.
                :param m: Model object containing cube data.
                """
                dx, dy, dz = m.box_size

                # Create a 3D cube
                r = [0, 1]
                X, Y = np.meshgrid(r, r)
                ax.plot_surface(X * dx + x, Y * dy + y, np.zeros_like(X) + z, alpha=alpha, color=color)
                ax.plot_surface(X * dx + x, Y * dy + y, np.ones_like(X) * (z + dz), alpha=alpha, color=color)
                ax.plot_surface(X * dx + x, np.zeros_like(X) + y, Y * dy + z, alpha=alpha, color=color)
                ax.plot_surface(X * dx + x, np.ones_like(X) * (y + dy), Y * dy + z, alpha=alpha, color=color)
                ax.plot_surface(np.zeros_like(X) + x, X * dx + y, Y * dy + z, alpha=alpha, color=color)
                ax.plot_surface(np.ones_like(X) * (x + dx), X * dx + y, Y * dy + z, alpha=alpha, color=color)
            else:
                print(f"Model type '{m.type}' not supported for rendering in Matplotlib.")
        plt.tight_layout()
        plt.axis('off')
        plt.grid(False)
        plt.gca().set_box_aspect([1,1,1])
        plt.tight_layout()
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
        box_size=[1.0, 1.0, 1.0],
        orientation_pitch=0.0,
        orientation_yaw=0.0,
        orientation_roll=0.0,
        model_data=None
    )
    
    backend = BackendMatplot(name="MatplotlibBackend")
    backend.render([cube])