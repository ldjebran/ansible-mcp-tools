from typing import Any

from ansible_mcp_tools.openapi.protocols.tool_rule import ToolRule


class MethodRule(ToolRule):
    def __init__(
        self,
        black_list_methods: list[str],
    ):
        if not isinstance(black_list_methods, list):
            black_list_methods = []

        self._black_list_methods = list(
            map(lambda item: item.lower(), black_list_methods)
        )

    def check(self, path: str, method: str, method_operation: dict[str:Any]) -> bool:
        if method.lower() in self._black_list_methods:
            return False
        return True


class OperationIdWhiteRule(ToolRule):
    include_any = True

    def __init__(self, white_list_operations: list[str]):
        self._white_list_operations = white_list_operations

    def check(self, path: str, method: str, method_operation: dict[str:Any]) -> bool:
        operation_id = method_operation.get("operationId", "")
        if operation_id in self._white_list_operations:
            return True
        return False


class OperationIdBlackRule(ToolRule):
    def __init__(self, black_list: list[str]):
        self._black_list = black_list

    def check(self, path: str, method: str, method_operation: dict[str:Any]) -> bool:
        operation_id = method_operation.get("operationId", "")
        if operation_id in self._black_list:
            return False
        return True


class PathRule(ToolRule):
    def __init__(self, black_list_paths: list[str]):
        self._black_list_paths = black_list_paths

    def check(self, path: str, method: str, method_operation: dict[str:Any]) -> bool:
        if path in self._black_list_paths:
            return False
        return True


class NoDescriptionRule(ToolRule):
    def check(self, path: str, method: str, method_operation: dict[str:Any]) -> bool:
        if not method_operation.get("description", "") and not method_operation.get(
            "summary", ""
        ):
            return False
        return True


def check_tool_rules(
    tool_rules: list[ToolRule], path: str, method: str, method_operation: dict[str:Any]
) -> bool:
    valid = True
    for tool_rule in tool_rules:
        check = tool_rule.check(path, method, method_operation)
        if tool_rule.include_any:
            if check:
                valid = True
                break
        else:
            if not check:
                valid = False
                # do not break to check all the rules,
                # because maybe a white rule with include_any True is ahead of the list

    return valid
