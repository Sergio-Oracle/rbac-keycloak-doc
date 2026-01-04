from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from authlib.integrations.flask_client import OAuth
import requests
import jwt as pyjwt
import uuid
app = Flask(__name__)
app.secret_key = "super-secret-key-change-in-production"
# =========================
# CONFIG KEYCLOAK
# =========================
KEYCLOAK_URL = "http://localhost:8080"
REALM = "mcp-rtn"
CLIENT_ID = "web-client"
CLIENT_SECRET = "QtchSzGOH8hS8KjujbCLLbTmO5J6WQST"
# =========================
# MCP CONFIG
# =========================
MCP_SERVER_URL = "http://127.0.0.1:3333/mcp"
MCP_PROTOCOL_VERSION = "2024-11-05"
# =========================
# OAUTH
# =========================
oauth = OAuth(app)
keycloak = oauth.register(
    name="keycloak",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url=f"{KEYCLOAK_URL}/realms/{REALM}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"},
)
# =========================
# MCP HEADERS (CRITIQUE)
# =========================
def get_mcp_headers(session_id: str):
    return {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "X-Session-ID": session_id # ⭐ SEULE SOURCE DE VÉRITÉ
    }
# =========================
# MCP SESSION
# =========================
def ensure_mcp_session():
    if "mcp_session_id" not in session:
        session["mcp_session_id"] = str(uuid.uuid4())
        init_mcp_session()
    return session["mcp_session_id"]
def init_mcp_session():
    session_id = session["mcp_session_id"]
    payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {
                "name": "mcp-web-interface",
                "version": "1.0.0"
            }
        }
    }
    r = requests.post(
        MCP_SERVER_URL,
        headers=get_mcp_headers(session_id),
        json=payload,
        timeout=10
    )
    return r.status_code == 200
# =========================
# ROUTES WEB
# =========================
@app.route("/")
def index():
    if "token" in session:
        ensure_mcp_session()
        return render_template(
            "dashboard.html",
            username=session.get("username"),
            roles=session.get("roles", [])
        )
    return render_template("login.html")
@app.route("/login")
def login():
    redirect_uri = url_for("authorize", _external=True, _scheme="http")
    redirect_uri = redirect_uri.replace("127.0.0.1", "localhost")
    return keycloak.authorize_redirect(redirect_uri)
@app.route("/authorize")
def authorize():
    try:
        token = keycloak.authorize_access_token()
        userinfo = token.get("userinfo", {})
        session["token"] = token["access_token"]
        session["refresh_token"] = token.get("refresh_token")
        session["username"] = userinfo.get("preferred_username")
        session["email"] = userinfo.get("email")
        decoded = pyjwt.decode(
            token["access_token"],
            options={"verify_signature": False}
        )
        session["roles"] = decoded.get("realm_access", {}).get("roles", [])
        session["mcp_session_id"] = str(uuid.uuid4())
        init_mcp_session()
        return redirect(url_for("index"))
    except Exception as e:
        return f"Erreur auth: {e}", 401
@app.route("/logout")
def logout():
    session.clear()
    redirect_uri = url_for("index", _external=True, _scheme="http")
    redirect_uri = redirect_uri.replace("127.0.0.1", "localhost")
    logout_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/logout"
    return redirect(f"{logout_url}?redirect_uri={redirect_uri}")
# =========================
# API MCP
# =========================
@app.route("/api/tools")
def list_tools():
    if "token" not in session:
        return jsonify({"error": "Non authentifié"}), 401
    session_id = ensure_mcp_session()
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    r = requests.post(
        MCP_SERVER_URL,
        headers=get_mcp_headers(session_id),
        json=payload,
        timeout=30
    )
    return jsonify(r.json())
@app.route("/api/call_tool", methods=["POST"])
def call_tool():
    if "token" not in session:
        return jsonify({"error": "Non authentifié"}), 401
    data = request.json or {}
    tool_name = data.get("tool_name")
    tool_args = data.get("arguments", {})
    tool_args["token"] = session["token"]
    session_id = ensure_mcp_session()
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": tool_args
        }
    }
    r = requests.post(
        MCP_SERVER_URL,
        headers=get_mcp_headers(session_id),
        json=payload,
        timeout=30
    )
    return jsonify(r.json())
# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
