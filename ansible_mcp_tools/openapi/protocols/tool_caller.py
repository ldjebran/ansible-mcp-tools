import mcp.types as types

from typing import Dict, List

from typing import Protocol, runtime_checkable


@runtime_checkable
class ToolCaller(Protocol):
    async def tool_call(
        self, name: str, arguments: Dict
    ) -> List[types.TextContent]: ...
