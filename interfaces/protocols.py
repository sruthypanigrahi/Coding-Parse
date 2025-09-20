"""Protocol interfaces for duck typing"""
from typing import Protocol, Any, Optional, Union


class Readable(Protocol):
    """Protocol for readable objects"""
    def read(self) -> str:
        """Read and return string content"""
        ...


class Writable(Protocol):
    """Protocol for writable objects"""
    def write(self, data: Union[str, bytes]) -> Optional[int]:
        """Write data and optionally return bytes written"""
        ...