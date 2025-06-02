from os import environ

from ansible_mcp_tools.registry import register_service_url, register_sample_tools
from ansible_mcp_tools.registry import init as init_registry
from ansible_mcp_tools.server import LightspeedBaseAAPServer

from ansible_mcp_tools.authentication import LightspeedAuthenticationBackend
from ansible_mcp_tools.authentication.validators.aap_token_validator import (
    AAPTokenValidator,
)
from ansible_mcp_tools.authentication.validators.aap_jwt_validator import (
    AAPJWTValidator,
)

from mcp.server.fastmcp.utilities.logging import configure_logging


configure_logging("DEBUG")

init_registry()

AAP_URL = environ.get("AAP_URL", "https://localhost")
register_service_url("gateway", AAP_URL)
register_service_url("controller", "https://localhost:8043")
register_service_url("lightspeed", "http://localhost:7080")


mcp = LightspeedBaseAAPServer(
    auth_backend=LightspeedAuthenticationBackend(
        authentication_validators=[
            AAPJWTValidator(AAP_URL, verify_cert=False),
            AAPTokenValidator(AAP_URL, verify_cert=False),
        ]
    ),
    host="127.0.0.1",
    port=3180,
)


register_sample_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="sse")
