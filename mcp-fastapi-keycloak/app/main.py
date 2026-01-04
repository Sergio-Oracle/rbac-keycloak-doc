from fastapi import FastAPI
from app.api_president import router as president_router

app = FastAPI(
    title="MCP FastAPI Keycloak",
    version="1.0.0",
    swagger_ui_init_oauth={
        "clientId": "swagger-client",
        "usePkceWithAuthorizationCodeGrant": True,
        "scopes": "openid profile",
        # ❌ AUCUN clientSecret
    }
)

app.include_router(president_router)
