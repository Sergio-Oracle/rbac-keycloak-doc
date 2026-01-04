from fastmcp import FastMCP
from app.auth import verify_token
from app.database import SessionLocal
from app.crud import get_all, create
from app.models import President

mcp = FastMCP(
    name="president-mcp",
    version="1.0.0",
    instructions="MCP Server for President CRUD with Keycloak RBAC"
)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

@mcp.tool()
def list_presidents(token: str):
    """List all presidents (reader or admin)"""
    user = verify_token(token)
    if not {"reader", "admin"}.intersection(user["roles"]):
        raise Exception("Forbidden: reader role required")
    
    db = get_db()
    presidents = get_all(db)
    return [{"code": p.code, "prenom": p.prenom, "nom": p.nom, "solde": p.solde} for p in presidents]

@mcp.tool()
def create_president(token: str, code: int, prenom: str, nom: str, solde: float):
    """Create a president (admin only)"""
    user = verify_token(token)
    if "admin" not in user["roles"]:
        raise Exception("Forbidden: admin role required")
    
    db = get_db()
    pres = President(code=code, prenom=prenom, nom=nom, solde=solde)
    pres = create(db, pres)
    return {"code": pres.code, "prenom": pres.prenom, "nom": pres.nom, "solde": pres.solde}
