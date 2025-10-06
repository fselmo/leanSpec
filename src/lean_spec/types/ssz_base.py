"""Base classes and interfaces for all SSZ types."""

from __future__ import annotations

import io
from abc import ABC, abstractmethod
from typing import IO, Any, TypeVar

from pydantic import GetCoreSchemaHandler, RootModel
from pydantic_core import core_schema
from typing_extensions import Iterator, Self

from .base import StrictBaseModel


class SSZType(ABC):
    """
    Abstract base class for all SSZ types.

    This is the minimal interface that all SSZ types must implement.
    Use SSZModel for Pydantic-based SSZ types.
    """

    @classmethod
    @abstractmethod
    def is_fixed_size(cls) -> bool:
        """
        Check if the type has a fixed size in bytes.

        Returns:
            bool: True if the size is fixed, False otherwise.
        """
        ...

    @classmethod
    @abstractmethod
    def get_byte_length(cls) -> int:
        """
        Get the byte length of the type if it is fixed-size.

        Raises:
            TypeError: If the type is not fixed-size.

        Returns:
            int: The number of bytes.
        """
        ...

    @abstractmethod
    def serialize(self, stream: IO[bytes]) -> int:
        """
        Serializes the object and writes it to a binary stream.

        Args:
            stream (IO[bytes]): The stream to write the serialized data to.

        Returns:
            int: The number of bytes written.
        """
        ...

    @classmethod
    @abstractmethod
    def deserialize(cls, stream: IO[bytes], scope: int) -> Self:
        """
        Deserializes an object from a binary stream within a given scope.

        Args:
            stream (IO[bytes]): The stream to read from.
            scope (int): The number of bytes available to read for this object.

        Returns:
            Self: An instance of the class.
        """
        ...

    def encode_bytes(self) -> bytes:
        """
        Serializes the SSZ object to a byte string.

        Returns:
            bytes: The serialized byte string.
        """
        with io.BytesIO() as stream:
            self.serialize(stream)
            return stream.getvalue()

    @classmethod
    def decode_bytes(cls, data: bytes) -> Self:
        """
        Deserializes a byte string into an SSZ object.

        Args:
            data (bytes): The byte string to deserialize.

        Returns:
            Self: An instance of the class.
        """
        with io.BytesIO(data) as stream:
            return cls.deserialize(stream, len(data))

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        Provide Pydantic core schema for SSZType instances.

        This tells Pydantic to accept any instance of SSZType without trying to
        decompose or validate the internal structure.
        """
        return core_schema.is_instance_schema(cls)


T = TypeVar("T")


class SSZRootModel(RootModel[T], SSZType):
    """
    Base class for SSZ collection types that wrap a single root value.

    This class is for homogeneous collections like lists, vectors, and bitfields
    that fundamentally contain a single data structure (tuple, list, etc).

    Provides natural collection APIs by delegating to the root value:
    - `for item in collection` iterates over root contents
    - `collection[i]` accesses root by index
    - `len(collection)` returns root length

    Use SSZModel for container types with named fields.
    """

    root: Any

    def __len__(self) -> int:
        """Return the length of the root collection."""
        return len(self.root)

    def __iter__(self) -> Iterator[Any]:  # type: ignore[override]
        """Iterate over the root collection's items."""
        return iter(self.root)

    def __getitem__(self, key: Any) -> Any:
        """Get an item from the root collection."""
        return self.root[key]

    def __repr__(self) -> str:
        """String representation showing the class name and root data."""
        # For tuples/lists, show the contents directly
        if isinstance(self.root, (tuple, list)):
            return f"{self.__class__.__name__}(data={list(self.root)!r})"
        # For other types, show the root value
        return f"{self.__class__.__name__}(root={self.root!r})"


class SSZModel(StrictBaseModel, SSZType):
    """
    Base class for SSZ container types with named fields.

    This combines StrictBaseModel (Pydantic validation + immutability) with SSZ serialization.
    Use this for containers with heterogeneous named fields.

    For collection types (lists, vectors, bitfields), use SSZRootModel.
    For simple types that need special inheritance (like int), use SSZType directly.

    SSZModel provides field-based access patterns:
    - `len(container)` returns the number of fields
    - `for name, value in container` iterates over (field_name, field_value) pairs
    - `container["field_name"]` accesses fields by name
    """

    def __len__(self) -> int:
        """Return the number of fields in this container."""
        return len(self.__pydantic_fields__)

    def __iter__(self) -> Iterator[Any]:  # type: ignore[override]
        """Iterate over (field_name, field_value) pairs."""
        return iter((name, getattr(self, name)) for name in self.__pydantic_fields__.keys())

    def __getitem__(self, key: Any) -> Any:
        """Get a field value by name."""
        if isinstance(key, str) and key in self.model_fields:
            return getattr(self, key)
        raise KeyError(f"Field '{key}' not found in {self.__class__.__name__}")

    def __repr__(self) -> str:
        """String representation showing field names and values."""
        field_strs = [f"{name}={getattr(self, name)!r}" for name in self.__pydantic_fields__.keys()]
        return f"{self.__class__.__name__}({' '.join(field_strs)})"
