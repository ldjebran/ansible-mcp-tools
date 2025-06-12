import mcp.types as types

from typing import List
from typing import Protocol, runtime_checkable


@runtime_checkable
class ToolParser(Protocol):
    def parse_tools(self) -> List[types.Tool]: ...
