import json
import mcp.types as types

from abc import ABC
from typing import Dict, List, override

from ansible_mcp_tools.openapi.protocols.tool_parser import ToolParser
from ansible_mcp_tools.openapi.protocols.tool_name_strategy import ToolNameStrategy

from mcp.server.fastmcp.utilities.logging import get_logger

from ansible_mcp_tools import utils
from ansible_mcp_tools.openapi.common import (
    DEFAULT_VERSION_PARAM_NAME,
    get_spec_default_version,
    get_spec_path_with_version,
)
from ansible_mcp_tools.openapi.protocols.tool_rule import ToolRule
from ansible_mcp_tools.openapi.tool_rules import check_tool_rules

logger = get_logger(__name__)


class BaseToolParser(ToolParser, ABC):
    def __init__(
        self,
        spec: Dict,
        service_name: str,
        tool_name_strategy: ToolNameStrategy,
        tool_rules: List[ToolRule] | None = None,
    ):
        if tool_rules is None:
            tool_rules = []
        self._tool_rules = tool_rules
        self._spec = spec
        self._service_name = service_name
        self._tool_name_strategy = tool_name_strategy


class DefaultToolParser(BaseToolParser):
    def __init__(
        self,
        spec: Dict,
        service_name: str,
        tool_name_strategy: ToolNameStrategy,
        tool_rules: list[ToolRule] | None = None,
    ):
        super().__init__(spec, service_name, tool_name_strategy, tool_rules=tool_rules)

    @override
    def parse_tools(self) -> List[types.Tool]:
        """Register tools from OpenAPI spec, preserving across calls if already populated."""
        tools: List[types.Tool] = []
        logger.debug("Clearing previously registered tools to allow re-registration")
        tools.clear()
        tools_ignored = 0
        if not self._spec:
            logger.error("OpenAPI spec is None or empty.")
            return tools
        if "paths" not in self._spec:
            logger.error("No 'paths' key in OpenAPI spec.")
            return tools

        logger.debug(f"Spec paths available: {list(self._spec['paths'].keys())}")
        default_spec_version = get_spec_default_version(self._spec)

        paths = {path: item for path, item in self._spec["paths"].items()}
        logger.debug(f"Paths: {list(paths.keys())}")
        for path, path_item in paths.items():
            if not path_item:
                logger.debug(f"Empty path item for {path}")
                continue

            path, ignore_version_path_param = get_spec_path_with_version(
                path,
                default_spec_version,
                version_param_name=DEFAULT_VERSION_PARAM_NAME,
            )

            for method, operation in path_item.items():
                if not isinstance(operation, dict) or not check_tool_rules(
                    self._tool_rules, path, method, operation
                ):
                    logger.debug(
                        f"Skipping unsupported path operation item, path: {path}, method: {method}, operation: {operation}"
                    )
                    tools_ignored += 1
                    continue
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    logger.debug(f"Skipping unsupported method {method} for {path}")
                    tools_ignored += 1
                    continue
                try:
                    raw_name = f"{self._service_name}_{method.upper()} {path}"
                    operation_id = operation.get("operationId", "")
                    function_name = utils.get_tool_name_from_operation_id(
                        operation_id,
                        raw_name,
                        self._tool_name_strategy.normalize_tool_name,
                    )

                    tool_exists = False
                    for tool in tools:
                        if tool.name == function_name:
                            tool_exists = True
                            logger.warning(
                                f"Function: {function_name} already exists. Skipping."
                            )
                    if tool_exists:
                        continue

                    description = operation.get("summary", "")
                    if not description:
                        description = operation.get("description", "")
                        if description and "\n" in description:
                            # take a max of tree lines
                            description_lines = description.split("\n")
                            description = "\n".join(
                                description_lines[0 : min(3, len(description_lines))]
                            )
                            description = description.replace("\n", " ")
                        if not description:
                            description = operation_id or function_name

                    input_schema = {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False,
                    }
                    parameters = operation.get("parameters", [])
                    placeholder_params = [
                        part.strip("{}")
                        for part in path.split("/")
                        if "{" in part and "}" in part
                    ]
                    for param_name in placeholder_params:
                        param_name = (
                            self._tool_name_strategy.normalize_tool_parameter_name(
                                param_name
                            )
                        )
                        input_schema["properties"][param_name] = {
                            "type": "string",
                            "description": f"Path parameter {param_name}",
                        }
                        input_schema["required"].append(param_name)
                        logger.debug(
                            f"Added URI placeholder {param_name} to inputSchema for {function_name}"
                        )
                    for param in parameters:
                        param_name = param.get("name")
                        param_name = (
                            self._tool_name_strategy.normalize_tool_parameter_name(
                                param_name
                            )
                        )
                        param_in = param.get("in")
                        if param_in in ["path", "query"]:
                            if (
                                param_in == "path"
                                and param_name == DEFAULT_VERSION_PARAM_NAME
                                and ignore_version_path_param
                            ):
                                continue

                            param_type = param.get("schema", {}).get("type", "string")
                            schema_type = (
                                param_type
                                if param_type
                                in ["string", "integer", "boolean", "number"]
                                else "string"
                            )
                            input_schema["properties"][param_name] = {
                                "type": schema_type,
                                "description": param.get(
                                    "description", f"{param_in} parameter {param_name}"
                                ),
                            }
                            if (
                                param.get("required", False)
                                and param_name not in input_schema["required"]
                            ):
                                input_schema["required"].append(param_name)
                    tool = types.Tool(
                        name=function_name,
                        description=description,
                        inputSchema=input_schema,
                    )
                    tools.append(tool)
                    logger.debug(
                        f"Registered function: {function_name} ({method.upper()} {path}) with inputSchema: {json.dumps(input_schema)}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error registering function for {method.upper()} {path}: {e}",
                        exc_info=True,
                    )
        logger.debug(f"Registered {len(tools)} functions from OpenAPI spec.")
        logger.debug(f"Ignored {tools_ignored} functions from OpenAPI spec.")
        return tools
