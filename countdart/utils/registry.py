"""This module contains the Registry class.

The registry stores classes, whose objects can be built from dictionary-configs.
"""

from typing import Any, Dict, Generic, Type, TypeVar

T = TypeVar("T", bound=type)


class Registry(Generic[T]):
    """Registry class, which allows building classes from dictionary configurations.

    Classes can be registered using `@registry.register_class()`

    To build an instance of a class, pass a dictionary to `build`.
    The dictionary has to contain at least the key `"type"` which is used to
    infer the class which should be selected from the dictionary.

    By default, the given dictionary except the `"type"` are passed onto
    the `__init__` function of the class.

    Args:
         name: the name of the registry
    """

    def __init__(
        self,
        name: str,
    ):
        self.name = name
        self.registry: Dict[str, Type[T]] = {}

    def register_class(self, cls: Type[T]):
        """Registers a class to this registry.

        Args:
             cls: the class to register
        """
        self.registry[cls.__name__] = cls
        return cls

    def build(self, config: Dict[str, Any]) -> T:
        """Builds an instance of the class using the config.

        If the config is not a dict, returns the given object.
        This is done to prevent trying to rebuild objects.

        Args:
            config: the config to use to build the class in the registry

        Returns:
            the built object
        """
        if not isinstance(config, dict):
            return config
        class_name = config.pop("type")
        try:
            cls_to_build = self.registry[class_name]
        except KeyError as e:
            raise ValueError(f"No class named '{class_name}' in registry.") from e
        return cls_to_build(**config)

    def __getitem__(self, class_name: str) -> Type[T]:
        return self.registry[class_name]
