import re
from typing import Any

DEFAULT_VERSION_MATCH: str = "^v[1-9]+"

DEFAULT_VERSION_PARAM_NAME: str = "version"


def get_spec_default_version(spec: dict[str, Any]) -> str | None:
    version: str | None = None
    info_version: str | None = spec.get("info", {}).get("version", None)
    if info_version and re.match(DEFAULT_VERSION_MATCH, info_version):
        version = info_version
    return version


def get_spec_path_with_version(
    path: str, version: str, version_param_name=DEFAULT_VERSION_PARAM_NAME
) -> (str, bool):
    ignore_version_path_param = False
    version_in_path_string = "{" + version_param_name + "}"
    if version and version_in_path_string in path:
        path = path.replace(version_in_path_string, version)
        ignore_version_path_param = True
    return path, ignore_version_path_param
