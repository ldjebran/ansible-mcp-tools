import re

import shortuuid

from ansible_mcp_tools.openapi.protocols.tool_name_strategy import ToolNameStrategy

from mcp.server.fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)


class DefaultToolNameStrategy(ToolNameStrategy):

    def normalize_tool_name(self, raw_name: str) -> str:
        """Convert an HTTP method and path into a normalized tool name."""
        try:
            method, path = raw_name.split(" ", 1)
            method = method.lower()

            path_name = ""
            path_parts = path.split("/")
            for path_part in path_parts:
                pp = path_part
                if pp:
                    if pp.startswith("{"):
                        pp = pp[1:]
                    if pp.endswith("}"):
                        pp = pp[:-1]
                    path_name = path_name + "_" + pp if path_name else pp

            if not path_parts:
                return "unknown_tool"

            name = f"{method}_{path_name}"
            name = self._anthropic_limitations(name)

            return shortuuid.uuid(name)

        except ValueError:
            logger.debug(f"Failed to normalize tool name: {raw_name}")
            return "unknown_tool"

    def normalize_tool_parameter_name(self, raw_name: str) -> str:
        return self._anthropic_limitations(raw_name)

    def _anthropic_limitations(self, raw_name: str) -> str:
        raw_name.replace(" ", "_")
        raw_name = raw_name.replace("{", "")
        raw_name = raw_name.replace("}", "")
        raw_name = raw_name.replace(",", "_")
        raw_name = raw_name[:63]

        # This is a nasty assertion to check the correctness raw_name
        # It is useful for debugging.. but could probably be removed.
        pattern = r"^[a-zA-Z0-9_-]{1,64}$"  # Raw string for regex pattern
        match = re.search(pattern, raw_name)
        if not match:
            raise RuntimeWarning(f"Conversion of {raw_name} did not pass checks.")
        return raw_name
