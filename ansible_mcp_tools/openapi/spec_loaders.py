import json
import httpx
import yaml

from typing import override
from abc import ABC

from ansible_mcp_tools.openapi.protocols.spec_loader import SpecLoader

from mcp.server.fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)


class BaseLoader(SpecLoader, ABC):

    def __init__(self, url: str):
        self._url = url

    @override
    def load(self):
        content = self.fetch()
        try:
            spec = json.loads(content)
            logger.debug("Content parsed as JSON.")
        except json.JSONDecodeError:
            try:
                spec = yaml.safe_load(content)
                logger.debug("Content parsed as YAML.")
            except yaml.YAMLError as ye:
                raise RuntimeError(
                    f"YAML parsing failed: {ye}. Raw content: {content[:500]}..."
                )

        return spec


class FileLoader(BaseLoader):

    def __init__(self, url: str):
        if not url.lower().startswith("file://"):
            raise RuntimeError(f"URL should begin with 'file://'.")
        super().__init__(url)

    @override
    def fetch(self) -> str:
        logger.debug(f"Fetching OpenAPI spec from file: {self._url}")
        try:
            with open(self._url[7:], "r") as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to fetch spec from {self._url}, {e}.")


class UrlLoader(BaseLoader):

    retries: int = 3

    @override
    def fetch(self) -> str:
        logger.debug(f"Fetching OpenAPI spec from URL: {self._url}")
        attempt = 0
        while attempt < self.retries:
            try:
                # This is purposefully synchronous
                with httpx.Client(verify=False) as client:
                    response = client.get(self._url)
                    response.raise_for_status()
                    return response.text

            except Exception as e:
                attempt += 1
                logger.warning(f"Fetch attempt {attempt}/{self.retries} failed: {e}")

        raise RuntimeError(
            f"Failed to fetch spec from {self._url} after {self} attempts."
        )
