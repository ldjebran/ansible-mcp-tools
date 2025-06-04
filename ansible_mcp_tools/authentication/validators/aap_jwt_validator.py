import httpx

import jwt

import cachetools

from urllib.parse import urljoin

from .aap_base_validator import AAPBaseValidator

from mcp.server.fastmcp.utilities.logging import get_logger

from ansible_mcp_tools.authentication.auth_user import (
    AuthenticationUser,
    AuthenticationInfo,
)

from starlette.authentication import (
    AuthCredentials,
    AuthenticationError,
    BaseUser,
)

from starlette.requests import HTTPConnection

from ansible_mcp_tools.authentication.context import auth_context_var

logger = get_logger(__name__)


_cache = cachetools.TTLCache(maxsize=100, ttl=600)


class AAPJWTValidator(AAPBaseValidator):
    AUTHENTICATION_HEADER_NAME = "X-DAB-JW-TOKEN"

    async def _get_decryption_key(self) -> str:
        url = urljoin(self._authentication_server_url, "api/gateway/v1/jwt_key/")
        public_key = _cache.get(url)
        if public_key:
            return public_key
        logger.debug("calling authentication server at url: %s", url)
        async with httpx.AsyncClient(verify=self._verify_cert) as client:
            response = await client.get(url)
            if not response.is_success:
                raise AuthenticationError("failed to retrieve decryption key from AAP")
            public_key = response.text
            _cache[url] = public_key
            return public_key

    def decode_jwt_token(self, unencrypted_token, decryption_key):
        options = {"require": ["user_data", "exp"]}
        return jwt.decode(
            unencrypted_token,
            decryption_key,
            audience="ansible-services",
            options=options,
            issuer="ansible-issuer",
            algorithms=["RS256"],
        )

    async def validate(
        self, connection: HTTPConnection
    ) -> tuple[AuthCredentials, BaseUser] | None:
        authentication_header_value = connection.headers.get(
            self.AUTHENTICATION_HEADER_NAME, None
        )
        logger.debug(
            "header: %s >>>>> %s ",
            self.AUTHENTICATION_HEADER_NAME,
            authentication_header_value,
        )
        if authentication_header_value is None:
            return None
        try:
            decryption_key = await self._get_decryption_key()
        except Exception as exp:
            logger.error("failed to get the jwt public key: %s", exp)
            raise AuthenticationError("failed to get the jwt public key")

        try:
            jwt_token_data = self.decode_jwt_token(
                authentication_header_value, decryption_key
            )
        except Exception as exp:
            logger.error("failed to decode jwt token: %s", exp)
            raise AuthenticationError("failed to decode jwt token")

        username = jwt_token_data["user_data"]["username"]

        auth_user = AuthenticationUser(
            username,
            AuthenticationInfo(
                self.AUTHENTICATION_HEADER_NAME,
                authentication_header_value,
                self._authentication_server_url,
                verify_cert=self._verify_cert,
            ),
        )
        # set user to context var
        auth_context_var.set(auth_user)
        return AuthCredentials(), auth_user
