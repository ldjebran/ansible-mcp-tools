from typing import Callable
from ansible_mcp_tools import registry

AAP_JWT_HEADER_NAME = "X-DAB-JW-TOKEN"


def get_aap_service_url_base_path_by_header_name(
    service_name: str, auth_header_name: str
) -> str | None:
    if auth_header_name != AAP_JWT_HEADER_NAME:
        return registry.get_aap_service_url_base_path(service_name, context="gateway")
    return registry.get_aap_service_url_base_path(service_name)


def get_aap_service_url_path(
    service_name: str, auth_header_name: str, path: str
) -> str | None:
    base_url_path = get_aap_service_url_base_path_by_header_name(
        service_name, auth_header_name
    )
    if base_url_path is None:
        return None
    for text in ("api/", "/api/"):
        if path.startswith(text):
            path = path[len(text) :]
            break

    if path.startswith("/"):
        path = path[1:]

    return f"{base_url_path}/{path}"


def get_tool_name_from_operation_id(
    operation_id: str, raw_name: str, normalization_function: Callable[[str], str]
) -> str:
    if 0 < len(operation_id) <= 64:
        return operation_id
    return normalization_function(raw_name)
