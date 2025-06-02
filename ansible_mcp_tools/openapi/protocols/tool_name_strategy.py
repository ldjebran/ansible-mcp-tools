from typing import Protocol, runtime_checkable


@runtime_checkable
class ToolNameStrategy(Protocol):

    def normalize_tool_name(self, raw_name: str) -> str: ...

    def normalize_tool_parameter_name(self, raw_name: str) -> str: ...
