from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt
import requests

KEYCLOAK_URL = "http://localhost:8080"
REALM = "mcp-rtn"
CLIENT_ID = "swagger-client"

OIDC_CONFIG = f"{KEYCLOAK_URL}/realms/{REALM}/.well-known/openid-configuration"
oidc = requests.get(OIDC_CONFIG).json()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=oidc["authorization_endpoint"],
    tokenUrl=oidc["token_endpoint"],
    scopes={
        "openid": "OpenID",
        "profile": "Profile"
    }
)

jwks = requests.get(oidc["jwks_uri"]).json()


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            issuer=f"{KEYCLOAK_URL}/realms/{REALM}",
            options={"verify_aud": False}
        )

        roles = payload.get("realm_access", {}).get("roles", [])

        return {
            "sub": payload.get("sub"),
            "username": payload.get("preferred_username"),
            "roles": roles,
            "raw": payload
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
def require_admin(user=Depends(verify_token)):
    if "admin" not in user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return user


def require_reader(user=Depends(verify_token)):
    if not {"reader", "admin"}.intersection(user["roles"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reader role required"
        )
    return user
