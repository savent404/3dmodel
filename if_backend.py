from typing import List
from if_model import Model, ModelOperation

class BackendIface:
    """
    Interface for backend operations.
    This interface defines the methods that any backend implementation should provide.
    """

    def __init__(self, name: str):
        """
        Initialize the backend with a name.
        :param name: Name of the backend.
        """
        self.name = name
    
    def transform(self, model: List[Model], operation: ModelOperation) -> List[Model]:
        """
        Transform the given model using the specified operation.
        :param model: List of models to be transformed.
        :param operation: The operation to apply to the models.
        :return: List of transformed models.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def render(self, model: List[Model]) -> str:
        """
        Render the given model to a string representation.
        :param model: List of models to be rendered.
        :return: String representation of the rendered model.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")