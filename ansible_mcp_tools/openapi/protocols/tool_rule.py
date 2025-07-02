from typing import Any

from typing import Protocol, runtime_checkable


@runtime_checkable
class ToolRule(Protocol):
    # if include_any is True, any tool that pass the check will be included,
    # this may be used in a whitelist rules
    include_any: bool = False

    def check(
        self, path: str, method: str, method_operation: dict[str:Any]
    ) -> bool: ...
