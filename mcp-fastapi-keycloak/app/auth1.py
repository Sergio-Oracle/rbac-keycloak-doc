from fastapi import Depends

def verify_token():
    # MODE DEV (pas de Keycloak)
    return {"user": "dev"}
