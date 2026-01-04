from fastapi import FastAPI
from app.api_president import router

app = FastAPI(
    title="President API",
    description="API CRUD MySQL avec OAuth2.1 / Keycloak",
    version="1.0.0"
)

app.include_router(router)
